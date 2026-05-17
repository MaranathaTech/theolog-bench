"""LLM-as-judge scoring for theolog-bench.

Handles categories requiring nuanced theological evaluation:
confessional_knowledge, comparative_theology, and error_detection quality checks.
Uses an APIBackend to call a judge LLM (configured in config.yaml).
"""

import json
import logging
import re
from pathlib import Path

import yaml

# Categories that benefit from judge scoring
_JUDGE_CATEGORIES = {
    "confessional_knowledge",
    "comparative_theology",
    "error_detection",
    "doctrinal_position",
    "catechism_recall",
}


class JudgeScorer:
    """LLM-as-judge for nuanced theological evaluation."""

    def __init__(self, backend=None, config_path: str = None):
        """Initialize the judge.

        If backend is not provided, create one from config.yaml settings.
        """
        if backend is None:
            config_path = config_path or str(
                Path(__file__).parent.parent / "config.yaml"
            )
            with open(config_path) as f:
                config = yaml.safe_load(f)
            judge_cfg = config.get("judge", {})
            from lib.backends import APIBackend

            backend = APIBackend(
                api_url=judge_cfg.get("api_url", "https://openrouter.ai/api/v1"),
                model=judge_cfg.get("model", "google/gemini-2.5-flash"),
                api_key=judge_cfg.get("api_key"),
            )
        self.backend = backend

    def score(self, question: dict, response: str) -> dict:
        """Score a response using the judge LLM."""
        from lib.scorer import strip_think_blocks
        response = strip_think_blocks(response)

        method = question.get("scoring", {}).get("method", "")
        if method == "position_detection":
            prompt = self._build_position_prompt(question, response)
        elif method == "semantic_similarity":
            prompt = self._build_catechism_prompt(question, response)
        else:
            prompt = self._build_prompt(question, response)
        try:
            raw_output = self.backend.generate(prompt)
        except Exception as e:
            logging.getLogger(__name__).warning(
                "Judge call failed for %s: %s", question.get("id", "?"), e
            )
            return {
                "score": 0,
                "method": "llm_judge",
                "details": {
                    "justification": f"Judge call failed: {e}",
                    "raw_output": "",
                    "error": True,
                },
            }
        return self._parse_output(raw_output)

    def _build_prompt(self, question: dict, response: str) -> str:
        """Build the judge prompt."""
        source = question.get("source", "Unknown")
        reference = question.get("reference_answer", "")
        rubric = question.get("scoring", {}).get(
            "rubric",
            "Evaluate theological accuracy and alignment with Reformed confessional standards.",
        )

        return (
            "You are a Reformed theology expert evaluating an AI model's response "
            "for theological accuracy.\n\n"
            f"Question asked: {question['question']}\n"
            f"Expected answer source: {source}\n"
            f"Reference text: {reference}\n"
            f"Scoring rubric: {rubric}\n\n"
            f"Model's response:\n{response}\n\n"
            "Score this response 0-100 on theological accuracy and alignment with "
            "Reformed confessional standards.\n"
            "Consider:\n"
            "- Accuracy: Does the response correctly represent the confessional/biblical teaching?\n"
            "- Completeness: Does it cover the key points from the reference text?\n"
            "- Orthodoxy: Does it avoid heterodox statements?\n"
            "- Clarity: Is the theological explanation clear and well-organized?\n\n"
            'You MUST respond with ONLY a JSON object, no other text:\n'
            '{"score": <0-100>, "justification": "<brief 1-2 sentence explanation>"}'
        )

    def _build_position_prompt(self, question: dict, response: str) -> str:
        """Build a judge prompt for position detection (doctrinal_position / error_detection)."""
        expected = question.get("scoring", {}).get("expected_position") or question.get("scoring", {}).get("position", "")
        required_points = question.get("scoring", {}).get("required_points", [])
        heterodox_flags = question.get("scoring", {}).get("heterodox_flags", [])

        prompt = (
            "You are a Reformed theology expert evaluating whether an AI model "
            "correctly identifies and takes a Reformed doctrinal position.\n\n"
            f"Question: {question['question']}\n"
            f"Expected position: The model should clearly {expected.upper()} this statement.\n"
        )
        if required_points:
            prompt += f"Key points the model should make: {'; '.join(required_points)}\n"
        if heterodox_flags:
            prompt += f"Heterodox elements to reject: {', '.join(heterodox_flags)}\n"
        prompt += (
            f"\nModel's response:\n{response}\n\n"
            "Score 0-100 based on:\n"
            "- Does the model clearly take the correct position (affirm/deny as expected)? (50 points)\n"
            "- Does it explain WHY this is the Reformed position with theological depth? (30 points)\n"
            "- Does it address the required points? (20 points)\n"
            "A model that presents a balanced academic comparison but clearly concludes "
            "with the correct Reformed position should score well.\n"
            "A model that hedges without committing to the correct position should score lower.\n\n"
            'Respond with ONLY a JSON object:\n'
            '{"score": <0-100>, "justification": "<brief explanation>"}'
        )
        return prompt

    def _build_catechism_prompt(self, question: dict, response: str) -> str:
        """Build a judge prompt for catechism recall (semantic similarity questions)."""
        reference = question.get("reference_answer", "")
        source = question.get("source", "Unknown")

        return (
            "You are a Reformed theology expert evaluating whether an AI model "
            "faithfully conveys catechism teaching.\n\n"
            f"Question: {question['question']}\n"
            f"Source: {source}\n"
            f"Reference answer (exact catechism text):\n{reference}\n\n"
            f"Model's response:\n{response}\n\n"
            "Score 0-100 based on:\n"
            "- Does the response convey the SAME theological content as the reference? (60 points)\n"
            "- Does it cover ALL key doctrinal points from the reference? (30 points)\n"
            "- Is it theologically accurate with no errors? (10 points)\n\n"
            "IMPORTANT: A paraphrased answer that captures all key doctrinal points "
            "should score just as high as a verbatim quotation. Do NOT penalize for "
            "using different words if the theological substance is equivalent.\n"
            "DO penalize for missing key points, theological errors, or adding content "
            "that contradicts the reference.\n\n"
            'Respond with ONLY a JSON object:\n'
            '{"score": <0-100>, "justification": "<brief explanation>"}'
        )

    def _parse_output(self, raw_output: str) -> dict:
        """Parse the judge's JSON output."""
        # Try to extract JSON from the response.
        # The judge might wrap it in markdown code blocks or add extra text.
        # Use brace-balanced extraction to handle nested braces in justification text.
        result = self._extract_json_with_score(raw_output)
        if result is not None:
            try:
                score = max(0, min(100, int(result.get("score", 0))))
                justification = result.get("justification", "")
                return {
                    "score": score,
                    "method": "llm_judge",
                    "details": {
                        "justification": justification,
                        "raw_output": raw_output,
                    },
                }
            except (ValueError, TypeError):
                pass

        # Fallback: look for "score": N pattern directly
        score_match = re.search(r'"score"\s*:\s*(\d{1,3})', raw_output)
        if score_match:
            n_int = int(score_match.group(1))
            if 0 <= n_int <= 100:
                return {
                    "score": n_int,
                    "method": "llm_judge",
                    "details": {
                        "justification": "Score extracted from partial JSON",
                        "raw_output": raw_output,
                    },
                }

        # Complete failure to parse
        return {
            "score": 0,
            "method": "llm_judge",
            "details": {
                "justification": "Failed to parse judge output",
                "raw_output": raw_output,
            },
        }

    @staticmethod
    def _extract_json_with_score(text: str) -> dict | None:
        """Extract a JSON object containing a 'score' key, handling nested braces."""
        # Find each '{' and try json.loads from that position
        for i, ch in enumerate(text):
            if ch != '{':
                continue
            # Find the balancing closing brace
            depth = 0
            for j in range(i, len(text)):
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[i:j + 1]
                        try:
                            obj = json.loads(candidate)
                            if isinstance(obj, dict) and "score" in obj:
                                return obj
                        except json.JSONDecodeError:
                            pass
                        break
        return None


def score_with_judge(question: dict, response: str, judge: JudgeScorer = None) -> dict:
    """Score a response using the LLM judge.

    Creates a JudgeScorer if not provided.
    """
    if judge is None:
        judge = JudgeScorer()
    return judge.score(question, response)


def should_use_judge(question: dict) -> bool:
    """Return True if this question should be scored by the LLM judge.

    Checks the scoring method and category.
    """
    scoring = question.get("scoring", {})
    if scoring.get("method") == "llm_judge":
        return True
    category = question.get("category", "")
    return category in _JUDGE_CATEGORIES
