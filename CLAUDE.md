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
├── results/                  # Benchmark run results (gitignored)
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
- `lib/judge.py` — LLM-as-judge scoring: `JudgeScorer` class uses an `APIBackend` to evaluate responses for theological accuracy. `score_with_judge(question, response)` is the convenience entry point. `should_use_judge(question)` returns True for questions needing judge evaluation (confessional_knowledge, comparative_theology, error_detection, or explicit `llm_judge` method). Judge config is read from `config.yaml` `judge:` section. Failed judge calls return `score: 0` with `error: True` instead of crashing.
- `lib/report.py` — Report formatting: `generate_report(results)` produces a text report with category breakdown, overall score, and flagged failures. `generate_comparison_report(results_list)` shows side-by-side category scores for 2+ runs.
- `run.py` — Main benchmark runner CLI. Orchestrates: load questions → query model → automated scoring → optional LLM judge → save JSON results → print report. Supports `--backend local|api`, `--categories`, `--limit`, `--judge/--no-judge`, `--preset <name>`, `--sweep [presets...]`, `--list-presets`, `--smoke` (quick 3-per-category smoke test), `--group <name>` (run a named group of presets), `--list-groups`, `--resume <file>` (resume from partial results). Saves atomic checkpoints every 10 questions/judge calls. Results include `"status"` field (`"in_progress"`, `"complete"`, or `"aborted: <reason>"`). Sweep mode isolates errors per preset so one failure doesn't crash the entire multi-model run.
- `report.py` — Standalone tool to regenerate reports from saved result JSON files, or compare multiple runs with `--compare`.
- `config.yaml` — Configuration for the LLM judge (defaults to Gemini 2.5 Flash on OpenRouter), scoring params, model presets for `--preset`/`--sweep`, and named groups for `--group` (local, budget, mid, frontier, cloud, all, finetune-compare, smoke).
- `benchmark.json` — The generated question bank. Do not edit manually; regenerate via `build_benchmark.py`.

## Benchmark Categories

| Category | Weight | Scoring Method | Description |
|---|---|---|---|
| catechism_recall | 0.25 | semantic_similarity | Direct recall of catechism Q&A |
| confessional_knowledge | 0.15 | llm_judge | Knowledge of confessional teaching |
| doctrinal_position | 0.20 | position_detection | TULIP, Solas, Reformed distinctives |
| biblical_reference | 0.15 | reference_check | Scripture citation accuracy |
| error_detection | 0.15 | position_detection | Identifying heterodox statements |
| comparative_theology | 0.10 | llm_judge | Reformed vs other traditions |

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
python3 run.py --group budget                                    # Run all presets in a named group
python3 run.py --smoke --group budget                            # Smoke test all budget models
python3 run.py --list-groups                                     # List available groups
python3 report.py results/<file>.json                           # View a result
python3 report.py results/a.json results/b.json --compare       # Compare runs
python3 run.py --resume results/<partial>.json --preset <name> --judge  # Resume from partial results
```
