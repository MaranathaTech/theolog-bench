#!/usr/bin/env python3
"""Build the theolog-bench benchmark question bank from creed JSON files."""

import json
import re
from pathlib import Path

CREEDS_DIR = Path(__file__).parent / ".." / "data" / "raw" / "creeds"
OUTPUT_FILE = Path(__file__).parent / "benchmark.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(filename: str) -> dict:
    path = CREEDS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_phrases(answer: str) -> list[str]:
    """Split an answer into substantive phrase-level chunks."""
    parts = re.split(r"[;,]", answer)
    phrases = [p.strip().rstrip(".") for p in parts if len(p.strip()) > 15]
    return phrases[:4]


def extract_concepts(answer: str) -> list[str]:
    """Extract clause-level concept chunks from an answer."""
    parts = re.split(r"[;,.]", answer)
    concepts = [p.strip() for p in parts if len(p.strip()) > 10]
    return concepts[:4]


# ---------------------------------------------------------------------------
# Category 1: Catechism Recall (~120 questions)
# ---------------------------------------------------------------------------

def build_catechism_recall() -> list[dict]:
    questions = []

    catechisms = [
        {
            "file": "westminster_shorter_catechism.json",
            "id_prefix": "wsc",
            "title": "Westminster Shorter Catechism",
            "selected": list(range(1, 31)),  # Q1-Q30
        },
        {
            "file": "heidelberg_catechism.json",
            "id_prefix": "hc",
            "title": "Heidelberg Catechism",
            "selected": [
                1, 21, 26, 27, 28, 29, 30, 31, 32, 33, 34, 44, 45, 54, 55,
                56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 80, 86, 115, 129,
            ],
        },
        {
            "file": "westminster_larger_catechism.json",
            "id_prefix": "wlc",
            "title": "Westminster Larger Catechism",
            "selected": [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 25, 27, 29,
                30, 31, 32, 33, 34, 35, 36, 38, 57, 58, 59, 60, 70,
            ],
        },
        {
            "file": "puritan_catechism.json",
            "id_prefix": "pc",
            "title": "Puritan Catechism",
            "selected": list(range(1, 16)),  # Q1-Q15
        },
        {
            "file": "keachs_catechism.json",
            "id_prefix": "kc",
            "title": "Keach's Catechism",
            "selected": list(range(1, 16)),  # Q1-Q15
        },
    ]

    for cat in catechisms:
        data = load_json(cat["file"])
        items = data["Data"]
        selected_set = set(cat["selected"])

        for item in items:
            num = item["Number"]
            if num not in selected_set:
                continue

            answer = item["Answer"]
            questions.append({
                "id": f"{cat['id_prefix']}-{num:03d}",
                "category": "catechism_recall",
                "source": f"{cat['title']} Q{num}",
                "question": item["Question"],
                "reference_answer": answer,
                "scoring": {
                    "method": "semantic_similarity",
                    "required_phrases": extract_phrases(answer),
                    "key_concepts": extract_concepts(answer),
                },
            })

    return questions


# ---------------------------------------------------------------------------
# Category 2: Confessional Knowledge (~40 questions)
# ---------------------------------------------------------------------------

# WCF has no Title field on chapters — map manually
WCF_CHAPTER_TITLES = {
    "1": "Of the Holy Scripture",
    "2": "Of God, and of the Holy Trinity",
    "3": "Of God's Eternal Decree",
    "4": "Of Creation",
    "5": "Of Providence",
    "6": "Of the Fall of Man, of Sin, and of the Punishment thereof",
    "7": "Of God's Covenant with Man",
    "8": "Of Christ the Mediator",
    "9": "Of Free Will",
    "10": "Of Effectual Calling",
    "11": "Of Justification",
    "12": "Of Adoption",
    "13": "Of Sanctification",
    "14": "Of Saving Faith",
    "15": "Of Repentance unto Life",
    "16": "Of Good Works",
    "17": "Of the Perseverance of the Saints",
    "18": "Of the Assurance of Grace and Salvation",
    "19": "Of the Law of God",
    "20": "Of Christian Liberty, and Liberty of Conscience",
    "21": "Of Religious Worship, and the Sabbath Day",
    "22": "Of Lawful Oaths and Vows",
    "23": "Of the Civil Magistrate",
    "24": "Of Marriage and Divorce",
    "25": "Of the Church",
    "26": "Of the Communion of Saints",
    "27": "Of the Sacraments",
    "28": "Of Baptism",
    "29": "Of the Lord's Supper",
    "30": "Of Church Censures",
    "31": "Of Synods and Councils",
    "32": "Of the State of Men after Death, and of the Resurrection of the Dead",
    "33": "Of the Last Judgment",
}


def build_confessional_knowledge() -> list[dict]:
    questions = []

    # --- WCF ---
    wcf = load_json("westminster_confession_of_faith.json")
    wcf_chapters = [1, 2, 3, 5, 7, 8, 10, 11, 17, 33]
    for chapter_num in wcf_chapters:
        ch_str = str(chapter_num)
        chapter = next(c for c in wcf["Data"] if c["Chapter"] == ch_str)
        title = WCF_CHAPTER_TITLES[ch_str]
        content_parts = [s["Content"] for s in chapter["Sections"]]
        full_content = " ".join(content_parts)

        questions.append({
            "id": f"wcf-ch{chapter_num:02d}",
            "category": "confessional_knowledge",
            "source": f"Westminster Confession of Faith, Chapter {chapter_num}",
            "question": f"What does the Westminster Confession of Faith teach about {title.lower().removeprefix('of ')}?",
            "reference_answer": full_content,
            "scoring": {
                "method": "llm_judge",
                "rubric": _wcf_rubric(title, content_parts),
            },
        })

    # --- Belgic Confession ---
    belgic = load_json("belgic_confession_of_faith.json")
    belgic_articles = [1, 2, 7, 12, 13, 14, 15, 16, 22, 37]
    for art_num in belgic_articles:
        art_str = str(art_num)
        article = next(a for a in belgic["Data"] if a["Article"] == art_str)
        title = article["Title"]
        content = article["Content"]

        questions.append({
            "id": f"belgic-art{art_num:02d}",
            "category": "confessional_knowledge",
            "source": f"Belgic Confession, Article {art_num}",
            "question": f"What does the Belgic Confession teach about {title.lower()}?",
            "reference_answer": content,
            "scoring": {
                "method": "llm_judge",
                "rubric": f"Must address the key points of Article {art_num} ({title}). Should align with the Belgic Confession's teaching on this topic.",
            },
        })

    # --- Canons of Dort ---
    # The Canons have 4 data chapters: "1", "2", "3&4", "4"
    # These correspond to the traditional 5 Heads of Doctrine:
    #   Head 1 = Chapter "1", Head 2 = Chapter "2",
    #   Heads 3&4 = Chapter "3&4", Head 5 = Chapter "4"
    dort = load_json("canons_of_dort.json")
    dort_chapters = [
        ("1", "Divine Predestination", ["A7", "A9"]),
        ("2", "The Death of Christ and the Redemption of Men", ["A1", "A8"]),
        ("3&4", "The Corruption of Man and His Conversion to God", ["A1", "A3"]),
        ("3&4", "The Conversion of Man and the Manner Thereof", ["A10", "A11"]),
        ("4", "The Perseverance of the Saints", ["A1", "A8"]),
    ]
    for ch_str, topic, section_ids in dort_chapters:
        chapter = next(c for c in dort["Data"] if c["Chapter"] == ch_str)

        for sec_id in section_ids:
            sec = next(s for s in chapter["Sections"] if s["Section"] == sec_id)
            head_label = ch_str.replace("&", "/")
            questions.append({
                "id": f"dort-ch{ch_str.replace('&', '')}-{sec_id.lower()}",
                "category": "confessional_knowledge",
                "source": f"Canons of Dort, Head {head_label}, Article {sec_id[1:]}",
                "question": f"What do the Canons of Dort teach about {topic.lower()} in Article {sec_id[1:]}?",
                "reference_answer": sec["Content"],
                "scoring": {
                    "method": "llm_judge",
                    "rubric": f"Must reflect the teaching of Canons of Dort, Head {head_label} ({topic}), Article {sec_id[1:]}. Should align with Reformed soteriology.",
                },
            })

    # --- LBCF 1689 ---
    lbcf = load_json("london_baptist_1689.json")
    lbcf_chapters = [1, 2, 3, 5, 7, 8, 10, 11, 17, 32]
    for chapter_num in lbcf_chapters:
        ch_str = str(chapter_num)
        chapter = next(c for c in lbcf["Data"] if c["Chapter"] == ch_str)
        title = chapter["Title"]
        content_parts = [s["Content"] for s in chapter["Sections"]]
        full_content = " ".join(content_parts)

        questions.append({
            "id": f"lbcf-ch{chapter_num:02d}",
            "category": "confessional_knowledge",
            "source": f"1689 London Baptist Confession, Chapter {chapter_num}",
            "question": f"What does the 1689 London Baptist Confession teach about {title.lower().removeprefix('of ')}?",
            "reference_answer": full_content,
            "scoring": {
                "method": "llm_judge",
                "rubric": f"Must address the key points of Chapter {chapter_num} ({title}). Should align with the 1689 London Baptist Confession's Reformed Baptist theology.",
            },
        })

    return questions


