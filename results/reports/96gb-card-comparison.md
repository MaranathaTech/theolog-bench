# theolog-bench: Models That Fit on a 96GB GPU

Comparative evaluation of open-weight LLMs that can run locally on a single
NVIDIA RTX PRO 6000 Blackwell (96GB VRAM) at Q4 quantization.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | VRAM (Q4) | Overall |
|---|---|---|---|---|
| 1 | **Mistral Medium 3.5** | 128B dense | ~70 GB | **66.5%** |
| 2 | Llama 3.3 70B | 70B dense | ~40 GB | 63.9% |
| 3 | Qwen3.5 122B-A10B | 122B MoE (10B active) | ~70 GB | 60.3% |
| 4 | DeepSeek R1 70B Distill | 70B dense | ~40 GB | 10.3% |

---

## Category Breakdown

| Category (weight) | Mistral Med 3.5 | Llama 3.3 70B | Qwen3.5 122B | DS R1 70B |
|---|---|---|---|---|
| Catechism Recall (25%) | **49.5** | 45.7 | 47.7 | 5.3 |
| Confessional Knowledge (15%) | **87.8** | 81.0 | 79.6 | 15.8 |
| Doctrinal Position (20%) | **62.4** | 59.0 | 56.6 | 1.7 |
| Biblical Reference (15%) | 52.2 | **67.3** | 47.8 | 1.5 |
| Error Detection (15%) | **76.2** | 67.7 | 61.8 | 1.7 |
| Comparative Theology (10%) | **91.7** | 83.2 | 87.0 | 58.2 |

---

## Detailed Analysis

### 1. Mistral Medium 3.5 (128B dense) — 66.5%

**Best overall performer.** Leads in 5 of 6 categories. Its key advantage is
consistency: only 18 severe failures (score < 20) out of 270 questions, and
just 1 zero in catechism recall.

- **Strengths**: Comparative theology (91.7%), confessional knowledge (87.8%),
  and error detection (76.2%) — all requiring nuanced theological reasoning.
- **Weakness**: Catechism recall (49.5%) — like all general-purpose models, it
  paraphrases rather than quoting verbatim from confessional standards.
- **Architecture note**: Dense 128B means all parameters are active every token.
  No MoE routing means deterministic inference behavior and simpler deployment.
  Fits comfortably in 96GB with room for 8K+ context windows.

### 2. Llama 3.3 70B Instruct (70B dense) — 63.9%

**Best at Scripture, strong runner-up.** Leads decisively in biblical reference
(67.3% vs next best 52.2%), suggesting strong training on Bible text. Moderate
failure rate (33 severe failures). Strong error detection (67.7%) shows it can
identify heterodox statements reliably.

- **Strengths**: Biblical reference (67.3%), confessional knowledge (81.0%),
  and error detection (67.7%).
- **Weakness**: Catechism recall (45.7%) — weakest among the top 3 at verbatim
  recall, though the gap is small.
- **Architecture note**: At 70B dense and ~40GB Q4, this is the most
  memory-efficient option. Leaves 56GB free for context, batching, or running
  alongside other services.

### 3. Qwen3.5 122B-A10B (122B MoE, 10B active) — 60.3%

**Bimodal performance.** Shows a striking all-or-nothing pattern in catechism
recall: 31 zeros but also 31 scores at 80+. When it knows an answer, it knows
it well; when it doesn't, it fails completely. Total of 55 severe failures.

- **Strengths**: Comparative theology (87.0%) and confessional knowledge (79.6%).
- **Weakness**: Error detection (61.8%) — improved after scorer fixes but still
  weakest of the top 3. Struggles with multi-view responses that discuss
  heterodox positions alongside Reformed teaching.
- **Architecture note**: MoE with only 10B active parameters per token means
  fast inference (~3x faster than 70B dense for the same quality tier), but the
  full 122B must reside in VRAM (~70GB at Q4).

### 4. DeepSeek R1 70B Distill (70B dense) — 10.3%

**Not suitable for this task.** Scored zero on 225 of 270 questions (83%).
Only 232 severe failures — essentially a total failure on automated scoring.

- **Root cause**: DeepSeek R1 is a chain-of-thought reasoning model. Its
  outputs are dominated by lengthy internal reasoning traces (`<think>...</think>`
  blocks) with minimal final answers. The automated scorer's pattern matchers
  cannot parse this format. The only passable scores came from judge-evaluated
  categories (comparative theology: 58.2%) where the LLM judge could interpret
  the reasoning output.
- **Verdict**: Would require significant prompt engineering or scorer adaptation
  to evaluate fairly. Not recommended for direct theological Q&A without a
  wrapper that extracts final answers from reasoning traces.

---

## Context: How These Compare to Cloud Models

For reference, the top cloud-only models scored (all re-scored with updated
scorer v2):

| Model | Overall | Runnable Locally? |
|---|---|---|
| Claude Opus 4.7 | 73.9% | No (proprietary, ~2-5T params) |
| GPT-5.5 | 70.7% | No (proprietary) |
| Grok 4 Fast | 69.4% | No (proprietary, ~3T MoE) |
| Claude Sonnet 4.6 | 69.0% | No (proprietary) |
| GPT-4.1 Mini | 68.9% | No (proprietary, ~7B) |
| Mistral Large 3 | 66.9% | No (675B MoE, needs ~350GB) |
| **Mistral Medium 3.5** | **66.5%** | **Yes — 96GB card** |

Mistral Medium 3.5 at 66.5% is within 0.4 points of its larger sibling
(Mistral Large 3 at 66.9%), within 2.4 points of the cheapest cloud model
that beats it (GPT-4.1 Mini at 68.9%), and within 7.4 points of the frontier
(Claude Opus 4.7 at 73.9%).

---

## Recommendation

**Mistral Medium 3.5 is the clear choice** for local theological reasoning on
a 96GB card. It nearly matches Mistral Large 3's performance at 1/5 the memory
footprint, leads in 5 of 6 categories among local-capable models, and has the
lowest failure rate.

If memory efficiency matters more than peak score (e.g., running alongside
other services), **Llama 3.3 70B** at 40GB is a strong alternative — it
trades only 2.6 points overall for 30GB less VRAM, has the best Scripture
citation ability of any model tested, and strong error detection.

**Avoid DeepSeek R1 70B Distill** for direct theological Q&A — its
chain-of-thought format is incompatible with standard evaluation.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 14, 2026.*
