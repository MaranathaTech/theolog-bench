#!/usr/bin/env python3
"""Run the theolog-bench benchmark against a model."""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load .env file from the theolog-bench directory
load_dotenv(Path(__file__).parent / ".env")


def load_config(config_path: str = None) -> dict:
    """Load configuration from config.yaml."""
    path = config_path or str(Path(__file__).parent / "config.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the theolog-bench Reformed theology benchmark"
    )
    parser.add_argument(
        "--backend", choices=["local", "api"], default=None,
        help="Model backend: 'local' (Unsloth) or 'api' (OpenAI-compatible)",
    )
    parser.add_argument(
        "--model-path", default="../models/reformed-qwen3-1.7b",
        help="Path to local model (for local backend)",
    )
    parser.add_argument(
        "--api-url", default=None,
        help="API URL (for api backend, default from config.yaml)",
    )
    parser.add_argument(
        "--model", default=None,
        help="Model name (for api backend, default from config.yaml)",
    )
    parser.add_argument(
        "--api-key", default=None,
        help="API key (optional, for cloud APIs)",
    )
    parser.add_argument(
        "--benchmark", default="benchmark.json",
        help="Path to benchmark.json (default: benchmark.json)",
    )
    parser.add_argument(
        "--judge", action="store_true", default=True, dest="judge",
        help="Enable LLM-as-judge scoring (default: enabled)",
    )
    parser.add_argument(
        "--no-judge", action="store_false", dest="judge",
        help="Disable LLM-as-judge scoring",
    )
    parser.add_argument(
        "--judge-url", default=None,
        help="Override judge API URL",
    )
    parser.add_argument(
        "--judge-model", default=None,
        help="Override judge model name",
    )
    parser.add_argument(
        "--output-dir", default="results/raw/",
        help="Directory to save results (default: results/raw/)",
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Resume from a partial results file (skip completed questions/judge calls)",
    )
    parser.add_argument(
        "--categories", default=None,
        help="Comma-separated list of categories to run (default: all)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Max questions per category (for quick testing)",
    )
    parser.add_argument(
        "--preset", type=str, default=None,
        help="Use a named preset from config.yaml (e.g., 'finetuned', 'gpt-5.5')",
    )
    parser.add_argument(
        "--sweep", nargs="*", metavar="PRESET",
        help="Run benchmark across multiple presets. No args = all presets. "
             "Or specify: --sweep finetuned base-qwen3-1.7b gpt-5.5",
    )
    parser.add_argument(
        "--list-presets", action="store_true",
        help="List available presets and exit",
    )
    parser.add_argument(
        "--smoke", action="store_true",
        help="Quick smoke test: 3 questions per category, cheap model, no judge",
    )
    parser.add_argument(
        "--group", type=str, default=None,
        help="Run a named group of presets from config.yaml (e.g., 'local', 'budget', 'frontier', 'all')",
    )
    parser.add_argument(
        "--list-groups", action="store_true",
        help="List available groups and their presets, then exit",
    )
    parser.add_argument(
        "--detailed", action="store_true",
        help="Generate a detailed narrative report (LLM-generated) after sweep/group",
    )
    parser.add_argument(
        "--local", action="store_true",
        help="Override all presets to run locally via Ollama (http://localhost:11434/v1). "
             "Requires models to be pulled in Ollama with matching names.",
    )
    return parser


def _apply_local_override(args):
    """If --local flag is set, override to use Ollama."""
    if getattr(args, "local", False):
        args.backend = "api"
        args.api_url = "http://localhost:11434/v1"


def apply_preset(args, parser, config=None):
    """Apply a preset's settings as defaults for unset CLI args."""
    if not args.preset:
        return
    if config is None:
        config = load_config()
    preset = config.get("presets", {}).get(args.preset)
    if not preset:
        print(f"Unknown preset: {args.preset}")
        print(f"Available: {', '.join(config.get('presets', {}).keys())}")
        sys.exit(1)
    if args.backend is None:
        args.backend = preset.get("backend", "api")
    if args.model is None:
        args.model = preset.get("model")
    if args.api_url is None:
        args.api_url = preset.get("api_url")
    if args.model_path == parser.get_default("model_path") and "model_path" in preset:
        args.model_path = preset["model_path"]
    if "max_tokens" in preset:
        args.max_tokens = preset["max_tokens"]
    _apply_local_override(args)


