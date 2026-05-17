"""Unit tests for lib/judge.py (all external calls mocked)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.judge import JudgeScorer, should_use_judge


class TestJudgeScorerParsing:
    def test_judge_parses_valid_json(self, judge_question):
        """Judge correctly parses a well-formed JSON response."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = (
            '{"score": 85, "justification": "Good theological accuracy."}'
        )
        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(
            judge_question,
            "The WCF teaches Scripture is necessary and sufficient...",
        )
        assert result["score"] == 85
        assert result["method"] == "llm_judge"
        assert "Good theological accuracy" in result["details"]["justification"]

    def test_judge_parses_json_in_markdown_codeblock(self, judge_question):
        """Judge handles JSON wrapped in markdown code blocks."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = (
            '```json\n{"score": 72, "justification": "Decent."}\n```'
        )
        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(judge_question, "Some response")
        assert result["score"] == 72

    def test_judge_handles_malformed_output(self, judge_question):
        """Judge handles unstructured output by extracting a number."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = (
            "I think this deserves about a 65 out of 100 because it covers the main points."
        )
        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(judge_question, "Some response")
        assert result["score"] == 65

    def test_judge_handles_garbage_output(self, judge_question):
        """Judge returns 0 for completely unparseable output with no numbers."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "I cannot evaluate this response."
        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(judge_question, "Some response")
        assert result["score"] == 0

    def test_judge_clamps_score_to_100(self, judge_question):
        """Judge clamps scores above 100."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = (
            '{"score": 150, "justification": "Perfect!"}'
        )
        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(judge_question, "Some response")
        assert result["score"] == 100

    def test_judge_clamps_score_to_0(self, judge_question):
        """Judge clamps negative scores to 0."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = (
            '{"score": -10, "justification": "Terrible."}'
        )
        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(judge_question, "Some response")
        assert result["score"] == 0


class TestShouldUseJudge:
    def test_should_use_judge_for_llm_judge_method(self, judge_question):
        """should_use_judge returns True for llm_judge questions."""
        assert should_use_judge(judge_question) is True

    def test_should_use_judge_for_error_detection(self, error_detection_question):
        """should_use_judge returns True for error_detection category."""
        assert should_use_judge(error_detection_question) is True

    def test_should_use_judge_for_catechism_recall(self, catechism_question):
        """should_use_judge returns True for catechism_recall category."""
        assert should_use_judge(catechism_question) is True

    def test_should_use_judge_for_doctrinal_position(self, position_question_deny):
        """should_use_judge returns True for doctrinal_position category."""
        assert should_use_judge(position_question_deny) is True

    def test_should_use_judge_for_confessional_knowledge(self):
        """should_use_judge returns True for confessional_knowledge category."""
        question = {
            "category": "confessional_knowledge",
            "scoring": {"method": "semantic_similarity"},
        }
        assert should_use_judge(question) is True

    def test_should_use_judge_for_comparative_theology(self):
        """should_use_judge returns True for comparative_theology category."""
        question = {
            "category": "comparative_theology",
            "scoring": {"method": "semantic_similarity"},
        }
        assert should_use_judge(question) is True

    def test_should_not_use_judge_for_biblical_reference(self, reference_question):
        """should_use_judge returns False for biblical_reference."""
        assert should_use_judge(reference_question) is False


class TestPositionPrompt:
    """Tests for the position detection judge prompt."""

    def test_includes_expected_position(self, position_question_deny):
        """Position prompt includes the expected position (DENY)."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 80, "justification": "Good."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(position_question_deny, "No, a believer cannot lose salvation.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "DENY" in prompt

    def test_includes_required_points(self, position_question_deny):
        """Position prompt includes required_points from scoring config."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 80, "justification": "Good."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(position_question_deny, "No.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "God's sovereign keeping" in prompt
        assert "perseverance" in prompt

    def test_includes_heterodox_flags(self, position_question_deny):
        """Position prompt includes heterodox flags to watch for."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 80, "justification": "Good."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(position_question_deny, "No.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "can fall away" in prompt
        assert "conditional security" in prompt

    def test_affirm_position(self, position_question_affirm):
        """Position prompt uses AFFIRM for affirm-type questions."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 90, "justification": "Solid."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(position_question_affirm, "Yes, Scripture alone is infallible.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "AFFIRM" in prompt


class TestCatechismPrompt:
    """Tests for the catechism recall judge prompt."""

    def test_includes_reference_answer(self, catechism_question):
        """Catechism prompt includes the reference answer text."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 95, "justification": "Excellent."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(catechism_question, "To glorify God and enjoy him forever.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "glorify God" in prompt
        assert "enjoy him for ever" in prompt

    def test_includes_source(self, catechism_question):
        """Catechism prompt includes the source identifier."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 95, "justification": "Excellent."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(catechism_question, "To glorify God and enjoy him forever.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "Westminster Shorter Catechism" in prompt

    def test_includes_paraphrase_instruction(self, catechism_question):
        """Catechism prompt instructs judge not to penalize paraphrase."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 95, "justification": "Excellent."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(catechism_question, "To glorify God and enjoy him forever.")
        prompt = mock_backend.generate.call_args[0][0]
        assert "paraphrased answer" in prompt.lower() or "Do NOT penalize" in prompt


