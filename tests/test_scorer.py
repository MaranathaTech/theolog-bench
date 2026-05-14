"""Unit tests for lib/scorer.py."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.scorer import (
    score_response,
    score_semantic_similarity,
    score_position_detection,
    score_reference_check,
    strip_think_blocks,
)


# ---------------------------------------------------------------------------
# semantic_similarity tests
# ---------------------------------------------------------------------------


class TestSemanticSimilarity:
    def test_exact_answer_scores_high(self, catechism_question):
        """Exact reference answer with all phrases and concepts should score high.

        With both phrases found (60%) and both concepts found (40%) = 100.
        The exact reference answer only matches the required_phrases, not the
        key_concepts (which use different wording), so score = 60.
        To get 100 we include all phrase and concept text.
        """
        result = score_semantic_similarity(
            catechism_question,
            "Man's chief end is to glorify God, and to enjoy him for ever. "
            "This speaks to God's glory and the enjoyment of God.",
        )
        assert result["score"] >= 90
        assert result["method"] == "semantic_similarity"

    def test_partial_answer_scores_medium(self, catechism_question):
        """One of two required phrases present should score in the middle range."""
        result = score_semantic_similarity(
            catechism_question,
            "The purpose of man is to glorify God in all things.",
        )
        # Has "glorify God" phrase but missing "enjoy him"
        # Has partial concept coverage
        assert 30 <= result["score"] <= 80
        assert "glorify God" in result["details"]["phrases_found"]
        assert "enjoy him" in result["details"]["phrases_missing"]

    def test_wrong_answer_scores_low(self, catechism_question):
        """Completely unrelated text should score < 20."""
        result = score_semantic_similarity(
            catechism_question,
            "The weather forecast shows rain tomorrow afternoon.",
        )
        assert result["score"] < 20

    def test_paraphrased_answer_scores_reasonably(self, catechism_question):
        """Rephrased answer with same concepts should score >= 40."""
        result = score_semantic_similarity(
            catechism_question,
            "Humanity's highest purpose is to glorify God and to find full enjoyment of God forever.",
        )
        # "glorify God" phrase is present; "enjoyment of God" concept is present
        assert result["score"] >= 40

    def test_empty_response_scores_zero(self, catechism_question):
        """Empty string should score 0."""
        result = score_semantic_similarity(catechism_question, "")
        assert result["score"] == 0

    def test_empty_phrase_lists_falls_back_to_overlap(self):
        """Question with no required_phrases or key_concepts falls back to word overlap."""
        question = {
            "id": "test-fallback",
            "category": "catechism_recall",
            "reference_answer": "The Word of God is the only rule.",
            "scoring": {"method": "semantic_similarity"},
        }
        result = score_semantic_similarity(
            question,
            "The Word of God is the only rule to direct us.",
        )
        # Should use word overlap — most words match
        assert result["score"] > 50

    def test_empty_phrase_lists_empty_response(self):
        """Fallback with empty response scores 0."""
        question = {
            "id": "test-fallback-empty",
            "category": "catechism_recall",
            "reference_answer": "The Word of God.",
            "scoring": {"method": "semantic_similarity"},
        }
        result = score_semantic_similarity(question, "")
        assert result["score"] == 0


# ---------------------------------------------------------------------------
# position_detection tests — deny
# ---------------------------------------------------------------------------


class TestPositionDetectionDeny:
    def test_correct_denial_with_reasoning(self, position_question_deny):
        """Denial with reasoning should score >= 70.

        Must avoid heterodox flag words ('lose salvation', 'can fall away',
        'conditional security') even when used in a negating context, because
        the scorer checks phrase presence without understanding negation.
        """
        result = score_position_detection(
            position_question_deny,
            "No. God's sovereign keeping ensures the perseverance of the saints. "
            "Those whom God has effectually called will never be separated from Him.",
        )
        assert result["score"] >= 70
        assert result["details"]["detected_position"] == "deny"

    def test_correct_denial_bare(self, position_question_deny):
        """Bare 'No.' should detect denial and score > 0."""
        result = score_position_detection(position_question_deny, "No.")
        assert result["score"] > 0
        assert result["details"]["detected_position"] == "deny"

    def test_wrong_affirmation(self, position_question_deny):
        """Affirming when denial expected should score 0."""
        result = score_position_detection(
            position_question_deny,
            "Yes, believers can fall away from grace and lose their salvation.",
        )
        # "can fall away" and "lose salvation" are heterodox flags
        assert result["score"] == 0

    def test_heterodox_flags_catch_wrong_position(self, position_question_deny):
        """Response endorsing heterodox flags with wrong position should score 0."""
        result = score_position_detection(
            position_question_deny,
            "Yes, believers can lose salvation. Conditional security is the biblical teaching "
            "and those who fall away prove they never had saving faith to begin with is incorrect.",
        )
        assert result["score"] == 0

    def test_ambiguous_response(self, position_question_deny):
        """Hedging/unclear text should score low."""
        result = score_position_detection(
            position_question_deny,
            "This is a complex topic with various perspectives in church history.",
        )
        assert result["score"] == 0
        assert result["details"]["detected_position"] == "unclear"


# ---------------------------------------------------------------------------
# position_detection tests — affirm
# ---------------------------------------------------------------------------


class TestPositionDetectionAffirm:
    def test_correct_affirmation(self, position_question_affirm):
        """Affirmation with reasoning should score >= 70."""
        result = score_position_detection(
            position_question_affirm,
            "Yes, absolutely. Scripture alone is the infallible rule of faith and practice.",
        )
        assert result["score"] >= 70
        assert result["details"]["detected_position"] == "affirm"

    def test_wrong_denial_of_affirmation(self, position_question_affirm):
        """Denying when affirmation expected should score 0."""
        result = score_position_detection(
            position_question_affirm,
            "No, tradition also holds authority alongside Scripture.",
        )
        assert result["score"] == 0


# ---------------------------------------------------------------------------
# position_detection tests — reject (error_detection)
# ---------------------------------------------------------------------------


class TestPositionDetectionReject:
    def test_correctly_rejects_arminian_statement(self, error_detection_question):
        """Correctly rejecting heterodox statement should score >= 70.

        Must avoid heterodox flag words ('foresaw would choose', 'foreseen faith')
        even when rejecting them, because the scorer checks phrase presence.
        Must include a DENY_PATTERN so that detected_position == 'deny'/'reject'.
        """
        result = score_position_detection(
            error_detection_question,
            "This is incorrect and must be rejected. We reject this Arminian error. "
            "Reformed theology teaches unconditional election rooted in God's sovereign choice alone.",
        )
        assert result["score"] >= 70

    def test_agrees_with_heterodox_statement(self, error_detection_question):
        """Agreeing with the heterodox statement should score 0."""
        result = score_position_detection(
            error_detection_question,
            "Yes, this is correct. God foresaw would choose Him and elected accordingly "
            "based on foreseen faith.",
        )
        assert result["score"] == 0


# ---------------------------------------------------------------------------
# Scorer fix tests — multi-view responses and new patterns
# ---------------------------------------------------------------------------


class TestNewDenyPatterns:
    """Tests for Fix 1: additional DENY_PATTERNS (is rejected, firmly rejects, etc.)."""

    def test_is_rejected_pattern(self, error_detection_question):
        """'is rejected' should register as deny."""
        result = score_position_detection(
            error_detection_question,
            "This view is rejected by Reformed theology. Unconditional election "
            "is rooted in God's sovereign choice alone.",
        )
        assert result["details"]["detected_position"] in ("deny", "reject")
        assert result["score"] >= 70

    def test_is_fundamentally_rejected(self, error_detection_question):
        """'is fundamentally rejected' should register as deny."""
        result = score_position_detection(
            error_detection_question,
            "The Arminian view is fundamentally rejected in the Reformed tradition. "
            "God's sovereign choice is unconditional.",
        )
        assert result["details"]["detected_position"] in ("deny", "reject")
        assert result["score"] >= 70

    def test_rejected_as_unbiblical(self, error_detection_question):
        """'rejected as unbiblical' should register as deny."""
        result = score_position_detection(
            error_detection_question,
            "This teaching is rejected as unbiblical. Reformed theology upholds "
            "unconditional election and God's sovereign choice.",
        )
        assert result["details"]["detected_position"] in ("deny", "reject")
        assert result["score"] >= 70

    def test_firmly_rejects(self, position_question_deny):
        """'firmly rejects' should register as deny."""
        result = score_position_detection(
            position_question_deny,
            "Reformed theology firmly rejects this claim. God's sovereign keeping "
            "ensures the perseverance of the saints.",
        )
        assert result["details"]["detected_position"] in ("deny", "reject")
        assert result["score"] >= 70


class TestExplanatoryAffirmSkip:
    """Tests for Fix 2: explanatory affirm patterns skipped on deny/reject questions."""

    def test_reformed_affirms_in_reject_context(self, error_detection_question):
        """'Reformed theology affirms' used to explain a rejection should not count as affirm."""
        result = score_position_detection(
            error_detection_question,
            "This statement is incorrect. Reformed theology affirms that God's "
            "sovereign choice is unconditional election, not based on foreseen faith.",
        )
        # "This is incorrect" = deny, "Reformed theology affirms" should be skipped
        assert result["details"]["detected_position"] in ("deny", "reject")
        assert result["score"] >= 70

    def test_scripture_teaches_in_reject_context(self, error_detection_question):
        """'Scripture teaches' as explanation in rejection should not count as affirm."""
        result = score_position_detection(
            error_detection_question,
            "This is incorrect. We reject this view. Scripture teaches that "
            "unconditional election flows from God's sovereign choice, not human decision.",
        )
        assert result["details"]["detected_position"] in ("deny", "reject")
        assert result["score"] >= 70

    def test_explanatory_affirm_still_counts_for_affirm_questions(self, position_question_affirm):
        """'Reformed theology affirms' should still count as affirm when expected=affirm."""
        result = score_position_detection(
            position_question_affirm,
            "Reformed theology affirms that Scripture alone is the infallible rule of faith.",
        )
        assert result["details"]["detected_position"] == "affirm"
        assert result["score"] >= 70


class TestHeterodoxPartialCredit:
    """Tests for Fix 3: partial credit when heterodox flags found but required points covered."""

    def test_multiview_with_required_points_gets_partial(self, error_detection_question):
        """Multi-view response with heterodox flag endorsed but required points should get partial credit."""
        result = score_position_detection(
            error_detection_question,
            # Affirming/unclear tone but covers required points and has heterodox flag
            "There are multiple views on election. Some believe God foresaw would choose "
            "certain individuals. However, unconditional election means God's sovereign "
            "choice is not based on foreseen faith.",
        )
        # Has heterodox flag "foresaw would choose" endorsed + required points covered
        # Should get partial credit (40 * coverage) rather than 0
        assert result["score"] > 0

    def test_heterodox_without_required_points_scores_zero(self, error_detection_question):
        """Heterodox flag endorsed with no required points covered should score 0."""
        result = score_position_detection(
            error_detection_question,
            "Yes, God foresaw would choose certain people and elected them accordingly "
            "based on foreseen faith. This is a well-known theological position.",
        )
        assert result["score"] == 0


# ---------------------------------------------------------------------------
# reference_check tests
# ---------------------------------------------------------------------------


class TestReferenceCheck:
    def test_all_expected_references_found(self, reference_question):
        """Response with all expected references should score high."""
        result = score_reference_check(
            reference_question,
            "The doctrine of election is taught in Ephesians 1:4-5, "
            "Romans 8:29-30, and Romans 9:11-13.",
        )
        assert result["score"] >= 70
        assert len(result["details"]["expected_found"]) == 3
        assert len(result["details"]["expected_missing"]) == 0

    def test_partial_references(self, reference_question):
        """Only one of three expected references should yield mid score."""
        result = score_reference_check(
            reference_question,
            "The doctrine of election is taught in Ephesians 1:4-5.",
        )
        assert 20 <= result["score"] <= 60
        assert len(result["details"]["expected_found"]) == 1

    def test_abbreviated_references_match(self, reference_question):
        """Abbreviated book names should match expected references."""
        result = score_reference_check(
            reference_question,
            "Election is taught in Eph 1:4-5, Rom 8:29-30, and Rom 9:11-13.",
        )
        assert len(result["details"]["expected_found"]) == 3

    def test_fabricated_reference_penalized(self, reference_question):
        """Fabricated reference (invalid book) should incur a penalty."""
        result = score_reference_check(
            reference_question,
            "Election is taught in Ephesians 1:4-5 and Hezekiah 3:12.",
        )
        assert "Hezekiah 3:12" in result["details"]["fabricated_references"]

    def test_no_references_at_all(self, reference_question):
        """Response with no verse citations should score near 0."""
        result = score_reference_check(
            reference_question,
            "The doctrine of election is an important theological topic.",
        )
        assert result["score"] <= 5

    def test_additional_valid_references_bonus(self, reference_question):
        """Extra valid references beyond expected should increase score."""
        result_base = score_reference_check(
            reference_question,
            "Election is taught in Ephesians 1:4-5, Romans 8:29-30, "
            "and Romans 9:11-13.",
        )
        result_extra = score_reference_check(
            reference_question,
            "Election is taught in Ephesians 1:4-5, Romans 8:29-30, "
            "Romans 9:11-13, John 6:44, and Acts 13:48.",
        )
        assert result_extra["score"] >= result_base["score"]


# ---------------------------------------------------------------------------
# Dispatch tests
# ---------------------------------------------------------------------------


class TestScoreResponseDispatch:
    def test_score_response_dispatches_semantic(self, catechism_question):
        """semantic_similarity method routes correctly."""
        result = score_response(
            catechism_question,
            "To glorify God and enjoy him forever.",
        )
        assert result["method"] == "semantic_similarity"

    def test_score_response_dispatches_position(self, position_question_deny):
        """position_detection method routes correctly."""
        result = score_response(position_question_deny, "No.")
        assert result["method"] == "position_detection"

    def test_score_response_dispatches_reference(self, reference_question):
        """reference_check method routes correctly."""
        result = score_response(
            reference_question,
            "Ephesians 1:4-5 teaches election.",
        )
        assert result["method"] == "reference_check"

    def test_score_response_dispatches_llm_judge(self, judge_question):
        """llm_judge method returns placeholder."""
        result = score_response(
            judge_question,
            "The WCF teaches Scripture is sufficient.",
        )
        assert result["method"] == "llm_judge"
        assert result["score"] == 0
        assert "deferred" in result["details"]["note"].lower()

    def test_score_response_unknown_method(self):
        """Unknown method returns score 0 with error."""
        question = {
            "scoring": {"method": "unknown_method"},
        }
        result = score_response(question, "Some response.")
        assert result["score"] == 0
        assert "error" in result["details"]

    def test_score_response_strips_think_blocks(self, catechism_question):
        """Think blocks should be stripped before scoring."""
        result = score_response(
            catechism_question,
            "<think>Let me reason about this... the chief end of man...</think>"
            "Man's chief end is to glorify God, and to enjoy him forever.",
        )
        assert result["score"] >= 60


# ---------------------------------------------------------------------------
# strip_think_blocks tests
# ---------------------------------------------------------------------------


class TestStripThinkBlocks:
    def test_strips_single_think_block(self):
        text = "<think>internal reasoning here</think>The final answer."
        assert strip_think_blocks(text) == "The final answer."

    def test_strips_multiline_think_block(self):
        text = (
            "<think>\nLet me think step by step.\n"
            "Step 1: consider the question.\n"
            "Step 2: formulate answer.\n</think>\n"
            "The answer is yes."
        )
        assert strip_think_blocks(text) == "The answer is yes."

    def test_strips_multiple_think_blocks(self):
        text = "<think>first</think>Part one. <think>second</think>Part two."
        assert strip_think_blocks(text) == "Part one. Part two."

    def test_no_think_blocks_unchanged(self):
        text = "A normal response with no thinking."
        assert strip_think_blocks(text) == text

    def test_empty_string(self):
        assert strip_think_blocks("") == ""

    def test_only_think_block_returns_original(self):
        """If stripping leaves nothing, return the original text."""
        text = "<think>All reasoning, no final answer</think>"
        assert strip_think_blocks(text) == text
