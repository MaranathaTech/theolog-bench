"""Automated scoring for theolog-bench responses.

Provides three scoring methods:
- semantic_similarity: word/phrase overlap for catechism recall
- position_detection: affirm/deny pattern matching for doctrinal questions
- reference_check: Bible citation extraction and validation
"""

import re
import string


# ---------------------------------------------------------------------------
# Think block stripping
# ---------------------------------------------------------------------------

_THINK_RE = re.compile(r'<think>.*?</think>', re.DOTALL)


def strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> reasoning traces from model output.

    Chain-of-thought models (DeepSeek R1, Qwen3 in thinking mode, etc.) wrap
    internal reasoning in <think> tags. The scorer should evaluate only the
    final answer, not the reasoning process.
    """
    stripped = _THINK_RE.sub('', text).strip()
    return stripped if stripped else text  # fallback to original if nothing left


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

def score_response(question: dict, response: str) -> dict:
    """Route to the appropriate scoring method based on question config.

    Returns dict with keys: score (int 0-100), method (str), details (dict).
    """
    response = strip_think_blocks(response)
    method = question["scoring"]["method"]
    if method == "semantic_similarity":
        return score_semantic_similarity(question, response)
    elif method == "position_detection":
        return score_position_detection(question, response)
    elif method == "reference_check":
        return score_reference_check(question, response)
    elif method == "llm_judge":
        return {
            "score": 0,
            "method": "llm_judge",
            "details": {"note": "Judge scoring deferred — requires API call, run via lib.judge"},
        }
    else:
        return {
            "score": 0,
            "method": method,
            "details": {"error": f"Unknown scoring method: {method}"},
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, and normalize common variants."""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    # Normalize common spelling variants
    text = re.sub(r'\bfor ever\b', 'forever', text)
    text = re.sub(r'\bfor\s+ever\b', 'forever', text)
    # Strip markdown formatting artifacts
    text = re.sub(r'\*+', '', text)
    return text


def _words(text: str) -> list[str]:
    return _normalize(text).split()


def _phrase_present(phrase: str, response: str, window: int = 5) -> bool:
    """Check if all words of *phrase* appear within a sliding window in *response*.

    This allows minor reordering / inserted filler words while still requiring
    proximity.
    """
    phrase_words = _words(phrase)
    if not phrase_words:
        return True
    resp_words = _words(response)
    if len(resp_words) < len(phrase_words):
        return False
    # Slide a window of (len(phrase_words) + window) over response words
    win_size = len(phrase_words) + window
    for start in range(len(resp_words) - len(phrase_words) + 1):
        segment = resp_words[start : start + win_size]
        if all(w in segment for w in phrase_words):
            return True
    return False


# ---------------------------------------------------------------------------
# 1. Semantic similarity (catechism_recall)
# ---------------------------------------------------------------------------

def _word_overlap_score(reference: str, response: str) -> float:
    """Compute word overlap between reference answer and response.

    Returns a 0.0-1.0 ratio of reference words found in the response.
    Filters out common stop words to focus on content words.
    """
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "must", "can", "could", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "and", "but", "or", "nor", "not", "so",
        "yet", "both", "either", "neither", "each", "every", "all", "any",
        "few", "more", "most", "other", "some", "such", "no", "only", "own",
        "same", "than", "too", "very", "just", "because", "if", "when",
        "where", "how", "what", "which", "who", "whom", "this", "that",
        "these", "those", "it", "its", "he", "his", "him", "she", "her",
        "they", "them", "their", "we", "us", "our", "you", "your",
    }
    ref_words = set(_words(reference)) - stop_words
    resp_words = set(_words(response)) - stop_words
    if not ref_words:
        return 0.0
    return len(ref_words & resp_words) / len(ref_words)


