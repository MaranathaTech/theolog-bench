# theolog-bench

Reformed theology benchmark for evaluating LLM theological accuracy.

## Project Structure

```
theolog-bench/
├── lib/                      # Python library modules
│   ├── __init__.py
│   ├── backends.py           # ModelBackend ABC, UnslothBackend, APIBackend
│   ├── scorer.py             # Automated scoring: semantic_similarity, position_detection, reference_check
│   ├── judge.py              # LLM-as-judge scoring via APIBackend for confessional_knowledge, comparative_theology
│   └── report.py             # Report formatting: generate_report(), generate_comparison_report()
├── results/                  # Benchmark outputs
│   ├── raw/                  # JSON result files from benchmark runs
│   └── reports/              # Narrative markdown comparison reports
├── build_benchmark.py        # Generates benchmark.json from creed JSON files
├── run.py                    # Main benchmark runner CLI
├── report.py                 # Standalone report generation / comparison tool
├── benchmark.json            # Generated question bank (~270 questions)
├── config.yaml               # Judge model, scoring config, and model presets
├── .env.example              # Template for API key environment variables
└── requirements.txt          # Python dependencies (openai, pyyaml)
```

## Key Files

- `build_benchmark.py` — Reads creed JSON files from `../data/raw/creeds/` and generates `benchmark.json`. Run with `python3 build_benchmark.py`.
- `lib/backends.py` — Model backends: `UnslothBackend` (local Unsloth/4-bit) and `APIBackend` (OpenAI-compatible API). Both implement `ModelBackend` ABC with `generate(question) -> str` and `name() -> str`. Temperature defaults to 0.3. APIBackend auto-detects `OPENROUTER_API_KEY` / `OPENAI_API_KEY` env vars when no explicit key is provided. `APIBackend.generate()` retries transient errors (429, 5xx, timeouts) with exponential backoff (5 attempts, 2-60s). Hard errors (401, 402) raise `BenchmarkAPIError(retryable=False)` immediately.
- `lib/scorer.py` — Automated scoring: `score_response(question, response)` dispatches to `score_semantic_similarity`, `score_position_detection`, `score_reference_check`, or returns a deferred placeholder for `llm_judge`. All return `{"score": int, "method": str, "details": dict}` with scores 0-100.
- `lib/judge.py` — LLM-as-judge scoring: `JudgeScorer` class uses an `APIBackend` to evaluate responses for theological accuracy. `score_with_judge(question, response)` is the convenience entry point. `should_use_judge(question)` returns True for questions needing judge evaluation (all categories except biblical_reference). Dispatches to specialized prompts: `_build_position_prompt()` for position_detection, `_build_catechism_prompt()` for semantic_similarity, and generic `_build_prompt()` for llm_judge. Judge config is read from `config.yaml` `judge:` section. Failed judge calls return `score: 0` with `error: True` instead of crashing.
- `lib/report.py` — Report formatting: `generate_report(results)` produces a text report with category breakdown, overall score, and flagged failures. `generate_comparison_report(results_list)` shows side-by-side category scores for 2+ runs. `generate_detailed_report(results_list, config, group_name, group_description)` generates a narrative markdown report using the judge LLM (styled after `results/reports/96gb-card-comparison.md`), falling back to leaderboard on failure. Helpers `_compute_report_data()` and `_build_report_prompt()` handle data computation and prompt construction.
- `run.py` — Main benchmark runner CLI. Orchestrates: load questions → query model → automated scoring → optional LLM judge → save JSON results → print report. Supports `--backend local|api`, `--categories`, `--limit`, `--judge/--no-judge`, `--preset <name>`, `--sweep [presets...]`, `--list-presets`, `--smoke` (quick 3-per-category smoke test), `--group <name>` (run a named group of presets), `--list-groups`, `--resume <file>` (resume from partial results), `--detailed` (generate LLM narrative report after sweep/group). Saves atomic checkpoints every 10 questions/judge calls. Results include `"status"` field (`"in_progress"`, `"complete"`, or `"aborted: <reason>"`). Sweep mode isolates errors per preset so one failure doesn't crash the entire multi-model run.
- `report.py` — Standalone tool to regenerate reports from saved result JSON files, compare multiple runs with `--compare`, or generate LLM narrative reports with `--detailed`. Supports `--group-name NAME` (label the report) and `--output FILE` (write to file).
- `rejudge.py` — Re-runs LLM-as-judge scoring on existing result files using current judge prompts. Finds latest complete run per model, re-runs automated scoring (stored as `automated_score`), then runs judge on all eligible questions. Use `--dry-run` to preview scope/cost. Useful after judge prompt changes to update scores without re-querying models.
- `config.yaml` — Configuration for the LLM judge (defaults to Gemini 2.5 Flash on OpenRouter), scoring params (default max_tokens=2048, thinking models override to 4096), model presets for `--preset`/`--sweep` (each with optional `meta:` block for vendor/architecture/params/local_capable), named groups for `--group` (12gb, 24gb, 48gb, 96gb, budget, mid, frontier, cloud, all, local), and `group_descriptions:` for detailed report generation. All open-weight groups run via OpenRouter by default; use `--local` to override to Ollama.
- `benchmark.json` — The generated question bank. Do not edit manually; regenerate via `build_benchmark.py`.

