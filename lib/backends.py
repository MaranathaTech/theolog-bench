"""Model backends for theolog-bench."""

import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class BenchmarkAPIError(Exception):
    """API error during benchmark execution."""

    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class ModelBackend(ABC):
    @abstractmethod
    def generate(self, question: str) -> str:
        """Send a question to the model and return its response."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Return a human-readable name for this backend/model."""
        ...


class UnslothBackend(ModelBackend):
    """Local model via Unsloth/FastLanguageModel."""

    def __init__(self, model_path: str, max_seq_length: int = 1024,
                 temperature: float = 0.3, max_new_tokens: int = 512):
        from unsloth import FastLanguageModel
        from unsloth.chat_templates import get_chat_template

        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self._model_path = model_path

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_path,
            max_seq_length=max_seq_length,
            load_in_4bit=True,
        )

        self.tokenizer = get_chat_template(
            self.tokenizer,
            chat_template="chatml",
            mapping={
                "role": "from",
                "content": "value",
                "user": "human",
                "assistant": "gpt",
            },
            map_eos_token=True,
        )

        FastLanguageModel.for_inference(self.model)

    def generate(self, question: str) -> str:
        messages = [{"role": "user", "content": question}]
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(
            input_ids=inputs,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=0.9,
            do_sample=True,
            use_cache=True,
        )

        response = self.tokenizer.decode(
            outputs[0][inputs.shape[-1]:], skip_special_tokens=True
        )
        return response.strip()

    def name(self) -> str:
        return Path(self._model_path).name


class APIBackend(ModelBackend):
    """OpenAI-compatible API backend (Ollama, OpenRouter, OpenAI, etc.)."""

    def __init__(self, api_url: str, model: str, api_key: str = None,
                 temperature: float = 0.3, max_tokens: int = 512):
        from openai import OpenAI

        self._model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Check env var if no explicit key
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")

        self.client = OpenAI(
            base_url=api_url,
            api_key=api_key or "not-needed",
        )

    def generate(self, question: str) -> str:
        import openai

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": question}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                if not response.choices:
                    return ""
                content = response.choices[0].message.content
                if content is None:
                    return ""
                return content.strip()
            except openai.AuthenticationError as e:
                raise BenchmarkAPIError(
                    f"Authentication failed: {e}", retryable=False
                ) from e
            except openai.RateLimitError as e:
                # Check for retry-after header (must be before APIStatusError
                # since RateLimitError is a subclass of APIStatusError)
                retry_after = None
                if hasattr(e, "response") and e.response is not None:
                    retry_after_val = e.response.headers.get("retry-after")
                    if retry_after_val:
                        try:
                            retry_after = float(retry_after_val)
                        except (ValueError, TypeError):
                            pass
                if retry_after is not None:
                    delay = retry_after
                else:
                    delay = min(2 ** (attempt + 1), 60)
                logger.warning(
                    "Rate limited (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1, max_retries, delay, e,
                )
                time.sleep(delay)
                continue
            except openai.APIStatusError as e:
                if e.status_code == 402:
                    raise BenchmarkAPIError(
                        f"Credit exhaustion (402): {e}", retryable=False
                    ) from e
                if e.status_code >= 500:
                    # Server error — retryable
                    pass
                else:
                    raise BenchmarkAPIError(
                        f"API error ({e.status_code}): {e}", retryable=False
                    ) from e
            except (openai.APITimeoutError, openai.APIConnectionError) as e:
                delay = min(2 ** (attempt + 1), 60)
                logger.warning(
                    "Transient error (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1, max_retries, delay, e,
                )
                time.sleep(delay)
                continue

            # Reached here from 5xx server error fallthrough
            delay = min(2 ** (attempt + 1), 60)
            logger.warning(
                "Server error (attempt %d/%d), retrying in %.1fs",
                attempt + 1, max_retries, delay,
            )
            time.sleep(delay)

        raise BenchmarkAPIError(
            f"Max retries ({max_retries}) exhausted for model {self._model}",
            retryable=True,
        )

    def name(self) -> str:
        return self._model