def score_semantic_similarity(question: dict, response: str) -> dict:
    scoring = question["scoring"]
    required_phrases = scoring.get("required_phrases", [])
    key_concepts = scoring.get("key_concepts", [])

    phrases_found = []
    phrases_missing = []
    for phrase in required_phrases:
        if _phrase_present(phrase, response):
            phrases_found.append(phrase)
        else:
            phrases_missing.append(phrase)

    # Use flexible concept matching (not exact phrase matching) for key_concepts
    concepts_found = []
    concepts_missing = []
    for concept in key_concepts:
        if _concept_present(concept, response):
            concepts_found.append(concept)
        else:
            concepts_missing.append(concept)

    # Score calculation: phrase/concept match score
    has_phrases = len(required_phrases) > 0
    has_concepts = len(key_concepts) > 0

    if has_phrases and has_concepts:
        phrase_score = (len(phrases_found) / len(required_phrases)) * 60
        concept_score = (len(concepts_found) / len(key_concepts)) * 40
        match_score = phrase_score + concept_score
    elif has_phrases:
        match_score = (len(phrases_found) / len(required_phrases)) * 100
    elif has_concepts:
        match_score = (len(concepts_found) / len(key_concepts)) * 100
    else:
        match_score = 0.0

    # Word overlap score against the reference answer — gives partial credit
    # for paraphrases that use similar vocabulary without hitting exact phrases
    ref_answer = question.get("reference_answer", "")
    overlap = _word_overlap_score(ref_answer, response) if ref_answer else 0.0

    # Final score: use the higher of match score or overlap-based score,
    # but cap the overlap-only score at 60 (must hit phrases for full marks)
    overlap_score = min(60, overlap * 100)
    score = max(match_score, overlap_score)

    # If neither phrases/concepts are defined, use pure overlap
    if not has_phrases and not has_concepts:
        score = overlap * 100

    score = max(0, min(100, int(round(score))))

    return {
        "score": score,
        "method": "semantic_similarity",
        "details": {
            "phrases_found": phrases_found,
            "phrases_missing": phrases_missing,
            "concepts_found": concepts_found,
            "concepts_missing": concepts_missing,
            "word_overlap": round(overlap, 3),
        },
    }


# ---------------------------------------------------------------------------
# 2. Position detection (doctrinal_position, error_detection)
# ---------------------------------------------------------------------------

AFFIRM_PATTERNS = [
    # Direct affirmation
    r'(?:^|\n)\s*\*{0,2}yes\*{0,2}\b',  # "Yes" / "**yes**" at start of line/response
    r'\bthe answer is yes\b',
    r'\bthis is true\b',
    r'\bthis is correct\b',
    # Theological affirmation
    r'\bscripture teaches\b',
    r'\bthe bible teaches\b',
    r'\breformed theology affirms\b',
    r'\breformed view affirms\b',
    r'\breformed theology teaches that\b',
    r'\breformed position affirms\b',
    r'\bwe affirm\b',
    r'\bindeed\b',
    r'\babsolutely\b',
    # Content-based affirmation (model explains the doctrine positively)
    r'\bthe fall\b.{0,40}\bevery (part|aspect|faculty|dimension)\b',
    r'\btotal depravity\b.{0,60}\b(teaches|means|refers|affirms)\b',
    r'\bprofoundly affects every\b',
    r'\bcorrupt(s|ed|ing)\b.{0,30}\bentire\b',
]

# Affirm patterns that are explanatory — used by models to explain Reformed
# teaching as part of a rejection (e.g., "Reformed theology affirms that all
# are conceived in sin" while rejecting the Immaculate Conception). These
# should NOT count as affirm signals when the expected position is deny/reject.
EXPLANATORY_AFFIRM_PATTERNS = [
    r'\breformed theology affirms\b',
    r'\breformed view affirms\b',
    r'\breformed theology teaches that\b',
    r'\breformed position affirms\b',
    r'\bscripture teaches\b',
    r'\bthe bible teaches\b',
]

