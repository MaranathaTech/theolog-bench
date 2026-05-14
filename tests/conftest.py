import pytest


@pytest.fixture
def catechism_question():
    """A sample catechism_recall question."""
    return {
        "id": "wsc-001",
        "category": "catechism_recall",
        "source": "Westminster Shorter Catechism Q1",
        "question": "What is the chief end of man?",
        "reference_answer": "Man's chief end is to glorify God, and to enjoy him for ever.",
        "scoring": {
            "method": "semantic_similarity",
            "required_phrases": ["glorify God", "enjoy him"],
            "key_concepts": ["God's glory", "enjoyment of God"],
        },
    }


@pytest.fixture
def position_question_deny():
    """A doctrinal_position question expecting denial."""
    return {
        "id": "tulip-p-01",
        "category": "doctrinal_position",
        "source": "TULIP - Perseverance of the Saints",
        "question": "Can a true believer lose their salvation?",
        "expected_position": "deny",
        "reference_answer": "No. Those whom God has elected and effectually called cannot fall away from grace.",
        "scoring": {
            "method": "position_detection",
            "position": "deny",
            "required_points": ["God's sovereign keeping", "perseverance"],
            "key_references": ["John 10:28-29", "Romans 8:38-39"],
            "heterodox_flags": [
                "can fall away",
                "lose salvation",
                "conditional security",
            ],
        },
    }


@pytest.fixture
def position_question_affirm():
    """A doctrinal_position question expecting affirmation."""
    return {
        "id": "sola-scriptura-01",
        "category": "doctrinal_position",
        "source": "Five Solas - Sola Scriptura",
        "question": "Is the Bible the sole infallible rule of faith and practice?",
        "expected_position": "affirm",
        "reference_answer": "Yes. Scripture alone is the infallible rule of faith.",
        "scoring": {
            "method": "position_detection",
            "position": "affirm",
            "required_points": ["Scripture alone", "infallible"],
            "key_references": ["2 Timothy 3:16-17"],
            "heterodox_flags": [
                "tradition holds equal authority",
                "church above Scripture",
            ],
        },
    }


@pytest.fixture
def reference_question():
    """A biblical_reference question."""
    return {
        "id": "ref-elect-01",
        "category": "biblical_reference",
        "source": "Election",
        "question": "What Bible passages teach the doctrine of election?",
        "reference_answer": "Key passages include Ephesians 1:4-5 and Romans 8:29-30.",
        "scoring": {
            "method": "reference_check",
            "expected_references": [
                "Ephesians 1:4-5",
                "Romans 8:29-30",
                "Romans 9:11-13",
            ],
        },
    }


@pytest.fixture
def error_detection_question():
    """An error_detection question expecting rejection."""
    return {
        "id": "err-arm-01",
        "category": "error_detection",
        "source": "Arminianism",
        "question": "Evaluate this statement from a Reformed perspective: 'God chose to save those whom He foresaw would choose Him.'",
        "expected_position": "reject",
        "scoring": {
            "method": "position_detection",
            "position": "reject",
            "required_points": ["unconditional election", "God's sovereign choice"],
            "rubric": "Must identify this as Arminian. Must contrast with unconditional election.",
            "heterodox_flags": ["foresaw would choose", "foreseen faith"],
        },
    }


@pytest.fixture
def judge_question():
    """A confessional_knowledge question scored by judge."""
    return {
        "id": "wcf-ch01",
        "category": "confessional_knowledge",
        "source": "Westminster Confession of Faith, Chapter 1",
        "question": "What does the Westminster Confession of Faith teach about Holy Scripture?",
        "reference_answer": "The WCF teaches that Holy Scripture is most necessary, being the Word of God written.",
        "scoring": {
            "method": "llm_judge",
            "rubric": "Must reference the sufficiency and necessity of Scripture.",
        },
    }


@pytest.fixture
def sample_results():
    """A complete results dict for report testing."""
    return {
        "model_name": "test-model",
        "timestamp": "2026-05-12T12:00:00",
        "category_weights": {
            "catechism_recall": 0.25,
            "confessional_knowledge": 0.15,
            "doctrinal_position": 0.20,
            "biblical_reference": 0.15,
            "error_detection": 0.15,
            "comparative_theology": 0.10,
        },
        "questions": [
            {
                "id": "wsc-001",
                "category": "catechism_recall",
                "question": "What is the chief end of man?",
                "score": 95,
                "score_details": {},
            },
            {
                "id": "wsc-002",
                "category": "catechism_recall",
                "question": "What rule hath God given?",
                "score": 80,
                "score_details": {},
            },
            {
                "id": "wcf-ch01",
                "category": "confessional_knowledge",
                "question": "What does the WCF teach?",
                "score": 70,
                "score_details": {},
            },
            {
                "id": "tulip-p-01",
                "category": "doctrinal_position",
                "question": "Can a believer lose salvation?",
                "score": 100,
                "score_details": {},
            },
            {
                "id": "ref-elect-01",
                "category": "biblical_reference",
                "question": "Passages on election?",
                "score": 60,
                "score_details": {},
            },
            {
                "id": "err-arm-01",
                "category": "error_detection",
                "question": "Evaluate Arminian statement",
                "score": 85,
                "score_details": {},
            },
            {
                "id": "comp-rc-01",
                "category": "comparative_theology",
                "question": "Reformed vs Catholic?",
                "score": 30,
                "score_details": {},
            },
        ],
        "results_path": "results/test-model_20260512.json",
    }