def apply_preset_config(args, parser, preset_config):
    """Apply a preset config dict (from sweep) as defaults for unset CLI args."""
    if args.backend is None:
        args.backend = preset_config.get("backend", "api")
    if args.model is None:
        args.model = preset_config.get("model")
    if args.api_url is None:
        args.api_url = preset_config.get("api_url")
    if args.model_path == parser.get_default("model_path") and "model_path" in preset_config:
        args.model_path = preset_config["model_path"]
    if "max_tokens" in preset_config:
        args.max_tokens = preset_config["max_tokens"]
    _apply_local_override(args)


def _save_checkpoint(results: dict, output_path: Path):
    """Save partial results atomically."""
    tmp_path = output_path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(results, f, indent=2)
    tmp_path.rename(output_path)


def run_single_benchmark(args, config, questions, category_weights):
    """Run benchmark for a single model configuration. Returns the result file path."""
    from lib.backends import BenchmarkAPIError

    # Initialize backend — use preset max_tokens, else global scoring default, else 2048
    global_default = config.get("scoring", {}).get("max_tokens", 2048)
    max_tokens = getattr(args, "max_tokens", None) or global_default
    if args.backend == "local":
        from lib.backends import UnslothBackend
        backend = UnslothBackend(model_path=args.model_path)
    elif args.backend == "api":
        from lib.backends import APIBackend
        backend = APIBackend(
            api_url=args.api_url or "http://localhost:11434/v1",
            model=args.model or "qwen3:1.7b",
            api_key=args.api_key,
            max_tokens=max_tokens,
        )
    else:
        print("Error: --backend is required (or use --preset to set it)")
        sys.exit(1)

    model_name = backend.name()
    num_cats = len(set(q["category"] for q in questions))
    print(f"Running theolog-bench against: {model_name}")
    print(f"Questions: {len(questions)} across {num_cats} categories")
    print()

    # Compute output path early for checkpointing
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = model_name.replace("/", "_").replace(" ", "_")
    smoke_suffix = "_smoke" if getattr(args, "smoke", False) else ""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if getattr(args, "resume", None):
        output_path = Path(args.resume)
    else:
        output_path = output_dir / f"{safe_name}{smoke_suffix}_{timestamp}.json"

    # Initialize results dict
    results = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "category_weights": category_weights,
        "questions": [],
        "results_path": str(output_path),
        "status": "in_progress",
    }

    # Load existing progress if resuming
    existing_responses = {}
    existing_judge = set()
    if getattr(args, "resume", None):
        with open(args.resume) as f:
            prior = json.load(f)
        for q in prior.get("questions", []):
            if q.get("response"):
                existing_responses[q["id"]] = q
            if "judge_score" in q:
                existing_judge.add(q["id"])
        print(f"Resuming: {len(existing_responses)} responses, "
              f"{len(existing_judge)} judge scores loaded")

    # Query model for all questions
    for i, q in enumerate(questions, 1):
        qid = q["id"]
        if qid in existing_responses:
            print(f"  [{i}/{len(questions)}] {qid}: (cached)")
            results["questions"].append(existing_responses[qid])
            continue

        print(f"  [{i}/{len(questions)}] {qid}: {q['question'][:60]}...")
        try:
            response = backend.generate(q["question"])
        except BenchmarkAPIError as e:
            if not e.retryable:
                print(f"\n  FATAL: {e}")
                print(f"  Saving partial results ({len(results['questions'])} questions)...")
                results["status"] = f"aborted: {e}"
                _save_checkpoint(results, output_path)
                return str(output_path)
            print(f"  SKIPPED (retries exhausted): {e}")
            response = ""

        results["questions"].append({**q, "response": response})

        if i % 10 == 0:
            _save_checkpoint(results, output_path)

    # Run automated scoring
    from lib.scorer import score_response

    for rq in results["questions"]:
        if "score" in rq and "score_method" in rq:
            continue  # Already scored (from resume)
        result = score_response(rq, rq["response"])
        rq["score"] = result["score"]
        rq["score_details"] = result["details"]
        rq["score_method"] = result["method"]

    # Checkpoint before judge phase
    _save_checkpoint(results, output_path)

    # Optionally run LLM-as-judge
    if args.judge:
        from lib.judge import JudgeScorer, should_use_judge

        judge_config = {}
        if args.judge_url:
            judge_config["api_url"] = args.judge_url
        if args.judge_model:
            judge_config["model"] = args.judge_model

        # Create judge (uses config.yaml defaults if no overrides)
        if judge_config:
            from lib.backends import APIBackend as JudgeAPI

            judge_backend = JudgeAPI(
                api_url=judge_config.get("api_url", "https://openrouter.ai/api/v1"),
                model=judge_config.get("model", "google/gemini-2.5-flash"),
                api_key=args.api_key,
            )
            judge = JudgeScorer(backend=judge_backend)
        else:
            judge = JudgeScorer()

        judge_questions = [rq for rq in results["questions"] if should_use_judge(rq)]
        print(f"\nRunning LLM-as-judge on {len(judge_questions)} questions...")
        for i, rq in enumerate(judge_questions, 1):
            if rq["id"] in existing_judge:
                print(f"  [judge {i}/{len(judge_questions)}] {rq['id']}: (cached)")
                continue
            print(f"  [judge {i}/{len(judge_questions)}] {rq['id']}...")
            judge_result = judge.score(rq, rq["response"])
            rq["judge_score"] = judge_result["score"]
            rq["judge_details"] = judge_result["details"]
            # Preserve the automated score for reference
            rq["automated_score"] = rq["score"]
            rq["automated_score_method"] = rq.get("score_method", "")
            # Use judge as authoritative score for all judge-scored questions
            rq["score"] = judge_result["score"]
            rq["score_details"] = judge_result["details"]
            rq["score_method"] = "llm_judge"
            if i % 10 == 0:
                _save_checkpoint(results, output_path)

    # Mark complete and save
    results["status"] = "complete"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print report
    from lib.report import generate_report

    print()
    print(generate_report(results))

    return str(output_path)