# Patterns that indicate direct denial/rejection of a claim
DENY_PATTERNS = [
    # Direct denial
    r'(?:^|\n)\s*\*{0,2}no\*{0,2}\b',  # "No" / "**no**" at start of line/response
    r'\bthe answer is no\b',
    r'\ba qualified\s+\*{0,2}no\*{0,2}\b',  # "a qualified **no**"
    # Theological rejection
    r'\bthis is (incorrect|false|wrong|inaccurate)\b',
    r'\bthis statement is\s+\*{0,2}(incorrect|false|wrong|inaccurate)\b',
    r'\bscripture does not teach\b',
    r'\bthe bible does not teach\b',
    r'\breformed theology (rejects|denies)\b',
    r'\breformed view (rejects|denies)\b',
    r'\breformed .{0,30}(rejects?|denies?|opposes?)\b',
    r'\bwe (reject|deny)\b',
    r'\bmust (reject|deny)\b',
    r'\bthis is (heresy|heretical|heterodox|unbiblical)\b',
    r'\bcontrary to (scripture|the bible|reformed|core)\b',
    # Strong rejection language used by LLMs
    r'\bfundamentally (incompatible|at odds|opposed|contrary|wrong)\b',
    r'\b(incompatible|inconsistent) with\b.{0,40}\b(reformed|scripture|biblical|doctrine)\b',
    r'\b(represents?|reflects?)\s+(a\s+)?(misunderstanding|misrepresentation|error|heresy)\b',
    r'\bwould reject\b',
    r'\brejects? (this|the)\b',
    r'\bat odds with\b.{0,30}\breformed\b',
    r'\binaccurate and contrary\b',
    # Statement-level rejection (model quotes then rejects)
    r'\bis\s+(rejected|false|incorrect|wrong)\b',
    r'\bis\s+\w+\s+rejected\b',  # "is fundamentally rejected", "is unequivocally rejected"
    r'\brejected\s+(as|in its)\b',  # "rejected as unbiblical", "rejected in its entirety"
    r'\bfirmly (denies|rejects|opposes)\b',
]

# Content patterns that describe inability/depravity — these indicate the model is
# TEACHING Reformed doctrine about human inability. Only used when the expected position
# is "deny" (e.g., "Can man choose God?" -> deny -> these patterns support the denial).
# NOT used for "affirm" questions where these concepts are supporting evidence.
INABILITY_PATTERNS = [
    r'\b(cannot|can\s*not|unable|impossible)\b.{0,30}\b(choose god|save|merit|earn)\b',
    r'\b(cannot|can\s*not|unable)\b.{0,30}\b(of (his|their|its) own)\b',
    r'\bnot able to\b.{0,20}\b(choose|seek|come to) god\b',
    r'\benslaved to sin\b',
    r'\bspiritual(ly)? dead\b',
    r'\bdead in\b.{0,10}\b(sin|trespasses)\b',
    r'\btotal (depravity|inability)\b',
    r'\bbondage (of|to) (sin|the will)\b',
]


def _concept_present(concept: str, response: str) -> bool:
    """Check if a concept is present in the response using flexible matching.

    More lenient than _phrase_present — checks if the key content words of the
    concept appear anywhere in the response, not just in a sliding window.
    """
    concept_words = _words(concept)
    if not concept_words:
        return True
    resp_words_set = set(_words(response))
    # Require at least 60% of concept words to be present anywhere in response
    matches = sum(1 for w in concept_words if w in resp_words_set)
    threshold = max(1, len(concept_words) * 0.6)
    return matches >= threshold


def _heterodox_flag_endorsed(flag: str, response: str) -> bool:
    """Check if a heterodox flag is endorsed (not merely mentioned to refute).

    A model that says 'The Arminian view of foreseen faith is incorrect' mentions
    the flag but doesn't endorse it. We check if the flag appears in a context
    that suggests agreement rather than refutation.
    """
    resp_lower = response.lower()
    flag_lower = flag.lower()

    # Find where the flag appears
    idx = resp_lower.find(flag_lower)
    if idx == -1:
        # Try flexible matching
        if not _phrase_present(flag, response):
            return False
        # Flag is loosely present — check surrounding context
        idx = 0  # fallback: check full response
        for i in range(len(resp_lower) - len(flag_lower)):
            if _phrase_present(flag, resp_lower[i:i+len(flag_lower)+50]):
                idx = i
                break

    # Look at surrounding context (100 chars before and after the flag)
    context_start = max(0, idx - 150)
    context_end = min(len(resp_lower), idx + len(flag_lower) + 150)
    context = resp_lower[context_start:context_end]

    # If the context contains refutation language, the flag is being refuted, not endorsed
    refutation_signals = [
        'incorrect', 'false', 'wrong', 'reject', 'denied', 'denies',
        'incompatible', 'contrary', 'error', 'heretical', 'heterodox',
        'misunderstanding', 'misrepresentation', 'not teach', 'not the case',
        'rather than', 'instead', 'in contrast', 'opposes', 'opposed',
        'fundamentally', 'at odds', 'unbiblical', 'not what',
    ]
    for signal in refutation_signals:
        if signal in context:
            return False  # Flag is mentioned in a refuting context

    return True  # Flag appears to be endorsed


