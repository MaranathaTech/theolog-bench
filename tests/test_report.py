"""Unit tests for lib/report.py."""

import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.report import (
    generate_report,
    generate_comparison_report,
    _compute_report_data,
    _build_report_prompt,
    generate_detailed_report,
)


class TestGenerateReport:
    def test_generate_report_has_all_sections(self, sample_results):
        """Report includes model name, overall score, categories, and failures."""
        report = generate_report(sample_results)
        assert "test-model" in report
        assert "Overall Score:" in report
        assert "Catechism Recall" in report
        assert "Confessional Knowledge" in report
        assert "Doctrinal Position" in report
        assert "Biblical Reference" in report
        assert "Error Detection" in report
        assert "Comparative Theology" in report

    def test_generate_report_flags_low_scores(self, sample_results):
        """Report flags questions with score < 40."""
        report = generate_report(sample_results)
        # comp-rc-01 has score 30, should appear in flagged failures
        assert "comp-rc-01" in report
        # wsc-001 has score 95, should NOT appear in flagged section
        flagged_section = report.split("Flagged")[1] if "Flagged" in report else ""
        assert "wsc-001" not in flagged_section

    def test_generate_report_overall_score_is_weighted(self, sample_results):
        """Overall score uses category weights, not simple average."""
        report = generate_report(sample_results)
        match = re.search(r"Overall Score:\s+(\d+\.\d+)", report)
        assert match is not None
        overall = float(match.group(1))
        assert 0 < overall < 100

    def test_generate_report_includes_results_path(self, sample_results):
        """Report includes the results file path."""
        report = generate_report(sample_results)
        assert "results/raw/test-model_20260512.json" in report

    def test_generate_report_includes_timestamp(self, sample_results):
        """Report includes the timestamp."""
        report = generate_report(sample_results)
        assert "2026-05-12T12:00:00" in report


class TestGenerateComparisonReport:
    def test_generate_comparison_report_shows_both_models(self):
        """Comparison report includes both model names."""
        results1 = {
            "model_name": "model-a",
            "category_weights": {"catechism_recall": 1.0},
            "questions": [
                {"id": "q1", "category": "catechism_recall", "score": 80}
            ],
        }
        results2 = {
            "model_name": "model-b",
            "category_weights": {"catechism_recall": 1.0},
            "questions": [
                {"id": "q1", "category": "catechism_recall", "score": 60}
            ],
        }
        report = generate_comparison_report([results1, results2])
        assert "model-a" in report
        assert "model-b" in report
        assert "Delta" in report
        # model-a scores higher, should be ranked #1
        a_pos = report.index("model-a")
        b_pos = report.index("model-b")
        assert a_pos < b_pos

    def test_generate_comparison_needs_two_results(self):
        """Comparison report returns message if only 1 result."""
        result = generate_comparison_report([{"model_name": "only-one"}])
        assert "at least 2" in result.lower()

    def test_generate_comparison_three_models_no_delta(self):
        """With 3+ models, Delta line should not appear."""
        results = [
            {
                "model_name": f"model-{i}",
                "category_weights": {"catechism_recall": 1.0},
                "questions": [
                    {"id": "q1", "category": "catechism_recall", "score": 50 + i * 10}
                ],
            }
            for i in range(3)
        ]
        report = generate_comparison_report(results)
        assert "model-0" in report
        assert "model-1" in report
        assert "model-2" in report
        assert "Delta" not in report

    def test_generate_comparison_overall_row_present(self):
        """Comparison report includes OVERALL row."""
        results1 = {
            "model_name": "m1",
            "category_weights": {"catechism_recall": 1.0},
            "questions": [
                {"id": "q1", "category": "catechism_recall", "score": 80}
            ],
        }
        results2 = {
            "model_name": "m2",
            "category_weights": {"catechism_recall": 1.0},
            "questions": [
                {"id": "q1", "category": "catechism_recall", "score": 60}
            ],
        }
        report = generate_comparison_report([results1, results2])
        assert "OVERALL" in report

    def test_generate_comparison_custom_title(self):
        """Comparison report uses custom title when provided."""
        results = [
            {
                "model_name": f"model-{i}",
                "category_weights": {"catechism_recall": 1.0},
                "questions": [
                    {"id": "q1", "category": "catechism_recall", "score": 50 + i * 10}
                ],
            }
            for i in range(2)
        ]
        report = generate_comparison_report(results, title="theolog-bench Leaderboard")
        assert "theolog-bench Leaderboard" in report
        assert "Comparison Report" not in report

    def test_generate_comparison_default_title(self):
        """Comparison report uses default title when none provided."""
        results = [
            {
                "model_name": f"model-{i}",
                "category_weights": {"catechism_recall": 1.0},
                "questions": [
                    {"id": "q1", "category": "catechism_recall", "score": 50 + i * 10}
                ],
            }
            for i in range(2)
        ]
        report = generate_comparison_report(results)
        assert "theolog-bench Comparison Report" in report


