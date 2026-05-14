# theolog-bench: Reformed Theology Benchmark

Evaluates LLM theological accuracy against Reformed confessional standards — the Westminster Standards, Three Forms of Unity, and the 1689 London Baptist Confession of Faith. Unlike generic "Christian AI" benchmarks, theolog-bench tests against specific historic confessions with transparent methodology and reproducible scoring.

## Categories

| Category | Questions | Weight | Scoring Method | Description |
|---|---|---|---|---|
| Catechism Recall | ~120 | 25% | Semantic similarity | Direct recall of catechism Q&A (WSC, WLC, Heidelberg, Puritan, Keach's) |
| Confessional Knowledge | ~40 | 15% | LLM judge | Understanding of confessional teaching (WCF, Belgic, Dort, LBCF) |
| Doctrinal Position | ~30 | 20% | Position detection | TULIP and Five Solas — affirming Reformed distinctives |
| Biblical Reference | ~30 | 15% | Reference check | Scripture citation accuracy for theological claims |
| Error Detection | ~30 | 15% | Position detection | Identifying heterodox statements (Arminian, Roman Catholic, liberal, etc.) |
| Comparative Theology | ~20 | 10% | LLM judge | Distinguishing Reformed theology from other traditions |

## Scoring Methodology

### Automated Methods

- **Semantic similarity** (`catechism_recall`) — Splits the expected answer into phrases and concepts, then checks how many appear in the model's response. Uses a 60/40 weighting of phrase presence vs. concept coverage against a configurable similarity threshold (default 0.6).

- **Position detection** (`doctrinal_position`, `error_detection`) — Pattern-matching against required affirmations/denials and key doctrinal points. Checks that the model affirms what it should affirm and denies what it should deny, with bonus points for including required theological terms.

- **Reference check** (`biblical_reference`) — Extracts Bible citations from the response and compares them against expected references. Handles book name normalization and verse-level matching.

### LLM-as-Judge

For categories requiring nuanced theological evaluation (`confessional_knowledge`, `comparative_theology`, `error_detection`), an LLM judge scores responses on a 0-100 scale with a written justification. The judge model is configured in `config.yaml`.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate the question bank (only needed once, or to regenerate)
python build_benchmark.py

# Test against an Ollama model
python run.py --backend api --api-url http://localhost:11434/v1 --model qwen3:1.7b

# Test against the fine-tuned local model
python run.py --backend local --model-path ../models/reformed-qwen3-1.7b

# Test against OpenAI
python run.py --backend api --api-url https://api.openai.com/v1 --model gpt-4o --api-key $OPENAI_API_KEY

# Quick test (2 questions per category)
python run.py --backend api --api-url http://localhost:11434/v1 --model qwen3:1.7b --limit 2

# Run only specific categories
python run.py --backend api --model qwen3:1.7b --categories catechism_recall,doctrinal_position

# Disable LLM judge (automated scoring only)
python run.py --backend api --model qwen3:1.7b --no-judge

# Compare runs
python report.py --compare results/raw/qwen3_1.7b_*.json results/raw/reformed-qwen3-1.7b_*.json
```

Results are saved to `results/raw/{model}_{timestamp}.json`. Narrative comparison reports are saved to `results/reports/`.

## Quick Smoke Test

Verify the tool works before committing to a full benchmark:

    # Smoke test with cheapest cloud model (<$0.01)
    python run.py --smoke

    # Smoke test your fine-tuned model
    python run.py --smoke --preset finetuned

    # Smoke test a group of models
    python run.py --smoke --group budget

Smoke mode runs 3 questions per category (18 total), skips judge scoring,
and costs less than a penny on cloud models.

## Run Groups

Pre-defined groups for common testing scenarios:

    python run.py --list-groups          # See all groups
    python run.py --group local          # All Ollama models (free)
    python run.py --group budget         # Cheapest cloud models (~$0.25)
    python run.py --group mid            # Mid-tier cloud (~$1.50)
    python run.py --group frontier       # Top models (~$15)
    python run.py --group cloud          # All cloud models (~$17)
    python run.py --group all            # Everything (~$26)
    python run.py --group finetune-compare  # Just base vs fine-tuned (free)

## Model Test Matrix

theolog-bench includes pre-configured presets for testing across model sizes and providers.
List them with:

    python run.py --list-presets

### Recommended Test Progression

**1. Local baselines (free, requires Ollama):**

    python run.py --preset base-qwen3-1.7b    # Base model (your fine-tuning starting point)
    python run.py --preset finetuned           # Your fine-tuned model
    python run.py --preset qwen3-4b            # Next size up
    python run.py --preset gemma4-e4b          # Google's efficient 4.5B model

**2. Mid-range open models (free, requires Ollama + more VRAM):**

    python run.py --preset qwen3-8b
    python run.py --preset gemma4-26b          # MoE, runs at ~8B speed
    python run.py --preset deepseek-r1-8b      # Reasoning model

**3. Budget cloud models (requires OpenRouter API key, pennies per run):**

    export OPENROUTER_API_KEY=your-key-here
    python run.py --preset llama-4-scout       # ~$0.05/run
    python run.py --preset deepseek-v4-flash   # ~$0.05/run — best value
    python run.py --preset llama-4-maverick    # ~$0.10/run

**4. Mid-tier cloud models:**

    python run.py --preset grok-4-fast         # ~$0.08/run
    python run.py --preset deepseek-v4-pro     # ~$0.14/run — 49B active
    python run.py --preset mistral-large-3     # ~$0.24/run — 41B active, Apache 2.0
    python run.py --preset gpt-4.1-mini        # ~$0.26/run
    python run.py --preset gemini-2.5-flash    # ~$0.40/run

**5. Frontier cloud models:**

    python run.py --preset gemini-3.1-pro      # ~$1.90/run — 94.3% GPQA Diamond
    python run.py --preset grok-4              # ~$2.40/run
    python run.py --preset claude-sonnet-4.6   # ~$2.40/run
    python run.py --preset claude-opus-4.7     # ~$4.00/run — 87.6% SWE-bench
    python run.py --preset gpt-5.5             # ~$4.80/run — 82.7% Terminal-Bench

**6. Full sweep and compare:**

    python run.py --sweep                      # All presets
    python run.py --sweep finetuned base-qwen3-1.7b deepseek-v4-flash gpt-5.5  # Selected
    python report.py --compare results/raw/*.json
    python report.py --all --detailed --group-name "Frontier" --output results/reports/frontier-comparison.md

### Expected Results by Model Size

| Size Class | Expected Overall | Strengths | Weaknesses |
|------------|-----------------|-----------|------------|
| 1.7B base | 20-35 | — | Everything (no theological training) |
| 1.7B fine-tuned | 65-80 | Catechism recall, doctrinal positions | Comparative theology, long explanations |
| 2-4B open | 30-50 | Basic knowledge | Lack of Reformed specificity |
| 8B open | 40-60 | Broad knowledge, reasonable positions | May not know confessional content |
| 8B+ reasoning | 50-70 | Error detection, logical analysis | May not know confessional content |
| Mid-tier cloud | 55-75 | Good general theology | May be vague on Reformed distinctives |
| Frontier cloud | 70-90 | Comparative theology, nuanced analysis | May be diplomatically vague on positions |

### Cost Summary

| Preset | OpenRouter Model ID | Input/M | Output/M | Est./run |
|--------|-------------------|---------|----------|----------|
| **Local models** | — | — | — | **Free** |
| llama-4-scout | `meta-llama/llama-4-scout` | $0.08 | $0.30 | ~$0.05 |
| deepseek-v4-flash | `deepseek/deepseek-v4-flash` | $0.14 | $0.28 | ~$0.05 |
| llama-4-maverick | `meta-llama/llama-4-maverick` | $0.15 | $0.60 | ~$0.10 |
| grok-4-fast | `x-ai/grok-4-fast` | $0.20 | $0.50 | ~$0.08 |
| deepseek-v4-pro | `deepseek/deepseek-v4-pro` | $0.44 | $0.87 | ~$0.14 |
| qwen3.6-35b | `qwen/qwen3.6-35b-a3b` | $0.15 | $1.00 | ~$0.16 |
| mistral-large-3 | `mistralai/mistral-large-2512` | $0.50 | $1.50 | ~$0.24 |
| gpt-4.1-mini | `openai/gpt-4.1-mini` | $0.40 | $1.60 | ~$0.26 |
| gemini-2.5-flash | `google/gemini-2.5-flash` | $0.30 | $2.50 | ~$0.40 |
| gemini-3.1-pro | `google/gemini-3.1-pro-preview` | $2.00 | $12.00 | ~$1.90 |
| grok-4 | `x-ai/grok-4` | $3.00 | $15.00 | ~$2.40 |
| claude-sonnet-4.6 | `anthropic/claude-sonnet-4.6` | $3.00 | $15.00 | ~$2.40 |
| claude-opus-4.7 | `anthropic/claude-opus-4.7` | $5.00 | $25.00 | ~$4.00 |
| gpt-5.5 | `openai/gpt-5.5` | $5.00 | $30.00 | ~$4.80 |

**Full sweep cost:** ~$26 for all 22 models (8 local + 14 cloud) including judge scoring.
Without frontier models: ~$16. Without judge: subtract ~$9.

Judge model (Gemini 2.5 Flash) adds ~$0.40 per run when enabled.

## Configuration

Edit `config.yaml` to configure the LLM judge, scoring parameters, and model presets:

```yaml
judge:
  backend: api
  api_url: https://openrouter.ai/api/v1
  model: google/gemini-2.5-flash
  # api_key: your-key-here  # or set OPENROUTER_API_KEY env var
scoring:
  temperature: 0.3
  max_tokens: 512
  semantic_threshold: 0.6
```

- `judge.api_url` — Any OpenAI-compatible API (Ollama, OpenRouter, OpenAI)
- `judge.model` — The model used for LLM-as-judge evaluations (default: Gemini 2.5 Flash on OpenRouter)
- `judge.api_key` — API key for the judge endpoint (or set `OPENROUTER_API_KEY` / `OPENAI_API_KEY` env var)
- `scoring.semantic_threshold` — Minimum similarity score for catechism recall (0.0-1.0)
- `scoring.temperature` — Sampling temperature for model queries
- `scoring.max_tokens` — Maximum response length

See `config.yaml` for the full list of model presets.

## Adding Custom Questions

The question bank is generated by `build_benchmark.py` from creed JSON files in `../data/raw/creeds/`. To add questions:

1. **From a new creed/catechism**: Add the JSON file to `../data/raw/creeds/` following the existing format (`{Number, Question, Answer}` for catechisms or `{Chapter, Sections: [{Section, Content}]}` for confessions), then update the appropriate builder function in `build_benchmark.py`.

2. **Hand-crafted questions**: Add them directly in the relevant builder function in `build_benchmark.py` (e.g., `build_doctrinal_position()`, `build_error_detection()`).

After changes, regenerate with `python build_benchmark.py`. The `benchmark.json` schema:

```json
{
  "version": "1.0",
  "categories": {
    "category_name": {
      "description": "...",
      "weight": 0.25,
      "scoring_method": "semantic_similarity"
    }
  },
  "questions": [
    {
      "id": "category_name_001",
      "category": "category_name",
      "question": "...",
      "expected_answer": "...",
      "scoring": { "method": "semantic_similarity", "phrases": [...], "concepts": [...] },
      "source": "Westminster Shorter Catechism Q1",
      "difficulty": "standard"
    }
  ]
}
```

## How It Works

1. **Load questions** — Read `benchmark.json` (generated from creed JSON files)
2. **Query model** — Send each question to the target model via the selected backend (local or API)
3. **Automated scoring** — Score each response using the category's method (semantic similarity, position detection, or reference check)
4. **LLM judge** (optional) — For complex categories, an LLM judge evaluates theological accuracy on a 0-100 scale with justification
5. **Save results** — Write scored results to `results/raw/{model}_{timestamp}.json`
6. **Report** — Print a formatted report with per-category breakdown and overall weighted score

## Confessional Sources

Questions are drawn from these Reformed confessional documents:

- **Westminster Standards** (1647) — Westminster Shorter Catechism, Larger Catechism, and Confession of Faith
- **Three Forms of Unity** — Heidelberg Catechism (1563), Belgic Confession (1561), Canons of Dort (1619)
- **1689 London Baptist Confession** — The Baptist adaptation of the Westminster/Savoy tradition
- **Puritan Catechism** (C.H. Spurgeon) and **Keach's Catechism** (Benjamin Keach, 1693)
- **Hand-crafted questions** — TULIP, Five Solas, biblical reference, error detection (Arminianism, Roman Catholic distinctives, liberal theology, Pelagianism, open theism, Arianism, Amyraldism, Federal Vision, NPP, Barthian neo-orthodoxy, Molinism), and comparative theology
