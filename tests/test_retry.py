"""Unit tests for retry logic in lib/backends.py and judge fallback in lib/judge.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.backends import BenchmarkAPIError


def _make_api_backend():
    """Create an APIBackend with a mocked OpenAI client."""
    with patch("openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        from lib.backends import APIBackend

        backend = APIBackend(
            api_url="http://localhost:11434/v1", model="test-model"
        )
    return backend


def _make_success_response(content="Test response"):
    """Create a mock successful API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


class TestRetrySucceedsAfterTransientErrors:
    def test_retry_succeeds_after_rate_limit(self):
        """APIBackend.generate() retries on RateLimitError and succeeds."""
        import openai

        backend = _make_api_backend()

        # Build a RateLimitError
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.headers = {}
        rate_limit_error = openai.RateLimitError(
            message="Rate limited",
            response=mock_resp,
            body=None,
        )

        backend.client.chat.completions.create.side_effect = [
            rate_limit_error,
            rate_limit_error,
            _make_success_response("Success after retries"),
        ]

        with patch("time.sleep"):
            result = backend.generate("Test question")

        assert result == "Success after retries"
        assert backend.client.chat.completions.create.call_count == 3


class TestHardErrorRaisesImmediately:
    def test_auth_error_raises_immediately(self):
        """AuthenticationError raises BenchmarkAPIError(retryable=False) after 1 call."""
        import openai

        backend = _make_api_backend()

        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.headers = {}
        auth_error = openai.AuthenticationError(
            message="Invalid API key",
            response=mock_resp,
            body=None,
        )

        backend.client.chat.completions.create.side_effect = auth_error

        with pytest.raises(BenchmarkAPIError) as exc_info:
            backend.generate("Test question")

        assert exc_info.value.retryable is False
        assert backend.client.chat.completions.create.call_count == 1


class TestCreditExhaustionRaisesImmediately:
    def test_402_raises_immediately(self):
        """402 status raises BenchmarkAPIError(retryable=False) after 1 call."""
        import openai

        backend = _make_api_backend()

        mock_resp = MagicMock()
        mock_resp.status_code = 402
        mock_resp.headers = {}
        status_error = openai.APIStatusError(
            message="Payment required",
            response=mock_resp,
            body=None,
        )

        backend.client.chat.completions.create.side_effect = status_error

        with pytest.raises(BenchmarkAPIError) as exc_info:
            backend.generate("Test question")

        assert exc_info.value.retryable is False
        assert backend.client.chat.completions.create.call_count == 1


class TestMaxRetriesExhausted:
    def test_max_retries_exhausted(self):
        """After 5 RateLimitErrors, raises BenchmarkAPIError(retryable=True)."""
        import openai

        backend = _make_api_backend()

        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.headers = {}
        rate_limit_error = openai.RateLimitError(
            message="Rate limited",
            response=mock_resp,
            body=None,
        )

        backend.client.chat.completions.create.side_effect = rate_limit_error

        with patch("time.sleep"), pytest.raises(BenchmarkAPIError) as exc_info:
            backend.generate("Test question")

        assert exc_info.value.retryable is True
        assert backend.client.chat.completions.create.call_count == 5


class TestJudgeReturnsfallbackOnError:
    def test_judge_returns_fallback_on_error(self, judge_question):
        """JudgeScorer.score() returns score 0 with error flag instead of raising."""
        from lib.judge import JudgeScorer

        mock_backend = MagicMock()
        mock_backend.generate.side_effect = BenchmarkAPIError(
            "Credit exhaustion", retryable=False
        )

        judge = JudgeScorer(backend=mock_backend)
        result = judge.score(judge_question, "Some response")

        assert result["score"] == 0
        assert result["method"] == "llm_judge"
        assert result["details"]["error"] is True
        assert "Credit exhaustion" in result["details"]["justification"]