# Fixtures for detailed report tests

@pytest.fixture
def two_model_results():
    """Two result sets for detailed report testing."""
    return [
        {
            "model_name": "vendor-a/model-alpha",
            "category_weights": {
                "catechism_recall": 0.25,
                "confessional_knowledge": 0.15,
                "doctrinal_position": 0.20,
            },
            "questions": [
                {"id": "q1", "category": "catechism_recall", "score": 90},
                {"id": "q2", "category": "catechism_recall", "score": 80},
                {"id": "q3", "category": "confessional_knowledge", "score": 70},
                {"id": "q4", "category": "doctrinal_position", "score": 60},
                {"id": "q5", "category": "doctrinal_position", "score": 0},
            ],
        },
        {
            "model_name": "vendor-b/model-beta",
            "category_weights": {
                "catechism_recall": 0.25,
                "confessional_knowledge": 0.15,
                "doctrinal_position": 0.20,
            },
            "questions": [
                {"id": "q1", "category": "catechism_recall", "score": 50},
                {"id": "q2", "category": "catechism_recall", "score": 40},
                {"id": "q3", "category": "confessional_knowledge", "score": 85},
                {"id": "q4", "category": "doctrinal_position", "score": 10},
                {"id": "q5", "category": "doctrinal_position", "score": 0},
            ],
        },
    ]


@pytest.fixture
def sample_config():
    """Minimal config dict for testing."""
    return {
        "judge": {
            "backend": "api",
            "api_url": "https://openrouter.ai/api/v1",
            "model": "google/gemini-2.5-flash",
        },
        "presets": {
            "alpha": {
                "model": "vendor-a/model-alpha",
                "description": "Model Alpha",
                "meta": {
                    "vendor": "VendorA",
                    "architecture": "70B dense",
                    "params": "70B",
                    "local_capable": True,
                },
            },
            "beta": {
                "model": "vendor-b/model-beta",
                "description": "Model Beta",
                "meta": {
                    "vendor": "VendorB",
                    "architecture": "32B MoE",
                    "params": "32B",
                    "local_capable": False,
                },
            },
        },
        "group_descriptions": {
            "test-group": "A test group of models for unit testing.",
        },
    }


class TestComputeReportData:
    def test_structure(self, two_model_results, sample_config):
        """_compute_report_data returns expected top-level keys."""
        data = _compute_report_data(two_model_results, sample_config, "Test Group")
        assert "group_name" in data
        assert "models" in data
        assert "categories" in data
        assert "category_weights" in data
        assert "cat_winners" in data
        assert "run_date" in data
        assert data["group_name"] == "Test Group"

    def test_models_ranked_by_score(self, two_model_results, sample_config):
        """Models are sorted by overall score descending."""
        data = _compute_report_data(two_model_results, sample_config)
        models = data["models"]
        assert len(models) == 2
        assert models[0]["overall"] >= models[1]["overall"]
        # model-alpha should be first (higher scores)
        assert models[0]["name"] == "vendor-a/model-alpha"

    def test_meta_lookup(self, two_model_results, sample_config):
        """Meta is looked up from config presets by model name."""
        data = _compute_report_data(two_model_results, sample_config)
        alpha = [m for m in data["models"] if m["name"] == "vendor-a/model-alpha"][0]
        assert alpha["meta"]["vendor"] == "VendorA"
        assert alpha["meta"]["architecture"] == "70B dense"

    def test_failure_counts(self, two_model_results, sample_config):
        """Severe failures and zeros are counted correctly."""
        data = _compute_report_data(two_model_results, sample_config)
        alpha = [m for m in data["models"] if m["name"] == "vendor-a/model-alpha"][0]
        beta = [m for m in data["models"] if m["name"] == "vendor-b/model-beta"][0]
        # alpha has one zero (score 0), one severe failure (score 0 < 20)
        assert alpha["zeros"] == 1
        assert alpha["severe_failures"] == 1
        # beta has one zero and one score of 10 (both < 20)
        assert beta["zeros"] == 1
        assert beta["severe_failures"] == 2

    def test_cat_winners(self, two_model_results, sample_config):
        """Category winners are identified correctly."""
        data = _compute_report_data(two_model_results, sample_config)
        # alpha wins catechism_recall (85 avg vs 45 avg)
        assert data["cat_winners"]["catechism_recall"] == "vendor-a/model-alpha"
        # beta wins confessional_knowledge (85 vs 70)
        assert data["cat_winners"]["confessional_knowledge"] == "vendor-b/model-beta"


