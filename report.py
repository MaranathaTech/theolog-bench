#!/usr/bin/env python3
"""Generate reports from theolog-bench results."""

import argparse
import json
from pathlib import Path

from lib.report import generate_comparison_report, generate_report
from lib.scorer import score_response


def _rescore(results: dict) -> dict:
    """Re-run automated scorer on all questions, keeping judge scores."""
    for q in results.get("questions", []):
        method = q.get("score_method", q.get("scoring", {}).get("method", ""))
        # Keep judge scores — they came from the LLM, not our scorer
        if method == "llm_judge" and q.get("judge_score") is not None:
            continue
        response = q.get("response", "")
        if not response:
            continue
        result = score_response(q, response)
        q["score"] = result["score"]
        q["score_method"] = result["method"]
        q["score_details"] = result["details"]
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate theolog-bench reports")
    parser.add_argument("results", nargs="*", help="Result JSON file(s)")
    parser.add_argument(
        "--compare", action="store_true", help="Compare multiple runs"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Compare all complete (non-smoke) results in results/",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Model name substrings to exclude (e.g. 'reformed' 'qwen3-1.7b')",
    )
    parser.add_argument(
        "--rescore",
        action="store_true",
        help="Re-run automated scorer on all questions (keeps judge scores)",
    )
    args = parser.parse_args()

    if args.all:
        results_dir = Path(__file__).parent / "results"
        paths = sorted(results_dir.glob("*.json"))
        # Collect all complete, non-smoke results; keep latest per model
        by_model: dict[str, dict] = {}
        for p in paths:
            if "_smoke_" in p.name:
                continue
            with open(p) as f:
                data = json.load(f)
            status = data.get("status", "complete")
            if status not in ("complete",):
                continue
            name = data.get("model_name", "unknown")
            ts = data.get("timestamp", "")
            prev = by_model.get(name)
            if prev is None or ts > prev.get("timestamp", ""):
                by_model[name] = data
        results_list = list(by_model.values())
        if args.exclude:
            results_list = [
                r for r in results_list
                if not any(ex.lower() in r.get("model_name", "").lower() for ex in args.exclude)
            ]
        if len(results_list) < 2:
            print("Need at least 2 complete results to compare.")
            return
        if args.rescore:
            results_list = [_rescore(r) for r in results_list]
        print(generate_comparison_report(results_list))
        return

    if not args.results and not args.all:
        parser.print_help()
        return

    results_list = []
    if args.results:
        for path in args.results:
            with open(path) as f:
                results_list.append(json.load(f))

    if args.rescore:
        results_list = [_rescore(r) for r in results_list]

    if args.compare and len(results_list) >= 2:
        print(generate_comparison_report(results_list))
    elif len(results_list) == 1:
        print(generate_report(results_list[0]))
    else:
        for r in results_list:
            print(generate_report(r))
            print()


if __name__ == "__main__":
    main()