def _wcf_rubric(title: str, sections: list[str]) -> str:
    """Generate a rubric summary for a WCF chapter."""
    # Take a few key phrases from each section to build the rubric
    key_points = []
    for sec in sections[:3]:
        words = sec.split()[:20]
        key_points.append(" ".join(words) + "...")
    rubric = f"Must address the key teachings of WCF on {title}. "
    rubric += "Should cover: " + "; ".join(key_points)
    rubric += f" Should align with the Westminster Confession's teaching on {title.lower()}."
    return rubric


# ---------------------------------------------------------------------------
# Category 3: Doctrinal Position / TULIP + Solas (~30 questions)
# ---------------------------------------------------------------------------

def build_doctrinal_position() -> list[dict]:
    questions = []

    # --- TULIP ---
    tulip = [
        # Total Depravity
        {
            "id": "tulip-td-01",
            "question": "Is fallen man able to choose God of his own free will?",
            "expected_position": "deny",
            "required_points": [
                "Fallen man is totally unable to choose God",
                "The will is in bondage to sin",
                "Regeneration must precede faith",
            ],
            "key_references": ["Rom 3:10-12", "Eph 2:1-3", "John 6:44"],
            "heterodox_flags": ["free will can choose God", "prevenient grace enables choice"],
        },
        {
            "id": "tulip-td-02",
            "question": "Can an unregenerate person do anything spiritually good in God's sight?",
            "expected_position": "deny",
            "required_points": [
                "Without regeneration no one can do spiritual good",
                "Even outward conformity to the law is not truly good without faith",
                "The natural man is dead in sin",
            ],
            "key_references": ["Rom 8:7-8", "Heb 11:6", "Isa 64:6"],
            "heterodox_flags": ["natural goodness suffices", "everyone can please God"],
        },
        {
            "id": "tulip-td-03",
            "question": "Does the fall affect every part of human nature?",
            "expected_position": "affirm",
            "required_points": [
                "The fall corrupted every faculty of man",
                "Mind, will, and affections are all affected",
                "This is total depravity — not utter depravity",
            ],
            "key_references": ["Gen 6:5", "Jer 17:9", "Rom 3:10-18"],
            "heterodox_flags": ["reason is unaffected", "the will remains free"],
        },
        # Unconditional Election
        {
            "id": "tulip-ue-01",
            "question": "Does God choose to save people based on foreseen faith?",
            "expected_position": "deny",
            "required_points": [
                "Election is not based on foreseen faith or merit",
                "Election is according to God's sovereign good pleasure",
                "Faith is the result, not the cause, of election",
            ],
            "key_references": ["Eph 1:4-5", "Rom 9:11-13", "Acts 13:48"],
            "heterodox_flags": ["God foresees who will believe", "election is conditional"],
        },
        {
            "id": "tulip-ue-02",
            "question": "Is God's election of individuals to salvation conditional or unconditional?",
            "expected_position": "affirm",
            "required_points": [
                "Election is unconditional",
                "It is based solely on God's sovereign will",
                "No human merit or action conditions God's choice",
            ],
            "key_references": ["Rom 9:15-16", "Eph 1:11", "2 Tim 1:9"],
            "heterodox_flags": ["election is conditional on faith", "God elects based on merit"],
        },
        {
            "id": "tulip-ue-03",
            "question": "Did God choose His elect before the foundation of the world?",
            "expected_position": "affirm",
            "required_points": [
                "Election occurred before the foundation of the world",
                "It is an eternal decree of God",
                "God's choice preceded any human action or existence",
            ],
            "key_references": ["Eph 1:4", "2 Thess 2:13", "Rev 17:8"],
            "heterodox_flags": ["election happens in time", "God reacts to human choices"],
        },
        # Limited Atonement
        {
            "id": "tulip-la-01",
            "question": "Did Christ die to actually save His people or merely to make salvation possible?",
            "expected_position": "affirm",
            "required_points": [
                "Christ's death actually accomplished redemption for the elect",
                "The atonement is definite and effectual",
                "Christ did not merely make salvation possible but secured it",
            ],
            "key_references": ["John 10:11", "John 10:15", "Eph 5:25", "Matt 1:21"],
            "heterodox_flags": ["Christ made salvation possible for all", "atonement is universal in intent"],
        },
        {
            "id": "tulip-la-02",
            "question": "For whom did Christ specifically lay down His life?",
            "expected_position": "affirm",
            "required_points": [
                "Christ laid down His life for His sheep, the elect",
                "The atonement was particular and definite",
                "Scripture speaks of Christ dying for His people, His church, His sheep",
            ],
            "key_references": ["John 10:11", "John 10:15", "Acts 20:28", "Eph 5:25"],
            "heterodox_flags": ["Christ died for every individual equally", "universal atonement"],
        },
        {
            "id": "tulip-la-03",
            "question": "Is the atonement of Christ sufficient for all but efficient only for the elect?",
            "expected_position": "affirm",
            "required_points": [
                "The atonement is sufficient for all in its value and dignity",
                "It is efficient (effectual) only for the elect",
                "This reflects the classic Reformed distinction",
            ],
            "key_references": ["1 John 2:2", "John 10:15", "John 10:26"],
            "heterodox_flags": ["the atonement fails for some it was intended for"],
        },
        # Irresistible Grace
        {
            "id": "tulip-ig-01",
            "question": "Can those whom God has chosen to save ultimately resist His grace?",
            "expected_position": "deny",
            "required_points": [
                "God's effectual call cannot be ultimately resisted",
                "The Holy Spirit overcomes natural resistance",
                "All whom God has chosen will come to faith",
            ],
            "key_references": ["John 6:37", "John 6:44", "Phil 2:13", "Rom 8:30"],
            "heterodox_flags": ["grace can be resisted", "humans have final say"],
        },
        {
            "id": "tulip-ig-02",
            "question": "Does the Holy Spirit effectually call and regenerate all of the elect?",
            "expected_position": "affirm",
            "required_points": [
                "The Spirit effectually calls every one of the elect",
                "Regeneration is a work of the Spirit alone",
                "The effectual call always results in conversion",
            ],
            "key_references": ["John 3:5-8", "Titus 3:5", "1 Pet 1:3", "Rom 8:30"],
            "heterodox_flags": ["the Spirit only assists", "calling can fail"],
        },
        {
            "id": "tulip-ig-03",
            "question": "Is regeneration a work of God alone, or does it require human cooperation?",
            "expected_position": "affirm",
            "required_points": [
                "Regeneration is monergistic — a work of God alone",
                "Human cooperation is not required for the new birth",
                "Man is passive in regeneration, active in conversion",
            ],
            "key_references": ["John 1:13", "Eph 2:4-5", "James 1:18"],
            "heterodox_flags": ["synergism", "man cooperates in regeneration"],
        },
        # Perseverance of the Saints
        {
            "id": "tulip-ps-01",
            "question": "Can a true believer lose their salvation?",
            "expected_position": "deny",
            "required_points": [
                "True believers cannot lose their salvation",
                "God preserves His elect in a state of grace",
                "Those who fall away were never truly regenerate",
            ],
            "key_references": ["John 10:28-29", "Rom 8:38-39", "1 John 2:19"],
            "heterodox_flags": ["believers can lose salvation", "apostasy of the regenerate"],
        },
        {
            "id": "tulip-ps-02",
            "question": "Will all who are truly born again persevere to the end?",
            "expected_position": "affirm",
            "required_points": [
                "All truly regenerate persons will persevere",
                "Perseverance is grounded in God's faithfulness, not human effort",
                "God's preserving grace ensures final salvation",
            ],
            "key_references": ["Phil 1:6", "1 Pet 1:5", "Jude 1:24"],
            "heterodox_flags": ["perseverance depends on human effort", "saints can fall finally"],
        },
        {
            "id": "tulip-ps-03",
            "question": "Does God preserve His elect in a state of grace?",
            "expected_position": "affirm",
            "required_points": [
                "God actively preserves believers",
                "Preservation is by God's power, not human strength",
                "Believers may fall into sin but will not fall away finally",
            ],
            "key_references": ["1 Pet 1:5", "John 10:28-29", "Ps 37:28"],
            "heterodox_flags": ["God does not guarantee preservation", "believers keep themselves"],
        },
    ]

    for t in tulip:
        questions.append({
            "id": t["id"],
            "category": "doctrinal_position",
            "source": "TULIP — Reformed Soteriology",
            "question": t["question"],
            "reference_answer": " ".join(t["required_points"]),
            "scoring": {
                "method": "position_detection",
                "expected_position": t["expected_position"],
                "required_points": t["required_points"],
                "key_references": t["key_references"],
                "heterodox_flags": t["heterodox_flags"],
            },
        })

    # --- Five Solas ---
    solas = [
        # Sola Scriptura
        {
            "id": "sola-ss-01",
            "question": "Is the Bible the sole infallible rule of faith and practice?",
            "expected_position": "affirm",
            "required_points": [
                "Scripture alone is the infallible rule",
                "No church tradition holds equal authority",
                "The Bible is sufficient for faith and life",
            ],
            "key_references": ["2 Tim 3:16-17", "Isa 8:20", "Matt 15:3-9"],
            "heterodox_flags": ["tradition equals Scripture", "the church determines truth"],
        },
        {
            "id": "sola-ss-02",
            "question": "Do church traditions hold equal authority with Scripture?",
            "expected_position": "deny",
            "required_points": [
                "Church traditions do not hold equal authority with Scripture",
                "Scripture is the supreme standard",
                "Traditions must be tested by Scripture",
            ],
            "key_references": ["Mark 7:8-13", "Col 2:8", "2 Tim 3:16-17"],
            "heterodox_flags": ["tradition and Scripture are co-equal", "magisterium defines doctrine"],
        },
        # Sola Fide
        {
            "id": "sola-sf-01",
            "question": "Is faith alone sufficient for justification before God?",
            "expected_position": "affirm",
            "required_points": [
                "Justification is by faith alone",
                "Faith is the sole instrument of justification",
                "Good works are the fruit, not the basis, of justification",
            ],
            "key_references": ["Rom 3:28", "Eph 2:8-9", "Gal 2:16"],
            "heterodox_flags": ["works contribute to justification", "faith and works justify together"],
        },
        {
            "id": "sola-sf-02",
            "question": "Are good works necessary for justification?",
            "expected_position": "deny",
            "required_points": [
                "Good works are not necessary for justification",
                "Works are the evidence, not the ground, of justification",
                "Justification is a legal declaration based on Christ's righteousness alone",
            ],
            "key_references": ["Rom 4:4-5", "Titus 3:5", "Gal 2:21"],
            "heterodox_flags": ["works are meritorious for justification", "final justification by works"],
        },
        # Sola Gratia
        {
            "id": "sola-sg-01",
            "question": "Is salvation entirely a gift of God's grace?",
            "expected_position": "affirm",
            "required_points": [
                "Salvation is entirely by grace",
                "Grace is unmerited favor from God",
                "No human effort earns or contributes to salvation",
            ],
            "key_references": ["Eph 2:8-9", "Rom 11:6", "Titus 3:5"],
            "heterodox_flags": ["human merit contributes", "grace plus works"],
        },
        {
            "id": "sola-sg-02",
            "question": "Does God's grace in salvation depend on human cooperation?",
            "expected_position": "deny",
            "required_points": [
                "Saving grace does not depend on human cooperation",
                "Grace is efficacious and sovereign",
                "God's grace is the sole cause of salvation",
            ],
            "key_references": ["John 1:13", "Rom 9:16", "Phil 2:13"],
            "heterodox_flags": ["synergism", "grace requires human cooperation"],
        },
        # Solus Christus
        {
            "id": "sola-sc-01",
            "question": "Is Jesus Christ the only mediator between God and man?",
            "expected_position": "affirm",
            "required_points": [
                "Christ is the sole mediator",
                "No saint, priest, or other being mediates between God and man",
                "Access to God is only through Christ",
            ],
            "key_references": ["1 Tim 2:5", "John 14:6", "Acts 4:12"],
            "heterodox_flags": ["saints mediate", "Mary as mediatrix"],
        },
        {
            "id": "sola-sc-02",
            "question": "Can salvation be found through any means other than Christ?",
            "expected_position": "deny",
            "required_points": [
                "There is no salvation apart from Christ",
                "Christ's work is the exclusive ground of salvation",
                "All other ways are excluded",
            ],
            "key_references": ["Acts 4:12", "John 14:6", "John 3:36"],
            "heterodox_flags": ["multiple paths to God", "anonymous Christians", "inclusivism"],
        },
        # Soli Deo Gloria
        {
            "id": "sola-sdg-01",
            "question": "Is God's glory the ultimate purpose of all things?",
            "expected_position": "affirm",
            "required_points": [
                "God's glory is the chief end of all things",
                "All of creation exists for God's glory",
                "Even salvation serves to display God's glory",
            ],
            "key_references": ["Rom 11:36", "1 Cor 10:31", "Eph 1:6", "Eph 1:12"],
            "heterodox_flags": ["man's happiness is the chief end", "God exists for us"],
        },
        {
            "id": "sola-sdg-02",
            "question": "Should salvation bring glory to God alone, not to man?",
            "expected_position": "affirm",
            "required_points": [
                "Salvation glorifies God alone",
                "No human boasting is warranted",
                "God receives all credit for salvation",
            ],
            "key_references": ["Eph 2:8-9", "1 Cor 1:29-31", "Ps 115:1"],
            "heterodox_flags": ["man deserves credit", "human decision is the decisive factor"],
        },
    ]

    for s in solas:
        questions.append({
            "id": s["id"],
            "category": "doctrinal_position",
            "source": "Five Solas — Protestant Reformation",
            "question": s["question"],
            "reference_answer": " ".join(s["required_points"]),
            "scoring": {
                "method": "position_detection",
                "expected_position": s["expected_position"],
                "required_points": s["required_points"],
                "key_references": s["key_references"],
                "heterodox_flags": s["heterodox_flags"],
            },
        })

    # --- Additional Doctrinal ---
    additional = [
        {
            "id": "doc-add-01",
            "question": "What is the Reformed view of infant baptism?",
            "scoring_override": {
                "method": "llm_judge",
                "rubric": (
                    "The model should demonstrate awareness that Reformed theology has an internal "
                    "debate on this topic. The mainstream Reformed (WCF/Westminster) position affirms "
                    "infant baptism as a covenant sign replacing circumcision (Gen 17:7, Acts 2:39, "
                    "Col 2:11-12). Reformed Baptists (1689 LBCF) hold that only believer's baptism "
                    "is valid. A strong answer presents the paedobaptist position and its covenantal "
                    "reasoning, and may also acknowledge the Reformed Baptist dissent. Penalize only "
                    "if the answer is theologically inaccurate or dismisses infant baptism as having "
                    "no basis in Reformed thought."
                ),
            },
            "required_points": [
                "Reformed paedobaptists affirm infant baptism as a sign of the covenant",
                "Covenantal reasoning connects baptism to circumcision",
                "Reformed Baptists hold a different position within the Reformed tradition",
            ],
            "key_references": ["Gen 17:7", "Acts 2:39", "Col 2:11-12"],
            "heterodox_flags": [],
        },
        {
            "id": "doc-add-02",
            "question": "What is the Reformed view of the relationship between law and gospel?",
            "expected_position": "affirm",
            "required_points": [
                "The law reveals sin and drives to Christ",
                "The gospel offers free grace through Christ",
                "The third use of the law guides the believer's life",
            ],
            "key_references": ["Gal 3:24", "Rom 3:20", "Rom 7:12", "Ps 119:105"],
            "heterodox_flags": ["antinomianism", "law is abolished entirely"],
        },
        {
            "id": "doc-add-03",
            "question": "Does Reformed theology teach that God is the author of sin?",
            "expected_position": "deny",
            "required_points": [
                "God is not the author of sin",
                "God ordains whatsoever comes to pass but is not the efficient cause of sin",
                "Secondary causes and human responsibility are upheld",
            ],
            "key_references": ["James 1:13", "1 John 1:5", "WCF 3.1"],
            "heterodox_flags": ["God causes sin", "determinism eliminates responsibility"],
        },
        {
            "id": "doc-add-04",
            "question": "Is the visible church necessary for salvation?",
            "expected_position": "affirm",
            "required_points": [
                "The visible church is ordinarily necessary for salvation",
                "The church is the means God uses to gather and perfect His people",
                "Outside the visible church there is no ordinary possibility of salvation",
            ],
            "key_references": ["Heb 10:25", "Acts 2:47", "WCF 25.2"],
            "heterodox_flags": ["the church is irrelevant", "individualism suffices"],
        },
        {
            "id": "doc-add-05",
            "question": "What role do good works play in the life of a believer?",
            "expected_position": "affirm",
            "required_points": [
                "Good works are the necessary fruit of true faith",
                "They are not the ground of justification but evidence of it",
                "Believers are created in Christ Jesus for good works",
            ],
            "key_references": ["Eph 2:10", "James 2:17-18", "Titus 2:14"],
            "heterodox_flags": ["works earn merit", "antinomianism", "works are optional"],
        },
    ]

    for a in additional:
        # Allow individual items to override the default position_detection scoring
        if "scoring_override" in a:
            scoring = a["scoring_override"]
        else:
            scoring = {
                "method": "position_detection",
                "expected_position": a["expected_position"],
                "required_points": a["required_points"],
                "key_references": a["key_references"],
                "heterodox_flags": a["heterodox_flags"],
            }
        entry = {
            "id": a["id"],
            "category": "doctrinal_position",
            "source": "Reformed Doctrinal Distinctives",
            "question": a["question"],
            "reference_answer": " ".join(a["required_points"]),
            "scoring": scoring,
        }
        questions.append(entry)

    return questions


