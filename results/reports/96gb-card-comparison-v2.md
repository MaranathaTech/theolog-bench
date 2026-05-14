# theolog-bench: 96GB GPU Models

Comparative evaluation of open-weight LLMs that can run locally on a single
NVIDIA RTX PRO 6000 Blackwell (96GB VRAM) at Q4 quantization.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **Mistral Medium 3.5** | 128B dense | **64.3%** |
| 2 | Qwen3.5 122B-A10B | 122B MoE (10B active) | 59.3% |
| 3 | Llama 3.3 70B Instruct | 70B dense | 59.0% |
| 4 | DeepSeek R1 70B Distill | 70B dense (R1 distill) | 10.3% |

---

## Category Breakdown

| Category (weight) | Mistral Med 3.5 | Qwen3.5 122B | Llama 3.3 70B | DS R1 70B |
|---|---|---|---|---|
| Biblical Reference (15%) | 52.2 | 47.8 | **67.3** | 1.5 |
| Catechism Recall (25%) | **49.5** | 47.7 | 45.7 | 5.3 |
| Comparative Theology (10%) | **91.7** | 87.0 | 83.2 | 58.2 |
| Confessional Knowledge (15%) | **87.8** | 79.6 | 81.0 | 15.8 |
| Doctrinal Position (20%) | **61.1** | 60.0 | 55.4 | 1.7 |
| Error Detection (15%) | **63.8** | 50.2 | 39.8 | 1.7 |

---

## Detailed Analysis

### 1. Mistral Medium 3.5 (128B dense) — 64.3%

**Best overall performer.** Leads in 5 of 6 categories, demonstrating strong
all-around theological understanding. It exhibits high consistency with only
18 severe failures (score < 20) out of 270 questions and just 7 zeros.

- **Strengths**: Comparative theology (91.7%), confessional knowledge (87.8%),
  and error detection (63.8%) — all categories requiring nuanced theological
  reasoning and evaluation. It also leads in the heavily weighted Catechism
  Recall (25%) and Doctrinal Position (20%) categories.
- **Weakness**: Biblical Reference (52.2%) is its weakest category, though still
  a respectable score. Like most general-purpose models, it tends to paraphrase
  rather than quote verbatim from confessional standards in Catechism Recall.
- **Architecture note**: As a dense 128B model, all parameters are active,
  leading to predictable inference behavior. It fits comfortably within 96GB
  VRAM, allowing for ample context windows.

### 2. Qwen3.5 122B-A10B (122B MoE, 10B active) — 59.3%

**Strong performance in high-level reasoning.** This model shows a bimodal
performance pattern, particularly in Catechism Recall, where it has 53 zeros
but also strong scores when it does answer correctly. It has a higher number
of severe failures (55/270) compared to Mistral Medium.

- **Strengths**: Excellent in Comparative Theology (87.0%) and strong in
  Confessional Knowledge (79.6%) and Doctrinal Position (60.0%).
- **Weakness**: Error Detection (50.2%) and Biblical Reference (47.8%) are its
  lowest-scoring categories. The high number of zeros suggests it sometimes
  completely fails to retrieve or formulate an answer.
- **Architecture note**: As an MoE model with only 10B active parameters per
  token, it offers faster inference speeds. However, the full 122B parameters
  must reside in VRAM, requiring approximately 70GB at Q4 quantization.

### 3. Llama 3.3 70B Instruct (70B dense) — 59.0%

**Best at Scripture, strong overall.** Llama 3.3 70B leads decisively in
Biblical Reference (67.3%), suggesting robust training on scriptural texts.
It has a moderate failure rate (33 severe failures, 20 zeros).

- **Strengths**: Biblical Reference (67.3%), Comparative Theology (83.2%), and
  Confessional Knowledge (81.0%). Its ability to cite Scripture accurately is
  a significant advantage.
- **Weakness**: Error Detection (39.8%) is its weakest category, indicating
  potential struggles in identifying subtle theological errors. Catechism
  Recall (45.7%) is also on the lower end among the top models.
- **Architecture note**: At 70B dense, this model is the most memory-efficient
  among the top performers, requiring approximately 40GB VRAM at Q4. This
  leaves significant VRAM free for larger context windows, batching, or running
  other services concurrently.

### 4. DeepSeek R1 70B Distill (70B dense) — 10.3%

**Not suitable for direct theological Q&A.** This model scored zero on 225
of 270 questions (83%), resulting in 232 severe failures. Its overall score
is significantly lower than other models.

- **Root cause**: DeepSeek R1 is designed as a chain-of-thought reasoning model.
  Its outputs are characterized by extensive internal reasoning traces
  (`<think>...</think>` blocks) with minimal, if any, direct final answers.
  The automated scorer's pattern matching is unable to parse this format,
  leading to near-total failure in most categories. The only category with a
  passable score was Comparative Theology (58.2%), likely due to the LLM-as-judge
  component being able to interpret its reasoning.
- **Verdict**: This model would require substantial prompt engineering to
  extract concise answers or a custom scorer designed to interpret its
  chain-of-thought output to be evaluated fairly for direct theological Q&A.
  It is not recommended for this benchmark's current evaluation methodology.

---

## Recommendation

**Mistral Medium 3.5 is the clear choice** for local theological reasoning on
a 96GB card. It demonstrates superior overall performance (64.3%) and leads
in the majority of categories, including the heavily weighted Catechism Recall
and Doctrinal Position. Its low failure rate and consistent performance make
it highly reliable.

If memory efficiency is a primary concern, **Llama 3.3 70B Instruct** is a
strong alternative. At 59.0% overall, it trades only a few percentage points
for significantly less VRAM usage (~40GB), making it ideal for environments
where VRAM is shared or context windows need to be maximized. Its exceptional
Biblical Reference capabilities are also a notable strength.

**Avoid DeepSeek R1 70B Distill** for direct theological Q&A with this
benchmark setup. Its architectural design is incompatible with the current
scoring methodology, leading to effectively unusable results.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 14, 2026.*