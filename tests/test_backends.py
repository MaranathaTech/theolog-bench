"""Unit tests for lib/backends.py (OpenAI client mocked, no UnslothBackend)."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


def _make_mock_openai(mock_client=None):
    """Create a MagicMock to stand in for the openai.OpenAI constructor."""
    mock = MagicMock()
    if mock_client is not None:
        mock.return_value = mock_client
    return mock


class TestAPIBackendGenerate:
    def test_api_backend_generate(self):
        """APIBackend.generate() calls the OpenAI client correctly."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "  Test response  "
        mock_client.chat.completions.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_client) as MockOpenAI:
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url="http://localhost:11434/v1", model="test-model"
            )
            result = backend.generate("Test question")

            assert result == "Test response"
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "test-model"
            assert call_kwargs["temperature"] == 0.3
            assert call_kwargs["messages"][0]["content"] == "Test question"

    def test_api_backend_name(self):
        """APIBackend.name() returns the model name."""
        with patch("openai.OpenAI"):
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url="http://localhost:11434/v1", model="qwen3:8b"
            )
            assert backend.name() == "qwen3:8b"

    def test_api_backend_picks_up_env_var(self):
        """APIBackend reads OPENROUTER_API_KEY from environment."""
        with patch("openai.OpenAI") as MockOpenAI, patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key-123", "OPENAI_API_KEY": ""},
            clear=False,
        ):
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url="https://openrouter.ai/api/v1", model="test"
            )
            call_kwargs = MockOpenAI.call_args[1]
            assert call_kwargs["api_key"] == "test-key-123"

    def test_api_backend_explicit_key_overrides_env(self):
        """Explicit api_key takes precedence over env var."""
        with patch("openai.OpenAI") as MockOpenAI, patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "env-key"},
            clear=False,
        ):
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url="https://openrouter.ai/api/v1",
                model="test",
                api_key="explicit-key",
            )
            call_kwargs = MockOpenAI.call_args[1]
            assert call_kwargs["api_key"] == "explicit-key"

    def test_api_backend_default_max_tokens(self):
        """APIBackend uses max_tokens=512 by default."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "response"
        mock_client.chat.completions.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_client):
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url="http://localhost:11434/v1", model="test"
            )
            backend.generate("question")

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["max_tokens"] == 512

    def test_api_backend_no_key_uses_fallback(self):
        """APIBackend uses 'not-needed' when no key is provided or in env."""
        with patch("openai.OpenAI") as MockOpenAI, patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url="http://localhost:11434/v1", model="test"
            )
            call_kwargs = MockOpenAI.call_args[1]
            assert call_kwargs["api_key"] == "not-needed"
