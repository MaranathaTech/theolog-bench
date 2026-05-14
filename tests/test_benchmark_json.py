"""Validate benchmark.json structural correctness."""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

BENCHMARK_PATH = Path(__file__).parent.parent / "benchmark.json"


@pytest.fixture
def benchmark():
    """Load benchmark.json."""
    if not BENCHMARK_PATH.exists():
        pytest.skip("benchmark.json not generated yet - run build_benchmark.py first")
    with open(BENCHMARK_PATH) as f:
        return json.load(f)


class TestBenchmarkStructure:
    def test_benchmark_has_version(self, benchmark):
        assert benchmark.get("version") == "1.0"

    def test_benchmark_has_categories(self, benchmark):
        cats = benchmark.get("categories", {})
        expected = {
            "catechism_recall",
            "confessional_knowledge",
            "doctrinal_position",
            "biblical_reference",
            "error_detection",
            "comparative_theology",
        }
        assert set(cats.keys()) == expected

    def test_category_weights_sum_to_one(self, benchmark):
        weights = sum(v["weight"] for v in benchmark["categories"].values())
        assert abs(weights - 1.0) < 0.01

    def test_all_questions_have_required_fields(self, benchmark):
        for q in benchmark["questions"]:
            assert "id" in q, f"Missing id in question"
            assert "category" in q, f"Missing category in {q.get('id', 'unknown')}"
            assert "question" in q, f"Missing question in {q.get('id', 'unknown')}"
            assert "scoring" in q, f"Missing scoring in {q.get('id', 'unknown')}"
            assert q["category"] in benchmark["categories"], (
                f"Unknown category {q['category']} in {q['id']}"
            )

    def test_question_ids_are_unique(self, benchmark):
        ids = [q["id"] for q in benchmark["questions"]]
        assert len(ids) == len(set(ids)), (
            f"Duplicate IDs found: {[x for x in ids if ids.count(x) > 1]}"
        )

    def test_minimum_question_counts(self, benchmark):
        """Each category should have a reasonable number of questions."""
        counts = Counter(q["category"] for q in benchmark["questions"])
        assert counts["catechism_recall"] >= 50, (
            f"catechism_recall has only {counts['catechism_recall']}"
        )
        assert counts["doctrinal_position"] >= 20
        assert counts["biblical_reference"] >= 15
        assert counts["error_detection"] >= 15
        assert counts["confessional_knowledge"] >= 20
        assert counts["comparative_theology"] >= 10

    def test_scoring_methods_are_valid(self, benchmark):
        valid_methods = {
            "semantic_similarity",
            "position_detection",
            "reference_check",
            "llm_judge",
        }
        for q in benchmark["questions"]:
            method = q["scoring"].get("method")
            assert method in valid_methods, (
                f"Invalid scoring method '{method}' in {q['id']}"
            )

    def test_smoke_subset_is_valid(self, benchmark):
        """Verify that limiting to 3 per category still covers all categories."""
        cats = Counter(q["category"] for q in benchmark["questions"])
        for cat, count in cats.items():
            assert count >= 3, (
                f"Category {cat} has only {count} questions, need at least 3 for smoke test"
            )