def score_position_detection(question: dict, response: str) -> dict:
    scoring = question["scoring"]
    # Handle both field names used in benchmark.json
    expected = scoring.get("expected_position") or scoring.get("position", "")
    expected = expected.lower().strip()

    # Strip markdown formatting for pattern matching
    resp_clean = re.sub(r'\*+', '', response)
    resp_lower = resp_clean.lower()

    affirm_matches = []
    for pat in AFFIRM_PATTERNS:
        if re.search(pat, resp_lower, re.MULTILINE | re.DOTALL):
            # When expected is deny/reject, skip explanatory affirm patterns
            # (e.g., "Reformed theology affirms X" used to explain a rejection)
            if expected in ("deny", "reject") and pat in EXPLANATORY_AFFIRM_PATTERNS:
                continue
            affirm_matches.append(pat)

    deny_matches = []
    for pat in DENY_PATTERNS:
        if re.search(pat, resp_lower, re.MULTILINE | re.DOTALL):
            deny_matches.append(pat)

    # Inability/depravity content patterns only count as deny evidence when the
    # question expects a deny/reject answer (e.g., "Can man save himself?" -> deny)
    if expected in ("deny", "reject"):
        for pat in INABILITY_PATTERNS:
            if re.search(pat, resp_lower, re.MULTILINE | re.DOTALL):
                deny_matches.append(pat)

    if len(affirm_matches) > len(deny_matches):
        detected_position = "affirm"
    elif len(deny_matches) > len(affirm_matches):
        detected_position = "deny"
    else:
        detected_position = "unclear"

    # Check heterodox flags — only penalize if the flag is endorsed, not merely mentioned
    heterodox_flags = scoring.get("heterodox_flags", [])
    heterodox_flags_found = []
    for flag in heterodox_flags:
        if _heterodox_flag_endorsed(flag, response):
            heterodox_flags_found.append(flag)

    # Check required points using flexible concept matching
    required_points = scoring.get("required_points", [])
    required_points_found = []
    for point in required_points:
        if _concept_present(point, response):
            required_points_found.append(point)

    # Scoring logic
    score = 0

    if expected in ("deny", "reject"):
        if heterodox_flags_found and detected_position not in ("deny", "reject"):
            # If the model covered required points despite heterodox flags, give
            # partial credit — the flags likely come from a comparative section
            if required_points_found:
                coverage = len(required_points_found) / max(1, len(required_points))
                score = int(round(40 * coverage))
            else:
                score = 0
        elif detected_position in ("deny", "reject"):
            score = 70
            if required_points:
                bonus = (len(required_points_found) / len(required_points)) * 30
                score += int(round(bonus))
        elif detected_position == "unclear" and required_points_found:
            # Model didn't use clear deny language but covered the required theological points
            # Give partial credit based on how many points were covered
            coverage = len(required_points_found) / max(1, len(required_points))
            score = int(round(50 * coverage))
        else:
            score = 0
    elif expected == "affirm":
        if detected_position == "affirm":
            score = 70
            if required_points:
                bonus = (len(required_points_found) / len(required_points)) * 30
                score += int(round(bonus))
        elif detected_position == "unclear" and required_points_found:
            coverage = len(required_points_found) / max(1, len(required_points))
            score = int(round(50 * coverage))
        elif heterodox_flags_found and detected_position != "deny":
            # For affirm questions with heterodox flags but required points covered,
            # give partial credit (multi-view response pattern)
            if required_points_found:
                coverage = len(required_points_found) / max(1, len(required_points))
                score = int(round(40 * coverage))
            else:
                score = 0
        else:
            score = 0

    score = max(0, min(100, score))

    return {
        "score": score,
        "method": "position_detection",
        "details": {
            "expected_position": expected,
            "detected_position": detected_position,
            "affirm_pattern_matches": len(affirm_matches),
            "deny_pattern_matches": len(deny_matches),
            "heterodox_flags_found": heterodox_flags_found,
            "required_points_found": required_points_found,
            "required_points_missing": [
                p for p in required_points if p not in required_points_found
            ],
        },
    }


