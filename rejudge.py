#!/usr/bin/env python3
"""Re-run LLM-as-judge scoring on existing result files.

Uses the new specialized judge prompts (position, catechism) on all results.
Preserves model responses — only re-scores the judge portions.

Usage:
    python rejudge.py                          # Re-judge all latest complete results
    python rejudge.py results/raw/foo.json     # Re-judge specific file(s)
    python rejudge.py --dry-run                # Show what would be re-judged
"""

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from lib.judge import JudgeScorer, should_use_judge
from lib.scorer import score_response


def find_latest_results() -> list[Path]:
    """Find the most recent complete run for each model."""
    raw_dir = Path(__file__).parent / "results" / "raw"
    by_model: dict[str, tuple[Path, str]] = {}
    for f in raw_dir.glob("*.json"):
        if "_smoke_" in f.name:
            continue
        try:
            with open(f) as fh:
                data = json.load(fh)
            if data.get("status") != "complete":
                continue
            if len(data.get("questions", [])) < 200:
                continue
            model = data["model_name"]
            ts = data.get("timestamp", "")
            if model not in by_model or ts > by_model[model][1]:
                by_model[model] = (f, ts)
        except (json.JSONDecodeError, KeyError):
            continue
    return [path for path, _ in by_model.values()]


def rejudge_file(path: Path, judge: JudgeScorer, dry_run: bool = False) -> dict:
    """Re-judge a single results file. Returns stats."""
    with open(path) as f:
        results = json.load(f)

    model = results.get("model_name", "unknown")
    questions = results.get("questions", [])

    # First, re-run automated scoring to get fresh baselines
    for q in questions:
        response = q.get("response", "")
        if not response:
            continue
        result = score_response(q, response)
        q["automated_score"] = result["score"]
        q["automated_score_method"] = result["method"]

    # Identify questions needing judge scoring
    judge_questions = [q for q in questions if should_use_judge(q) and q.get("response")]

    stats = {
        "model": model,
        "total_questions": len(questions),
        "judge_questions": len(judge_questions),
        "rescored": 0,
        "errors": 0,
    }

    if dry_run:
        # Count by category
        by_cat = {}
        for q in judge_questions:
            cat = q.get("category", "unknown")
            by_cat[cat] = by_cat.get(cat, 0) + 1
        stats["by_category"] = by_cat
        return stats

    print(f"\n  Re-judging {model} ({len(judge_questions)} judge questions)...")
    for i, q in enumerate(judge_questions, 1):
        if i % 20 == 0 or i == 1:
            print(f"    [{i}/{len(judge_questions)}]...")

        judge_result = judge.score(q, q["response"])
        q["judge_score"] = judge_result["score"]
        q["judge_details"] = judge_result["details"]
        # Judge is authoritative
        q["score"] = judge_result["score"]
        q["score_details"] = judge_result["details"]
        q["score_method"] = "llm_judge"
        stats["rescored"] += 1

        if judge_result.get("details", {}).get("error"):
            stats["errors"] += 1

    # For non-judge questions, use automated score as primary
    for q in questions:
        if not should_use_judge(q):
            if "automated_score" in q:
                q["score"] = q["automated_score"]
                q["score_method"] = q["automated_score_method"]

    # Save back
    results["status"] = "complete"
    with open(path, "w") as f:
        json.dump(results, f, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Re-run LLM-as-judge with new specialized prompts"
    )
    parser.add_argument(
        "results", nargs="*", help="Specific result files to re-judge"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be re-judged without making calls"
    )
    args = parser.parse_args()

    if args.results:
        paths = [Path(p) for p in args.results]
    else:
        paths = find_latest_results()

    if not paths:
        print("No result files found.")
        sys.exit(1)

    print(f"Found {len(paths)} result files to re-judge.")

    if args.dry_run:
        total_calls = 0
        for path in sorted(paths):
            stats = rejudge_file(path, judge=None, dry_run=True)
            n = stats["judge_questions"]
            total_calls += n
            cats = stats.get("by_category", {})
            cat_str = ", ".join(f"{k}={v}" for k, v in sorted(cats.items()))
            print(f"  {stats['model']:45s}  {n:3d} judge calls  ({cat_str})")
        print(f"\nTotal judge API calls: {total_calls}")
        est_cost = total_calls * 0.00033  # ~$0.00033 per Gemini Flash call
        print(f"Estimated cost: ~${est_cost:.2f}")
        return

    judge = JudgeScorer()
    all_stats = []

    for i, path in enumerate(sorted(paths), 1):
        print(f"\n[{i}/{len(paths)}] Processing: {path.name}")
        try:
            stats = rejudge_file(path, judge)
            all_stats.append(stats)
            print(f"    Done: {stats['rescored']} scored, {stats['errors']} errors")
        except Exception as e:
            print(f"    ERROR: {e}")
            all_stats.append({"model": path.name, "error": str(e)})

    # Summary
    print(f"\n{'=' * 60}")
    print("Re-judging complete!")
    total_scored = sum(s.get("rescored", 0) for s in all_stats)
    total_errors = sum(s.get("errors", 0) for s in all_stats)
    print(f"  Models processed: {len(all_stats)}")
    print(f"  Total judge calls: {total_scored}")
    print(f"  Errors: {total_errors}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
