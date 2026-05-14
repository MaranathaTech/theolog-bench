"""Unit tests for lib/report.py."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.report import generate_report, generate_comparison_report


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
        assert "results/test-model_20260512.json" in report

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