class TestBuildReportPrompt:
    def test_prompt_includes_required_sections(self, two_model_results, sample_config):
        """Prompt includes data summary, style example placeholder, and instructions."""
        data = _compute_report_data(two_model_results, sample_config, "Test Group")
        prompt = _build_report_prompt(data, "Example report text here", "A test group.")
        assert "STYLE EXAMPLE" in prompt
        assert "Example report text here" in prompt
        assert "BENCHMARK DATA" in prompt
        assert "Overall Rankings" in prompt
        assert "Category Breakdown" in prompt
        assert "Detailed Analysis" in prompt
        assert "Recommendation" in prompt
        assert "vendor-a/model-alpha" in prompt
        assert "vendor-b/model-beta" in prompt

    def test_prompt_includes_group_description(self, two_model_results, sample_config):
        """Prompt includes the group description when provided."""
        data = _compute_report_data(two_model_results, sample_config, "Test Group")
        prompt = _build_report_prompt(data, "example", "These are test models.")
        assert "These are test models." in prompt

    def test_prompt_includes_scores(self, two_model_results, sample_config):
        """Prompt includes actual score numbers from the data."""
        data = _compute_report_data(two_model_results, sample_config)
        prompt = _build_report_prompt(data, "example")
        # alpha catechism avg is 85.0
        assert "85.0%" in prompt
        # beta confessional avg is 85.0
        assert "85.0%" in prompt


class TestGenerateDetailedReport:
    def test_needs_two_results(self, sample_config):
        """Returns message if fewer than 2 results."""
        result = generate_detailed_report([{"model_name": "only-one"}], sample_config)
        assert "at least 2" in result.lower()

    @patch("lib.backends.APIBackend")
    def test_calls_llm_and_returns_report(self, mock_backend_cls,
                                          two_model_results, sample_config):
        """generate_detailed_report calls the LLM and returns its output."""
        mock_backend = MagicMock()
        mock_backend.name.return_value = "test-judge"
        mock_backend.generate.return_value = (
            "# Test Report\n\nThis is a detailed analysis of the models.\n"
            "Overall the results show significant differences between models."
        )
        mock_backend_cls.return_value = mock_backend

        report = generate_detailed_report(
            two_model_results, sample_config,
            group_name="Unit Test Group",
        )
        assert "Test Report" in report
        assert "detailed analysis" in report
        mock_backend.generate.assert_called_once()

    @patch("lib.backends.APIBackend")
    def test_fallback_on_llm_failure(self, mock_backend_cls,
                                     two_model_results, sample_config):
        """Falls back to leaderboard report when LLM call fails."""
        mock_backend = MagicMock()
        mock_backend.name.return_value = "test-judge"
        mock_backend.generate.side_effect = RuntimeError("API error")
        mock_backend_cls.return_value = mock_backend

        report = generate_detailed_report(two_model_results, sample_config)
        # Should fall back to comparison report format
        assert "OVERALL" in report
        assert "vendor-a/model-alpha" in report

    @patch("lib.backends.APIBackend")
    def test_fallback_on_empty_response(self, mock_backend_cls,
                                        two_model_results, sample_config):
        """Falls back to leaderboard report when LLM returns empty."""
        mock_backend = MagicMock()
        mock_backend.name.return_value = "test-judge"
        mock_backend.generate.return_value = ""
        mock_backend_cls.return_value = mock_backend

        report = generate_detailed_report(two_model_results, sample_config)
        assert "OVERALL" in report

    @patch("lib.backends.APIBackend")
    def test_group_description_from_config(self, mock_backend_cls,
                                           two_model_results, sample_config):
        """Looks up group description from config when not explicitly provided."""
        mock_backend = MagicMock()
        mock_backend.name.return_value = "test-judge"
        mock_backend.generate.return_value = (
            "# Full Report\n\nDetailed analysis with enough content to pass "
            "the minimum length check for the report validation logic here."
        )
        mock_backend_cls.return_value = mock_backend

        generate_detailed_report(
            two_model_results, sample_config,
            group_name="test-group",
        )
        # The prompt sent to the LLM should include the group description
        call_args = mock_backend.generate.call_args[0][0]
        assert "A test group of models for unit testing." in call_args
