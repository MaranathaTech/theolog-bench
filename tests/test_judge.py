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

    def test_should_not_use_judge_for_catechism(self, catechism_question):
        """should_use_judge returns False for catechism_recall."""
        assert should_use_judge(catechism_question) is False

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