## Benchmark Categories

| Category | Weight | Automated Method | Judge? | Description |
|---|---|---|---|---|
| catechism_recall | 0.25 | semantic_similarity | Yes (catechism prompt) | Direct recall of catechism Q&A |
| confessional_knowledge | 0.15 | llm_judge | Yes (generic prompt) | Knowledge of confessional teaching |
| doctrinal_position | 0.20 | position_detection | Yes (position prompt) | TULIP, Solas, Reformed distinctives |
| biblical_reference | 0.15 | reference_check | No | Scripture citation accuracy |
| error_detection | 0.15 | position_detection | Yes (position prompt) | Identifying heterodox statements |
| comparative_theology | 0.10 | llm_judge | Yes (generic prompt) | Reformed vs other traditions |

When judge is enabled (default), it is authoritative for all categories except biblical_reference. The automated score is preserved in `automated_score` for reference. Judge uses specialized prompts: position detection rewards nuanced answers that clearly conclude with the correct position; catechism recall rewards paraphrased answers that capture all key doctrinal points.

## Data Sources

Creed JSON files are at `../data/raw/creeds/`. Key formats:
- **Catechisms** (WSC, WLC, HC, Puritan, Keach's): `{Number, Question, Answer}`
- **Confessions with chapters** (WCF, LBCF, Dort): `{Chapter, Title?, Sections: [{Section, Content}]}`
- **Article-based** (Belgic): `{Article, Title, Content}`

WCF chapters lack a `Title` field — titles are mapped in `build_benchmark.py` via `WCF_CHAPTER_TITLES`.

## Commands

```bash
python3 build_benchmark.py                                      # Regenerate benchmark.json
python3 run.py --backend api --model qwen3:1.7b                 # Run benchmark against API
python3 run.py --backend api --model qwen3:1.7b --limit 2 --no-judge  # Quick test
python3 run.py --preset gpt-5.5                                 # Use a config preset
python3 run.py --list-presets                                    # List all presets
python3 run.py --sweep finetuned base-qwen3-1.7b gpt-5.5        # Run multiple presets
python3 run.py --sweep                                           # Run all presets
python3 run.py --smoke                                           # Quick smoke test (3 q/cat, cheap model, no judge)
python3 run.py --smoke --preset finetuned                        # Smoke test a specific model
python3 run.py --group 12gb                                      # Small models (12GB VRAM tier)
python3 run.py --group 24gb                                      # Medium models (24GB VRAM tier)
python3 run.py --group 48gb                                      # Large models (48GB VRAM tier)
python3 run.py --group 96gb                                      # XL models (96GB VRAM tier)
python3 run.py --group budget                                    # Cheapest cloud models
python3 run.py --group mid                                       # Mid-tier cloud models
python3 run.py --group frontier                                  # Top frontier models
python3 run.py --group 24gb --local                              # Run 24GB tier via Ollama
python3 run.py --smoke --group budget                            # Smoke test all budget models
python3 run.py --list-groups                                     # List available groups
python3 report.py results/raw/<file>.json                       # View a result
python3 report.py results/raw/a.json results/raw/b.json --compare  # Compare runs
python3 report.py --all --detailed --group-name "Frontier" --output results/reports/frontier-comparison.md  # LLM narrative report
python3 run.py --group frontier --detailed                       # Run group + generate narrative report
python3 run.py --resume results/raw/<partial>.json --preset <name> --judge  # Resume from partial results
python3 rejudge.py --dry-run                                             # Preview re-judge scope and cost
python3 rejudge.py                                                       # Re-judge all latest results with current prompts
python3 rejudge.py results/raw/specific_file.json                        # Re-judge specific file(s)
```