# ---------------------------------------------------------------------------
# Category 4: Biblical Reference Accuracy (~30 questions)
# ---------------------------------------------------------------------------

def build_biblical_reference() -> list[dict]:
    items = [
        {
            "id": "bibref-01",
            "question": "What Bible passages teach the doctrine of election?",
            "expected_references": ["Eph 1:4-5", "Rom 8:29-30", "Rom 9:11-13"],
        },
        {
            "id": "bibref-02",
            "question": "Where does Scripture teach the perseverance of the saints?",
            "expected_references": ["John 10:28-29", "Rom 8:38-39", "Phil 1:6"],
        },
        {
            "id": "bibref-03",
            "question": "What verses support the doctrine of total depravity?",
            "expected_references": ["Rom 3:10-12", "Eph 2:1-3", "Gen 6:5"],
        },
        {
            "id": "bibref-04",
            "question": "Which passages teach justification by faith alone?",
            "expected_references": ["Rom 3:28", "Eph 2:8-9", "Gal 2:16"],
        },
        {
            "id": "bibref-05",
            "question": "What Scripture passages teach the doctrine of original sin?",
            "expected_references": ["Rom 5:12", "Rom 5:18-19", "Ps 51:5", "Gen 3:6-7"],
        },
        {
            "id": "bibref-06",
            "question": "Where does the Bible teach the doctrine of the Trinity?",
            "expected_references": ["Matt 28:19", "2 Cor 13:14", "John 1:1", "Gen 1:26"],
        },
        {
            "id": "bibref-07",
            "question": "What passages affirm the full deity of Jesus Christ?",
            "expected_references": ["John 1:1", "John 1:14", "Col 2:9", "Heb 1:3", "Phil 2:6"],
        },
        {
            "id": "bibref-08",
            "question": "Which Bible passages teach the bodily resurrection of Christ?",
            "expected_references": ["1 Cor 15:3-8", "Matt 28:5-6", "Luke 24:39", "John 20:27"],
        },
        {
            "id": "bibref-09",
            "question": "What Scripture supports the doctrine of substitutionary atonement?",
            "expected_references": ["Isa 53:5-6", "2 Cor 5:21", "1 Pet 2:24", "Rom 3:25"],
        },
        {
            "id": "bibref-10",
            "question": "Where does the Bible teach the imputation of Christ's righteousness?",
            "expected_references": ["2 Cor 5:21", "Rom 4:3-6", "Phil 3:9", "Rom 5:19"],
        },
        {
            "id": "bibref-11",
            "question": "What passages describe the process of sanctification?",
            "expected_references": ["1 Thess 4:3", "Phil 2:12-13", "2 Cor 3:18", "Heb 12:14"],
        },
        {
            "id": "bibref-12",
            "question": "Where does Scripture teach about the means of grace?",
            "expected_references": ["Rom 10:17", "Acts 2:42", "1 Cor 11:23-26", "Matt 28:19"],
        },
        {
            "id": "bibref-13",
            "question": "What Bible passages support covenant theology?",
            "expected_references": ["Gen 17:7", "Jer 31:31-34", "Heb 8:6-13", "Gal 3:29"],
        },
        {
            "id": "bibref-14",
            "question": "Where does the Bible teach about the Lord's Supper?",
            "expected_references": ["1 Cor 11:23-26", "Matt 26:26-28", "Luke 22:19-20"],
        },
        {
            "id": "bibref-15",
            "question": "What passages address the doctrine of baptism?",
            "expected_references": ["Matt 28:19", "Acts 2:38-39", "Rom 6:3-4", "Col 2:11-12"],
        },
        {
            "id": "bibref-16",
            "question": "Where does Scripture teach about church government and eldership?",
            "expected_references": ["1 Tim 3:1-7", "Titus 1:5-9", "Acts 14:23", "1 Pet 5:1-4"],
        },
        {
            "id": "bibref-17",
            "question": "What Bible passages teach about the second coming of Christ?",
            "expected_references": ["Acts 1:11", "1 Thess 4:16-17", "Matt 24:30", "Rev 1:7"],
        },
        {
            "id": "bibref-18",
            "question": "Where does the Bible teach about the final judgment?",
            "expected_references": ["Matt 25:31-46", "Rev 20:11-15", "2 Cor 5:10", "Acts 17:31"],
        },
        {
            "id": "bibref-19",
            "question": "What Scripture passages teach about heaven and hell?",
            "expected_references": ["Rev 21:1-4", "Matt 25:46", "2 Thess 1:9", "John 14:2-3"],
        },
        {
            "id": "bibref-20",
            "question": "Where does the Bible teach the doctrine of creation?",
            "expected_references": ["Gen 1:1", "John 1:3", "Col 1:16", "Heb 11:3"],
        },
        {
            "id": "bibref-21",
            "question": "What passages teach about God's providence?",
            "expected_references": ["Matt 10:29-31", "Rom 8:28", "Eph 1:11", "Dan 4:35"],
        },
        {
            "id": "bibref-22",
            "question": "Where does Scripture teach about the nature and practice of prayer?",
            "expected_references": ["Matt 6:9-13", "Phil 4:6", "1 Thess 5:17", "John 14:13-14"],
        },
        {
            "id": "bibref-23",
            "question": "What Bible passages relate to Sabbath observance?",
            "expected_references": ["Exod 20:8-11", "Isa 58:13-14", "Mark 2:27-28", "Heb 4:9-10"],
        },
        {
            "id": "bibref-24",
            "question": "Where are the Ten Commandments given in Scripture?",
            "expected_references": ["Exod 20:1-17", "Deut 5:6-21"],
        },
        {
            "id": "bibref-25",
            "question": "Where does Jesus teach the Lord's Prayer?",
            "expected_references": ["Matt 6:9-13", "Luke 11:2-4"],
        },
        {
            "id": "bibref-26",
            "question": "What passages address the sacraments in Reformed theology?",
            "expected_references": ["Matt 28:19", "1 Cor 11:23-26", "Acts 2:38-39", "Rom 6:3-4"],
        },
        {
            "id": "bibref-27",
            "question": "Where does the Bible teach about church discipline?",
            "expected_references": ["Matt 18:15-17", "1 Cor 5:1-13", "Titus 3:10", "2 Thess 3:14-15"],
        },
        {
            "id": "bibref-28",
            "question": "What Scripture passages teach about Christian liberty?",
            "expected_references": ["Gal 5:1", "1 Cor 8:9", "Rom 14:1-23", "1 Pet 2:16"],
        },
        {
            "id": "bibref-29",
            "question": "Where does the Bible teach about marriage?",
            "expected_references": ["Gen 2:24", "Eph 5:22-33", "Matt 19:4-6", "Heb 13:4"],
        },
        {
            "id": "bibref-30",
            "question": "What passages address the role of the civil magistrate?",
            "expected_references": ["Rom 13:1-7", "1 Pet 2:13-17", "Acts 5:29", "Dan 2:21"],
        },
    ]

    questions = []
    for item in items:
        questions.append({
            "id": item["id"],
            "category": "biblical_reference",
            "source": "Biblical Reference Accuracy",
            "question": item["question"],
            "reference_answer": f"Key passages: {', '.join(item['expected_references'])}",
            "scoring": {
                "method": "reference_check",
                "expected_references": item["expected_references"],
            },
        })

    return questions