def main():
    parser = parse_args()
    args = parser.parse_args()
    config = load_config()

    # --list-presets: print presets and exit
    if args.list_presets:
        presets = config.get("presets", {})
        print("Available presets:")
        print()
        local_presets = {
            k: v for k, v in presets.items()
            if v.get("api_url", "").startswith("http://localhost") or v.get("backend") == "local"
        }
        cloud_presets = {k: v for k, v in presets.items() if k not in local_presets}
        print("  Local (Ollama / Unsloth):")
        for name, p in local_presets.items():
            print(f"    {name:25s} {p.get('description', '')}")
        print()
        print("  Cloud (OpenRouter):")
        for name, p in cloud_presets.items():
            print(f"    {name:25s} {p.get('description', '')}")
        return

    # --list-groups: print groups and exit
    if args.list_groups:
        groups = config.get("groups", {})
        presets = config.get("presets", {})
        if not groups:
            print("No groups defined in config.yaml")
            return
        print("Available groups:\n")
        for group_name, preset_list in groups.items():
            cost = 0.0
            for p_name in preset_list:
                p = presets.get(p_name, {})
                desc = p.get("description", "")
                cost_match = re.search(r'~\$(\d+\.?\d*)/run', desc)
                if cost_match:
                    cost += float(cost_match.group(1))
            cost_str = f"~${cost:.2f}" if cost > 0 else "Free"
            print(f"  {group_name:20s} ({len(preset_list)} models, {cost_str})")
            for p_name in preset_list:
                p = presets.get(p_name, {})
                print(f"    - {p_name:25s} {p.get('description', '')}")
            print()
        return

    # --smoke: apply smoke test defaults
    # Detect if user explicitly passed --judge or --no-judge
    judge_explicitly_set = any(a in sys.argv for a in ("--judge", "--no-judge"))
    if args.smoke:
        if args.limit is None:
            args.limit = 3
        if not judge_explicitly_set:
            args.judge = False
        # Use cheap default if no model specified
        if args.backend is None and args.preset is None and args.sweep is None and args.group is None:
            args.backend = "api"
            args.api_url = "https://openrouter.ai/api/v1"
            args.model = "deepseek/deepseek-v4-flash"
        judge_status = "with judge scoring" if args.judge else "no judge scoring"
        print("=" * 60)
        print("SMOKE TEST MODE")
        print(f"3 questions per category, {judge_status}")
        print("=" * 60)
        print()

    # --group: expand to sweep of group's presets
    if args.group:
        groups = config.get("groups", {})
        group = groups.get(args.group)
        if not group:
            print(f"Unknown group: {args.group}")
            print(f"Available: {', '.join(groups.keys())}")
            sys.exit(1)
        args.sweep = group

    # Load benchmark
    with open(args.benchmark) as f:
        benchmark = json.load(f)

    questions = benchmark["questions"]
    category_weights = {k: v["weight"] for k, v in benchmark["categories"].items()}

    # Filter by categories if specified
    if args.categories:
        cats = [c.strip() for c in args.categories.split(",")]
        questions = [q for q in questions if q["category"] in cats]

    # Limit per category if specified
    if args.limit:
        by_cat: dict[str, list] = defaultdict(list)
        for q in questions:
            by_cat[q["category"]].append(q)
        questions = []
        for cat, qs in by_cat.items():
            questions.extend(qs[: args.limit])

    # --sweep: run multiple presets
    if args.sweep is not None:
        presets = config.get("presets", {})
        preset_names = args.sweep if args.sweep else list(presets.keys())

        # Validate all presets first
        for name in preset_names:
            if name not in presets:
                print(f"Unknown preset: {name}")
                sys.exit(1)

        all_result_paths = []
        failed_presets = []
        for name in preset_names:
            print(f"\n{'=' * 60}")
            print(f"Running preset: {name} -- {presets[name].get('description', '')}")
            print(f"{'=' * 60}\n")
            # Create a fresh copy of args for each preset
            sweep_args = argparse.Namespace(**vars(args))
            sweep_args.backend = None
            sweep_args.model = None
            sweep_args.api_url = None
            sweep_args.model_path = parser.get_default("model_path")
            apply_preset_config(sweep_args, parser, presets[name])
            try:
                result_path = run_single_benchmark(sweep_args, config, list(questions), category_weights)
                all_result_paths.append(result_path)
            except Exception as e:
                print(f"\n  ERROR: Preset '{name}' failed: {e}")
                print(f"  Continuing to next preset...\n")
                failed_presets.append((name, str(e)))

        if failed_presets:
            print(f"\n{'=' * 60}")
            print(f"Failed presets ({len(failed_presets)}):")
            for name, err in failed_presets:
                print(f"  - {name}: {err}")
            print(f"{'=' * 60}")

        # Auto-generate comparison report
        if len(all_result_paths) >= 2:
            results_list = []
            for p in all_result_paths:
                with open(p) as f:
                    results_list.append(json.load(f))

            if args.detailed:
                from lib.report import generate_detailed_report

                # Determine group name from --group flag or default
                detail_group_name = args.group or "Sweep Comparison"
                report = generate_detailed_report(
                    results_list, config,
                    group_name=detail_group_name,
                )
                # Save to file
                safe_group = detail_group_name.lower().replace(" ", "-")
                reports_dir = Path("results/reports")
                reports_dir.mkdir(parents=True, exist_ok=True)
                output_path = reports_dir / f"{safe_group}-comparison.md"
                output_path.write_text(report)
                print(f"\n{'=' * 60}")
                print(f"Detailed report saved to {output_path}")
                print(report)
            else:
                from lib.report import generate_comparison_report

                print(f"\n{'=' * 60}")
                print(generate_comparison_report(results_list))

        return

    # --preset: apply preset defaults
    apply_preset(args, parser, config)

    # Validate that backend is set (either via --backend or --preset)
    if args.backend is None:
        print("Error: --backend is required (or use --preset to set it)")
        parser.print_usage()
        sys.exit(1)

    run_single_benchmark(args, config, questions, category_weights)


if __name__ == "__main__":
    main()