# ---------------------------------------------------------------------------
# 3. Reference check (biblical_reference)
# ---------------------------------------------------------------------------

BIBLE_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
    "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Psalm",
    "Proverbs", "Ecclesiastes", "Song of Solomon", "Song of Songs",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
    "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians",
    "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
]

ABBREV_TO_BOOK = {
    "Gen": "Genesis", "Ex": "Exodus", "Lev": "Leviticus",
    "Num": "Numbers", "Deut": "Deuteronomy", "Josh": "Joshua",
    "Judg": "Judges", "1 Sam": "1 Samuel", "2 Sam": "2 Samuel",
    "1 Kgs": "1 Kings", "2 Kgs": "2 Kings",
    "1 Chr": "1 Chronicles", "2 Chr": "2 Chronicles",
    "Neh": "Nehemiah", "Est": "Esther", "Ps": "Psalms",
    "Prov": "Proverbs", "Eccl": "Ecclesiastes",
    "Isa": "Isaiah", "Jer": "Jeremiah", "Lam": "Lamentations",
    "Ezek": "Ezekiel", "Dan": "Daniel", "Hos": "Hosea",
    "Amos": "Amos", "Obad": "Obadiah", "Jon": "Jonah",
    "Mic": "Micah", "Nah": "Nahum", "Hab": "Habakkuk",
    "Zeph": "Zephaniah", "Hag": "Haggai", "Zech": "Zechariah",
    "Mal": "Malachi", "Matt": "Matthew", "Mk": "Mark",
    "Lk": "Luke", "Jn": "John", "Rom": "Romans",
    "1 Cor": "1 Corinthians", "2 Cor": "2 Corinthians",
    "Gal": "Galatians", "Eph": "Ephesians", "Phil": "Philippians",
    "Col": "Colossians", "1 Thess": "1 Thessalonians",
    "2 Thess": "2 Thessalonians", "1 Tim": "1 Timothy",
    "2 Tim": "2 Timothy", "Tit": "Titus", "Phlm": "Philemon",
    "Heb": "Hebrews", "Jas": "James", "1 Pet": "1 Peter",
    "2 Pet": "2 Peter", "1 Jn": "1 John", "2 Jn": "2 John",
    "3 Jn": "3 John", "Rev": "Revelation",
}

# Build a set of all valid book names (canonical + abbreviations)
_VALID_BOOKS = set(b.lower() for b in BIBLE_BOOKS) | set(
    a.lower() for a in ABBREV_TO_BOOK
)

# Build combined regex for extracting references.
# Sort by length descending so longer names match first (e.g. "1 Samuel" before "1 Sam").
_ALL_NAMES = sorted(
    list(BIBLE_BOOKS) + list(ABBREV_TO_BOOK.keys()), key=len, reverse=True
)
_BOOK_PATTERN = "|".join(re.escape(name) for name in _ALL_NAMES)
_REF_RE = re.compile(
    rf'(?P<book>(?:{_BOOK_PATTERN}))\s+(?P<chapter>\d+)(?::(?P<verse_start>\d+)(?:\s*[-\u2013]\s*(?P<verse_end>\d+))?)?',
    re.IGNORECASE,
)


def _canonical_book(name: str) -> str | None:
    """Map a book name or abbreviation to its canonical full name, or None."""
    # Try exact match first
    for b in BIBLE_BOOKS:
        if name.lower() == b.lower():
            return b
    # Try abbreviation
    for abbr, full in ABBREV_TO_BOOK.items():
        if name.lower() == abbr.lower():
            return full
    return None