# ---------------------------------------------------------------------------
# Category 5: Error Detection (~30 questions)
# ---------------------------------------------------------------------------

def build_error_detection() -> list[dict]:
    items = [
        # Arminianism (6)
        {
            "id": "err-arm-01",
            "statement": "God elects individuals to salvation based on His foreknowledge of their future faith and repentance.",
            "position": "reject",
            "required_points": ["Election is unconditional, not based on foreseen faith", "Faith is the result of election, not its cause"],
            "rubric": "Must reject the Arminian view of conditional election based on foreseen faith. Should affirm unconditional election per Reformed standards.",
        },
        {
            "id": "err-arm-02",
            "statement": "God's saving grace can be ultimately resisted by the free will of man.",
            "position": "reject",
            "required_points": ["Effectual grace cannot be ultimately resisted", "God's sovereign call always accomplishes its purpose"],
            "rubric": "Must reject the Arminian doctrine of resistible grace. Should affirm irresistible (effectual) grace.",
        },
        {
            "id": "err-arm-03",
            "statement": "A truly regenerate believer can fall away from grace and lose their salvation.",
            "position": "reject",
            "required_points": ["True believers cannot lose salvation", "God preserves the elect"],
            "rubric": "Must reject the possibility of losing salvation. Should affirm the perseverance and preservation of the saints.",
        },
        {
            "id": "err-arm-04",
            "statement": "Christ died equally for every individual person, intending to save all without distinction.",
            "position": "reject",
            "required_points": ["The atonement is particular and definite", "Christ died especially for the elect"],
            "rubric": "Must reject universal atonement in intent. Should affirm particular redemption while acknowledging sufficiency for all.",
        },
        {
            "id": "err-arm-05",
            "statement": "God gives prevenient grace to all people, enabling them to freely choose or reject salvation.",
            "position": "reject",
            "required_points": ["Prevenient grace as an enabling universal gift is not a Reformed doctrine", "Effectual grace is particular, not universal"],
            "rubric": "Must reject the Arminian doctrine of prevenient grace. Should distinguish effectual calling from a universal enabling grace.",
        },
        {
            "id": "err-arm-06",
            "statement": "Man has libertarian free will that allows him to choose between good and evil apart from God's determining will.",
            "position": "reject",
            "required_points": ["Fallen man's will is in bondage to sin", "True freedom comes through regeneration"],
            "rubric": "Must reject libertarian free will in the fallen state. Should affirm compatibilist freedom and the bondage of the will.",
        },
        # Roman Catholic errors (6)
        {
            "id": "err-rc-01",
            "statement": "The Pope, when speaking ex cathedra on matters of faith and morals, is infallible and his teachings are irreformable.",
            "position": "reject",
            "required_points": ["No human being is infallible", "Scripture alone is the infallible rule of faith"],
            "rubric": "Must reject papal infallibility. Should affirm Sola Scriptura as the only infallible rule.",
        },
        {
            "id": "err-rc-02",
            "statement": "Justification involves an infusion of righteousness that makes the believer inherently righteous before God.",
            "position": "reject",
            "required_points": ["Justification is a legal declaration, not an infusion", "Christ's righteousness is imputed, not infused"],
            "rubric": "Must reject the Roman Catholic doctrine of infused righteousness. Should affirm forensic justification by imputed righteousness.",
        },
        {
            "id": "err-rc-03",
            "statement": "After death, most believers must undergo purification in purgatory before entering heaven.",
            "position": "reject",
            "required_points": ["Purgatory is not a biblical doctrine", "Believers go immediately to be with Christ at death"],
            "rubric": "Must reject the doctrine of purgatory. Should affirm the immediate presence with Christ for believers at death.",
        },
        {
            "id": "err-rc-04",
            "statement": "Mary was conceived without original sin, remained sinless, and was bodily assumed into heaven.",
            "position": "reject",
            "required_points": ["The immaculate conception and assumption of Mary are unbiblical", "All humans except Christ are born in sin"],
            "rubric": "Must reject Marian dogmas (immaculate conception, perpetual sinlessness, bodily assumption). Should affirm that all have sinned (Rom 3:23).",
        },
        {
            "id": "err-rc-05",
            "statement": "In the Eucharist, the bread and wine are transformed into the actual body and blood of Christ (transubstantiation).",
            "position": "reject",
            "required_points": ["Transubstantiation is rejected by Reformed theology", "Christ is spiritually present, not physically transformed in the elements"],
            "rubric": "Must reject transubstantiation. Should articulate the Reformed view of spiritual presence in the Lord's Supper.",
        },
        {
            "id": "err-rc-06",
            "statement": "The saints in heaven can hear prayers and intercede with God on behalf of believers on earth.",
            "position": "reject",
            "required_points": ["Christ is the sole mediator", "Prayer to saints is not biblical"],
            "rubric": "Must reject the invocation of saints. Should affirm Christ as the sole mediator (1 Tim 2:5).",
        },
        # Liberal theology (6)
        {
            "id": "err-lib-01",
            "statement": "The Bible contains errors in matters of history and science, and is only authoritative in matters of faith and practice.",
            "position": "reject",
            "required_points": ["Scripture is inerrant and infallible in all it affirms", "The Bible is fully trustworthy in all matters"],
            "rubric": "Must reject limited inerrancy. Should affirm the full inerrancy and infallibility of Scripture.",
        },
        {
            "id": "err-lib-02",
            "statement": "All people will eventually be saved because a loving God would never condemn anyone to eternal punishment.",
            "position": "reject",
            "required_points": ["Universalism contradicts Scripture", "Eternal punishment is a biblical reality"],
            "rubric": "Must reject universalism. Should affirm the reality of eternal judgment and the necessity of faith in Christ.",
        },
        {
            "id": "err-lib-03",
            "statement": "The miracles recorded in the Bible should be understood as mythological or symbolic rather than as literal historical events.",
            "position": "reject",
            "required_points": ["Biblical miracles are historical events", "God is sovereign over natural law"],
            "rubric": "Must reject the demythologization of miracles. Should affirm the historical reality of biblical miracles.",
        },
        {
            "id": "err-lib-04",
            "statement": "The atonement is best understood as a moral example — Christ's death inspires us to live sacrificially rather than satisfying divine justice.",
            "position": "reject",
            "required_points": ["The moral influence theory is inadequate", "The atonement is a penal substitutionary satisfaction of divine justice"],
            "rubric": "Must reject the moral influence theory of atonement. Should affirm penal substitutionary atonement.",
        },
        {
            "id": "err-lib-05",
            "statement": "Humans are born morally neutral and become sinful only through environmental influence and personal choice.",
            "position": "reject",
            "required_points": ["Humans are born with original sin inherited from Adam", "The guilt and corruption of Adam's sin is imputed to all his posterity"],
            "rubric": "Must reject the denial of original sin. Should affirm the doctrine of inherited guilt and corruption.",
        },
        {
            "id": "err-lib-06",
            "statement": "All religions offer equally valid paths to God, and Christianity should not claim exclusivity.",
            "position": "reject",
            "required_points": ["Christ is the only way to God", "Religious pluralism contradicts Scripture"],
            "rubric": "Must reject religious pluralism. Should affirm the exclusivity of Christ (John 14:6, Acts 4:12).",
        },
        # Other errors (6)
        {
            "id": "err-oth-01",
            "statement": "God promises health, wealth, and material prosperity to all believers who have sufficient faith.",
            "position": "reject",
            "required_points": ["The prosperity gospel distorts the biblical message", "God does not promise material prosperity to all believers"],
            "rubric": "Must reject the prosperity gospel. Should affirm that God's purposes include suffering and that material prosperity is not promised.",
        },
        {
            "id": "err-oth-02",
            "statement": "Baptism is the means by which a person is regenerated and receives new spiritual life.",
            "position": "reject",
            "required_points": ["Baptism is a sign and seal, not the cause of regeneration", "Regeneration is a work of the Holy Spirit"],
            "rubric": "Must reject baptismal regeneration. Should affirm that regeneration is by the Spirit alone, with baptism as a sign.",
        },
        {
            "id": "err-oth-03",
            "statement": "A person is born again at the moment they make a personal decision to accept Christ as their Savior.",
            "position": "reject",
            "required_points": ["Regeneration precedes and enables faith", "The new birth is a sovereign act of God, not a human decision"],
            "rubric": "Must reject decisional regeneration. Should affirm that regeneration is monergistic and precedes faith.",
        },
        {
            "id": "err-oth-04",
            "statement": "Man in his natural state has the full ability to obey God and achieve righteousness without divine grace.",
            "position": "reject",
            "required_points": ["This is the heresy of Pelagianism", "Man is totally dependent on grace for any spiritual good"],
            "rubric": "Must reject Pelagianism. Should affirm total inability and the necessity of grace.",
        },
        {
            "id": "err-oth-05",
            "statement": "God does not have exhaustive foreknowledge of future free decisions; the future is partly open even to God.",
            "position": "reject",
            "required_points": ["God has exhaustive foreknowledge", "Open theism contradicts God's omniscience and sovereignty"],
            "rubric": "Must reject open theism. Should affirm God's exhaustive omniscience and sovereign decree.",
        },
        {
            "id": "err-oth-06",
            "statement": "The Son of God did not exist eternally but was the first and greatest being created by the Father.",
            "position": "reject",
            "required_points": ["The Son is eternally begotten, not made", "Arianism was condemned as heresy"],
            "rubric": "Must reject Arianism/Socinianism. Should affirm the eternal deity of the Son, begotten not made.",
        },
        # Subtle errors (6)
        {
            "id": "err-sub-01",
            "statement": "God intended the atonement for all people without exception, but its application is limited to those who believe (Amyraldism/hypothetical universalism).",
            "position": "reject",
            "required_points": ["Amyraldism introduces a universal decree of redemption that is inconsistent with particular election", "The intent and application of the atonement are both particular"],
            "rubric": "Must identify Amyraldism as departing from confessional Reformed theology. Should explain why hypothetical universalism is inconsistent with the Reformed system.",
        },
        {
            "id": "err-sub-02",
            "statement": "Covenant faithfulness, rather than imputed righteousness alone, is the instrument through which believers maintain their justified status (Federal Vision).",
            "position": "reject",
            "required_points": ["Federal Vision conflates justification and sanctification", "Justification is by imputed righteousness received through faith alone"],
            "rubric": "Must reject Federal Vision's modification of justification. Should affirm that justification is by faith alone in Christ's imputed righteousness.",
        },
        {
            "id": "err-sub-03",
            "statement": "Paul's doctrine of justification is primarily about covenant membership markers rather than how an individual is made right with God (New Perspective on Paul).",
            "position": "reject",
            "required_points": ["The New Perspective redefines justification away from its forensic meaning", "Justification addresses how sinners are declared righteous before God"],
            "rubric": "Must reject the New Perspective on Paul's redefinition of justification. Should affirm the traditional Reformed understanding of forensic justification.",
        },
        {
            "id": "err-sub-04",
            "statement": "Scripture is not directly the Word of God but becomes the Word of God in the moment of existential encounter (Barthian neo-orthodoxy).",
            "position": "reject",
            "required_points": ["Scripture is objectively the Word of God regardless of human encounter", "Neo-orthodox views undermine the objective authority of Scripture"],
            "rubric": "Must reject Barth's view that Scripture merely becomes the Word of God. Should affirm that Scripture is the Word of God objectively.",
        },
        {
            "id": "err-sub-05",
            "statement": "God's sovereignty and human freedom are reconciled through middle knowledge — God knows what every creature would freely do in any possible circumstance (Molinism).",
            "position": "reject",
            "required_points": ["Molinism's middle knowledge is not a Reformed doctrine", "Reformed theology affirms God's sovereign decree, not a decree based on counterfactual knowledge of free choices"],
            "rubric": "Must identify Molinism as incompatible with Reformed theology. Should explain why middle knowledge undermines God's sovereign decree.",
        },
        {
            "id": "err-sub-06",
            "statement": "Worship may include any practice not explicitly forbidden by Scripture (Normative Principle) rather than only what Scripture positively commands (Regulative Principle).",
            "position": "reject",
            "required_points": ["The Regulative Principle of Worship is the confessional Reformed position", "Only what God commands in worship is permitted"],
            "rubric": "Must distinguish the Regulative Principle from the Normative Principle. Should affirm that Reformed confessions teach the RPW (WCF 21.1).",
        },
    ]

    questions = []
    for item in items:
        questions.append({
            "id": item["id"],
            "category": "error_detection",
            "source": "Error Detection — Theological Discernment",
            "question": f"Evaluate this statement from a Reformed perspective: \"{item['statement']}\"",
            "reference_answer": " ".join(item["required_points"]),
            "scoring": {
                "method": "position_detection",
                "position": item["position"],
                "required_points": item["required_points"],
                "rubric": item["rubric"],
            },
        })

    return questions


