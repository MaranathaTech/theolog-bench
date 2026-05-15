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

Pre-defined groups for common testing scenarios (all run via OpenRouter by default):

    python run.py --list-groups          # See all groups
    python run.py --group 12gb           # Small models, ≤14B (12GB VRAM tier, ~$0.10)
    python run.py --group 24gb           # Medium models, 24-35B (24GB VRAM tier, ~$0.50)
    python run.py --group 48gb           # Large models, 70B (48GB VRAM tier, ~$0.20)
    python run.py --group 96gb           # XL models, 100-128B (96GB VRAM tier, ~$1.00)
    python run.py --group budget         # Cheapest cloud models (~$0.40)
    python run.py --group mid            # Mid-tier cloud (~$2.00)
    python run.py --group frontier       # Top models (~$17)
    python run.py --group cloud          # All cloud models (~$21)
    python run.py --group all            # Everything (~$21)
    python run.py --group finetune-compare  # Just base vs fine-tuned (free, local)

    # Run any group locally via Ollama instead of OpenRouter:
    python run.py --group 24gb --local   # Requires models pulled in Ollama

## Model Test Matrix

theolog-bench includes pre-configured presets for testing across model sizes and providers.
List them with:

    python run.py --list-presets

### Recommended Test Progression

All groups run via OpenRouter by default. Add `--local` to run open-weight models via Ollama instead.

**1. Small open-weight models — 12GB VRAM tier (~$0.10 via OpenRouter):**

    python run.py --group 12gb               # Qwen3.5 9B, Phi-4, Gemma4 26B MoE
    python run.py --group 12gb --local       # Same models via Ollama (free)

**2. Medium open-weight models — 24GB VRAM tier (~$0.50 via OpenRouter):**

    python run.py --group 24gb               # 24-35B models: Gemma, Qwen, Mistral, GLM
    python run.py --group 24gb --local       # Same via Ollama on RTX 3090/4090/5090

**3. Large open-weight models — 48GB VRAM tier (~$0.20 via OpenRouter):**

    python run.py --group 48gb               # Llama 3.3 70B, DeepSeek R1 70B

**4. XL open-weight models — 96GB VRAM tier (~$1.00 via OpenRouter):**

    python run.py --group 96gb               # Qwen3.5 122B MoE, Mistral Medium 3.5

**5. Budget cloud models (~$0.40 total):**

    export OPENROUTER_API_KEY=your-key-here
    python run.py --group budget             # Llama 4, DeepSeek V4 Flash, GLM-4.7, MiniMax

**6. Mid-tier cloud models (~$2.00 total):**

    python run.py --group mid                # DeepSeek V4 Pro, GLM-5, Gemini 2.5 Flash, Kimi K2.6, etc.

**7. Frontier cloud models (~$17 total):**

    python run.py --group frontier           # Gemini 3.1 Pro, Grok 4, Claude, GPT-5.5

**8. Full sweep and compare:**

    python run.py --sweep                      # All presets
    python run.py --sweep deepseek-v4-flash glm-5 gpt-5.5  # Selected
    python report.py --compare results/raw/*.json
    python report.py --all --detailed --group-name "Frontier" --output results/reports/frontier-comparison.md

### Expected Results by Model Size

| Size Class | Expected Overall | Strengths | Weaknesses |
|------------|-----------------|-----------|------------|
| 1.7B base | 20-35 | — | Everything (no theological training) |
| 1.7B fine-tuned | 65-80 | Catechism recall, doctrinal positions | Comparative theology, long explanations |
| 2-4B open | 30-50 | Basic knowledge | Lack of Reformed specificity |
| 8-14B open | 40-60 | Broad knowledge, reasonable positions | May not know confessional content |
| 24-32B open | 50-70 | Good knowledge, solid positions | May miss confessional nuance |
| 70B+ open | 55-75 | Strong knowledge, reasoning | May be vague on Reformed distinctives |
| Mid-tier cloud | 55-75 | Good general theology | May be vague on Reformed distinctives |
| Frontier cloud | 70-90 | Comparative theology, nuanced analysis | May be diplomatically vague on positions |

### Cost Summary

| Preset | OpenRouter Model ID | Input/M | Output/M | Est./run |
|--------|-------------------|---------|----------|----------|
| **Local models** | — | — | — | **Free** |
| deepseek-v4-flash | `deepseek/deepseek-v4-flash` | $0.13 | $0.25 | ~$0.05 |
| llama-4-scout | `meta-llama/llama-4-scout` | $0.08 | $0.30 | ~$0.05 |
| glm-4.7 | `z-ai/glm-4.7` | $0.40 | $1.75 | ~$0.06 |
| llama-4-maverick | `meta-llama/llama-4-maverick` | $0.15 | $0.60 | ~$0.10 |
| minimax-m2.7 | `minimax/minimax-m2.7` | $0.26 | $1.20 | ~$0.12 |
| grok-4-fast | `x-ai/grok-4-fast` | $0.20 | $0.50 | ~$0.08 |
| deepseek-v4-pro | `deepseek/deepseek-v4-pro` | $0.43 | $0.87 | ~$0.14 |
| glm-5 | `z-ai/glm-5` | $0.60 | $1.92 | ~$0.25 |
| mistral-large-3 | `mistralai/mistral-large-2512` | $0.50 | $1.50 | ~$0.24 |
| gpt-4.1-mini | `openai/gpt-4.1-mini` | $0.40 | $1.60 | ~$0.26 |
| gemini-2.5-flash | `google/gemini-2.5-flash` | $0.30 | $2.50 | ~$0.40 |
| glm-5.1 | `z-ai/glm-5.1` | $0.98 | $3.08 | ~$0.50 |
| mimo-v2.5-pro | `xiaomi/mimo-v2.5-pro` | $1.00 | $3.00 | ~$0.50 |
| kimi-k2.6 | `moonshotai/kimi-k2.6` | $0.73 | $3.49 | ~$0.55 |
| gemini-3.1-pro | `google/gemini-3.1-pro-preview` | $2.00 | $12.00 | ~$1.90 |
| grok-4 | `x-ai/grok-4.3` | $1.25 | $2.50 | ~$2.40 |
| claude-sonnet-4.6 | `anthropic/claude-sonnet-4.6` | $3.00 | $15.00 | ~$2.40 |
| claude-opus-4.7 | `anthropic/claude-opus-4.7` | $5.00 | $25.00 | ~$4.00 |
| gpt-5.5 | `openai/gpt-5.5` | $5.00 | $30.00 | ~$4.80 |

**Full sweep cost:** ~$32 for all 41 models (8 local + 33 cloud) including judge scoring.
Without frontier models: ~$15. Without judge: subtract ~$13.

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
  max_tokens: 2048
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