def _normalize_ref(ref_str: str) -> tuple[str, int, int | None, int | None]:
    """Parse a reference string into (canonical_book, chapter, verse_start, verse_end).

    Returns ("", 0, None, None) if unparseable.
    """
    # Normalize dashes
    ref_str = ref_str.replace("\u2013", "-").replace("\u2014", "-")
    m = _REF_RE.search(ref_str)
    if not m:
        return ("", 0, None, None)
    book = _canonical_book(m.group("book"))
    if not book:
        return ("", 0, None, None)
    chapter = int(m.group("chapter"))
    vs = int(m.group("verse_start")) if m.group("verse_start") else None
    ve = int(m.group("verse_end")) if m.group("verse_end") else None
    return (book, chapter, vs, ve)


def _refs_match(extracted: tuple, expected: tuple) -> bool:
    """Check if an extracted reference matches an expected one.

    Matches at book+chapter level if exact verse matching is too strict.
    """
    e_book, e_ch, e_vs, e_ve = extracted
    x_book, x_ch, x_vs, x_ve = expected
    if e_book != x_book or e_ch != x_ch:
        return False
    # Book and chapter match — accept at minimum
    if x_vs is None or e_vs is None:
        return True
    # Both have verse starts — check overlap
    if e_vs == x_vs:
        return True
    # Check if ranges overlap
    e_end = e_ve if e_ve else e_vs
    x_end = x_ve if x_ve else x_vs
    return not (e_end < x_vs or x_end < e_vs)


def score_reference_check(question: dict, response: str) -> dict:
    scoring = question["scoring"]
    expected_refs = scoring.get("expected_references", [])

    # Extract all Bible references from response
    matches = list(_REF_RE.finditer(response))

    extracted_references = []
    valid_references = []
    fabricated_references = []

    for m in matches:
        raw = m.group(0)
        book = _canonical_book(m.group("book"))
        if book:
            valid_references.append(raw)
        else:
            fabricated_references.append(raw)
        extracted_references.append(raw)

    # Also scan for things that look like references but use invalid book names.
    # Pattern: capitalized word(s) followed by chapter:verse that didn't match our regex
    fake_re = re.compile(
        r'(?<!\w)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d+:\d+', re.MULTILINE
    )
    for m in fake_re.finditer(response):
        candidate_book = m.group(1)
        if candidate_book.lower() not in _VALID_BOOKS and m.group(0) not in extracted_references:
            fabricated_references.append(m.group(0))
            extracted_references.append(m.group(0))

    # Parse expected references
    parsed_expected = [_normalize_ref(r) for r in expected_refs]
    # Parse valid extracted references
    parsed_extracted = [_normalize_ref(r) for r in valid_references]

    # Match extracted against expected
    expected_found = []
    expected_missing = []
    for i, exp in enumerate(parsed_expected):
        if exp[0] == "":
            expected_missing.append(expected_refs[i])
            continue
        matched = False
        for ext in parsed_extracted:
            if ext[0] == "":
                continue
            if _refs_match(ext, exp):
                matched = True
                break
        if matched:
            expected_found.append(expected_refs[i])
        else:
            expected_missing.append(expected_refs[i])

    # Score calculation
    if expected_refs:
        reference_score = (len(expected_found) / len(expected_refs)) * 70
    else:
        reference_score = 70 if valid_references else 0

    # Fabrication penalty
    if fabricated_references:
        reference_score -= 20

    # Bonus for additional valid references beyond expected
    extra_valid = max(0, len(valid_references) - len(expected_found))
    bonus = min(30, extra_valid * 10)
    reference_score += bonus

    score = max(0, min(100, int(round(reference_score))))

    return {
        "score": score,
        "method": "reference_check",
        "details": {
            "extracted_references": extracted_references,
            "valid_references": valid_references,
            "fabricated_references": fabricated_references,
            "expected_found": expected_found,
            "expected_missing": expected_missing,
        },
    }
