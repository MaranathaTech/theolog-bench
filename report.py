#!/usr/bin/env python3
"""Generate reports from theolog-bench results."""

import argparse
import json
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load .env file from the theolog-bench directory
load_dotenv(Path(__file__).parent / ".env")

from lib.report import generate_comparison_report, generate_detailed_report, generate_report
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
        "--group",
        type=str,
        default=None,
        help="Filter results to only models in this config group (e.g. 'frontier', '24gb')",
    )
    parser.add_argument(
        "--rescore",
        action="store_true",
        help="Re-run automated scorer on all questions (keeps judge scores)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Generate a detailed narrative report using the judge LLM",
    )
    parser.add_argument(
        "--group-name",
        type=str,
        default=None,
        help="Label for the report (e.g. 'Frontier Cloud Models')",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom title for comparison reports (default: 'theolog-bench Comparison Report')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write report to this file instead of stdout",
    )
    args = parser.parse_args()

    if args.all:
        results_dir = Path(__file__).parent / "results" / "raw"
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
        if args.group:
            # Filter to only models belonging to the specified config group
            config_path = Path(__file__).parent / "config.yaml"
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            group_presets = cfg.get("groups", {}).get(args.group, [])
            if not group_presets:
                print(f"Unknown group: {args.group}")
                return
            # Resolve preset names to model names
            presets_cfg = cfg.get("presets", {})
            group_models = set()
            for preset_name in group_presets:
                preset = presets_cfg.get(preset_name, {})
                if preset.get("model"):
                    group_models.add(preset["model"])
            results_list = [
                r for r in results_list
                if r.get("model_name", "") in group_models
            ]
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
        if args.detailed:
            config_path = Path(__file__).parent / "config.yaml"
            with open(config_path) as f:
                config = yaml.safe_load(f)
            report = generate_detailed_report(
                results_list, config,
                group_name=args.group_name,
            )
        else:
            report = generate_comparison_report(results_list, title=args.title)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(report)
            print(f"Report written to {args.output}")
        else:
            print(report)
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

    if (args.compare or args.detailed) and len(results_list) >= 2:
        if args.detailed:
            config_path = Path(__file__).parent / "config.yaml"
            with open(config_path) as f:
                config = yaml.safe_load(f)
            report = generate_detailed_report(
                results_list, config,
                group_name=args.group_name,
            )
        else:
            report = generate_comparison_report(results_list, title=args.title)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(report)
            print(f"Report written to {args.output}")
        else:
            print(report)
    elif len(results_list) == 1:
        print(generate_report(results_list[0]))
    else:
        for r in results_list:
            print(generate_report(r))
            print()


if __name__ == "__main__":
    main()