# ---------------------------------------------------------------------------
# Category 6: Comparative Theology (~20 questions)
# ---------------------------------------------------------------------------

def build_comparative_theology() -> list[dict]:
    items = [
        # Reformed vs Roman Catholic (4)
        {
            "id": "comp-rc-01",
            "question": "How does Reformed soteriology differ from Roman Catholic soteriology?",
            "rubric": "Must contrast forensic justification by faith alone (Reformed) with infused righteousness and faith plus works (RC). Should mention sola fide, imputation vs. infusion, merit, and the role of sacraments in salvation.",
        },
        {
            "id": "comp-rc-02",
            "question": "How do Reformed and Roman Catholic ecclesiologies differ?",
            "rubric": "Must contrast the marks of the true church (Word, sacraments, discipline) with papal authority and apostolic succession. Should address the visible/invisible church distinction and the role of the papacy.",
        },
        {
            "id": "comp-rc-03",
            "question": "How do Reformed and Roman Catholic views of the sacraments differ?",
            "rubric": "Must contrast two sacraments (baptism, Lord's Supper) with seven sacraments. Should address spiritual presence vs. transubstantiation, the efficacy of sacraments, and ex opere operato.",
        },
        {
            "id": "comp-rc-04",
            "question": "How do Reformed and Roman Catholic views of Scripture and tradition differ?",
            "rubric": "Must contrast Sola Scriptura with the Roman Catholic two-source theory. Should address the sufficiency of Scripture, the role of the magisterium, and the relationship between Scripture and tradition.",
        },
        # Reformed vs Arminian (4)
        {
            "id": "comp-arm-01",
            "question": "How do Reformed and Arminian views of election differ?",
            "rubric": "Must contrast unconditional election (Reformed) with conditional election based on foreseen faith (Arminian). Should reference Eph 1:4-5, Rom 9:11-13, and the Canons of Dort.",
        },
        {
            "id": "comp-arm-02",
            "question": "How do Reformed and Arminian views of the atonement differ?",
            "rubric": "Must contrast particular redemption (Reformed) with universal atonement (Arminian). Should address the intent and efficacy of Christ's death and the distinction between sufficient for all, efficient for the elect.",
        },
        {
            "id": "comp-arm-03",
            "question": "How do Reformed and Arminian views of grace differ?",
            "rubric": "Must contrast irresistible/effectual grace (Reformed) with prevenient/resistible grace (Arminian). Should address monergism vs. synergism in regeneration.",
        },
        {
            "id": "comp-arm-04",
            "question": "How do Reformed and Arminian views of perseverance differ?",
            "rubric": "Must contrast perseverance of the saints (Reformed) with the possibility of apostasy (Arminian). Should address God's preservation vs. conditional security.",
        },
        # Reformed vs Lutheran (3)
        {
            "id": "comp-luth-01",
            "question": "How do Reformed and Lutheran views of the Lord's Supper differ?",
            "rubric": "Must contrast spiritual presence (Reformed) with sacramental union / real presence in, with, and under the elements (Lutheran). Should address Calvin's view vs. Luther's view and the rejection of transubstantiation by both.",
        },
        {
            "id": "comp-luth-02",
            "question": "How do Reformed and Lutheran views of law and gospel differ?",
            "rubric": "Must contrast the Reformed three uses of the law (including the third use as a guide for believers) with the Lutheran emphasis on the law-gospel dialectic. Should address the role of the law in the Christian life.",
        },
        {
            "id": "comp-luth-03",
            "question": "How do Reformed and Lutheran views of predestination differ?",
            "rubric": "Must contrast double predestination (Reformed) with single predestination (Lutheran). Should address the Lutheran rejection of reprobation and the Reformed affirmation of God's sovereign decree over both election and reprobation.",
        },
        # Reformed vs Baptist (3)
        {
            "id": "comp-bapt-01",
            "question": "How do Reformed paedobaptist and Baptist views of baptism differ?",
            "rubric": "Must contrast infant baptism as a covenant sign (paedobaptist) with believer's baptism only (Baptist). Should address covenant theology, the relationship of baptism to circumcision, and the nature of the covenant community.",
        },
        {
            "id": "comp-bapt-02",
            "question": "How do covenant theology and Baptist covenant theology differ?",
            "rubric": "Must contrast WCF covenant theology (one covenant of grace with different administrations) with 1689 Federalism or New Covenant Theology. Should address the continuity/discontinuity of the covenants and the nature of the new covenant community.",
        },
        {
            "id": "comp-bapt-03",
            "question": "How do Presbyterian and Baptist views of church polity differ?",
            "rubric": "Must contrast Presbyterian connectionalism (sessions, presbyteries, general assemblies) with Baptist congregational autonomy. Should address the authority of elders, the role of denominational structures, and local church independence.",
        },
        # Reformed vs Dispensationalist (3)
        {
            "id": "comp-disp-01",
            "question": "How do covenant theology and dispensationalism differ?",
            "rubric": "Must contrast the overarching covenants (works, grace, redemption) with distinct dispensational epochs. Should address the unity of the people of God vs. the Israel/Church distinction.",
        },
        {
            "id": "comp-disp-02",
            "question": "How do Reformed and dispensationalist views of Israel and the Church differ?",
            "rubric": "Must contrast the Reformed view that the Church is the continuation of Israel with the dispensationalist distinction between Israel and the Church as separate peoples of God. Should address the fulfillment of OT promises.",
        },
        {
            "id": "comp-disp-03",
            "question": "How do Reformed and dispensationalist eschatologies differ?",
            "rubric": "Must contrast amillennialism or postmillennialism (common Reformed views) with premillennial dispensationalism. Should address the millennium, the rapture, and the interpretation of Revelation.",
        },
        # Reformed vs Eastern Orthodox (3)
        {
            "id": "comp-eo-01",
            "question": "How do Reformed and Eastern Orthodox views of salvation differ?",
            "rubric": "Must contrast forensic justification and monergistic salvation (Reformed) with theosis/deification and synergistic cooperation with grace (EO). Should address the nature of salvation, the role of human effort, and the meaning of union with God.",
        },
        {
            "id": "comp-eo-02",
            "question": "How do Reformed and Eastern Orthodox views of theosis differ from the Reformed doctrine of sanctification?",
            "rubric": "Must contrast Orthodox theosis (participation in the divine nature/energies) with Reformed sanctification (progressive conformity to Christ's image by the Spirit). Should address the Creator-creature distinction.",
        },
        {
            "id": "comp-eo-03",
            "question": "How do Reformed and Eastern Orthodox views of tradition and authority differ?",
            "rubric": "Must contrast Sola Scriptura (Reformed) with Sacred Tradition as a co-equal source of authority (EO). Should address the role of ecumenical councils, church fathers, and the relationship between Scripture and tradition.",
        },
    ]

    questions = []
    for item in items:
        questions.append({
            "id": item["id"],
            "category": "comparative_theology",
            "source": "Comparative Theology",
            "question": item["question"],
            "reference_answer": item["rubric"],
            "scoring": {
                "method": "llm_judge",
                "rubric": item["rubric"],
            },
        })

    return questions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    benchmark = {
        "version": "1.0",
        "categories": {
            "catechism_recall": {
                "description": "Direct recall of catechism Q&A from Reformed confessional standards",
                "weight": 0.25,
            },
            "confessional_knowledge": {
                "description": "Knowledge of what Reformed confessions teach on specific topics",
                "weight": 0.15,
            },
            "doctrinal_position": {
                "description": "Correct doctrinal positions on TULIP, Five Solas, and key Reformed distinctives",
                "weight": 0.20,
            },
            "biblical_reference": {
                "description": "Ability to cite accurate and relevant Scripture references for doctrines",
                "weight": 0.15,
            },
            "error_detection": {
                "description": "Ability to identify and refute heterodox theological statements",
                "weight": 0.15,
            },
            "comparative_theology": {
                "description": "Understanding distinctions between Reformed theology and other traditions",
                "weight": 0.10,
            },
        },
        "questions": [],
    }

    builders = [
        ("catechism_recall", build_catechism_recall),
        ("confessional_knowledge", build_confessional_knowledge),
        ("doctrinal_position", build_doctrinal_position),
        ("biblical_reference", build_biblical_reference),
        ("error_detection", build_error_detection),
        ("comparative_theology", build_comparative_theology),
    ]

    for category_name, builder_fn in builders:
        questions = builder_fn()
        benchmark["questions"].extend(questions)
        print(f"  {category_name}: {len(questions)} questions")

    total = len(benchmark["questions"])
    print(f"\nTotal: {total} questions")

    # Validate category weights sum to 1.0
    weights = sum(c["weight"] for c in benchmark["categories"].values())
    assert abs(weights - 1.0) < 1e-9, f"Category weights sum to {weights}, expected 1.0"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    print(f"\nBenchmark written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