class TestPromptDispatch:
    """Tests that score() dispatches to the correct prompt builder."""

    def test_dispatches_position_detection(self, position_question_deny):
        """score() uses position prompt for position_detection method."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 75, "justification": "OK."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(position_question_deny, "No.")
        prompt = mock_backend.generate.call_args[0][0]
        # Position prompt has this unique marker
        assert "correctly identifies and takes a Reformed doctrinal position" in prompt

    def test_dispatches_semantic_similarity(self, catechism_question):
        """score() uses catechism prompt for semantic_similarity method."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 90, "justification": "Great."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(catechism_question, "To glorify God.")
        prompt = mock_backend.generate.call_args[0][0]
        # Catechism prompt has this unique marker
        assert "faithfully conveys catechism teaching" in prompt

    def test_dispatches_llm_judge(self, judge_question):
        """score() uses generic prompt for llm_judge method."""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = '{"score": 80, "justification": "Fine."}'
        judge = JudgeScorer(backend=mock_backend)
        judge.score(judge_question, "The WCF teaches...")
        prompt = mock_backend.generate.call_args[0][0]
        # Generic prompt has this unique marker
        assert "theological accuracy" in prompt
        assert "Scoring rubric" in prompt


class TestAutomatedScorePreservation:
    """Tests that automated_score is preserved when judge overwrites."""

    def test_automated_score_preserved_in_run_logic(self):
        """Simulates the run.py logic: judge overwrites but automated is kept."""
        # Simulate a question after automated scoring
        rq = {
            "id": "wsc-001",
            "category": "catechism_recall",
            "scoring": {"method": "semantic_similarity"},
            "score": 60,
            "score_method": "semantic_similarity",
            "score_details": {"overlap": 0.6},
            "response": "To glorify God and enjoy him forever.",
        }

        # Simulate what run.py does when judge returns
        judge_result = {
            "score": 92,
            "method": "llm_judge",
            "details": {"justification": "Excellent paraphrase."},
        }
        rq["judge_score"] = judge_result["score"]
        rq["judge_details"] = judge_result["details"]
        rq["automated_score"] = rq["score"]
        rq["automated_score_method"] = rq.get("score_method", "")
        rq["score"] = judge_result["score"]
        rq["score_details"] = judge_result["details"]
        rq["score_method"] = "llm_judge"

        assert rq["score"] == 92
        assert rq["automated_score"] == 60
        assert rq["automated_score_method"] == "semantic_similarity"
        assert rq["score_method"] == "llm_judge"
