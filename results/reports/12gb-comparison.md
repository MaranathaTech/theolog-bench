# theolog-bench: 12GB VRAM Tier

Comparative evaluation of open-weight LLMs that can run locally on a single
NVIDIA RTX 3060 (12GB VRAM) at Q4 quantization.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **google/gemma-4-26b-a4b-it** | 26B MoE, 4B active | **67.5%** |
| 2 | qwen/qwen3.5-9b | 9B dense | 63.1% |
| 3 | microsoft/phi-4 | 14B dense | 55.6% |

---

## Category Breakdown

| Category (weight) | google/gemma-4-26b-a4b-it | qwen/qwen3.5-9b | microsoft/phi-4 |
|---|---|---|---|
| Biblical Reference (15%) | 66.6 | **69.3** | 54.6 |
| Catechism Recall (25%) | 45.6 | **46.0** | 37.3 |
| Comparative Theology (10%) | **96.2** | 89.9 | 89.0 |
| Confessional Knowledge (15%) | **84.0** | 46.3 | 75.0 |
| Doctrinal Position (20%) | 52.9 | **54.4** | 36.5 |
| Error Detection (15%) | 89.0 | **95.7** | 70.7 |

---

## Detailed Analysis

### 1. google/gemma-4-26b-a4b-it (26B MoE, 4B active) — 67.5%

**Best overall performer.** Leads in 3 of 6 categories, including the highly weighted Confessional Knowledge (15%) and Comparative Theology (10%). It exhibits the lowest failure rate among the models tested, with only 13 severe failures (<20) and 7 zeros out of 270 questions.

- **Strengths**: Comparative Theology (96.2%), Error Detection (89.0%), and Confessional Knowledge (84.0%) — demonstrating strong nuanced theological reasoning and accurate identification of orthodox positions.
- **Weakness**: Doctrinal Position (52.9%) and Catechism Recall (45.6%) — struggles somewhat with direct affirmation/denial of specific doctrinal stances and verbatim recall of confessional texts.
- **Architecture note**: As a 26B MoE model with only 4B active parameters, it offers a good balance of performance and efficiency, fitting comfortably within the 12GB VRAM limit.

### 2. qwen/qwen3.5-9b (9B dense) — 63.1%

**Strong contender with excellent error detection.** This model leads in 3 categories, notably Biblical Reference (69.3%), Catechism Recall (46.0%), and Error Detection (95.7%). Its high score in Error Detection suggests a robust ability to identify heterodox statements. However, it has a higher number of severe failures (50/270) and zeros (46) compared to Gemma.

- **Strengths**: Error Detection (95.7%), Comparative Theology (89.9%), and Biblical Reference (69.3%) — indicating strong capabilities in identifying theological errors and citing Scripture.
- **Weakness**: Confessional Knowledge (46.3%) and Catechism Recall (46.0%) — its performance in these areas is significantly lower than its strengths, suggesting less familiarity with the specific phrasing of confessional standards.
- **Architecture note**: As a 9B dense model, it is the most compact and memory-efficient option, leaving ample VRAM for context or other tasks.

### 3. microsoft/phi-4 (14B dense) — 55.6%

**Solid foundational understanding but weaker recall.** While ranking third overall, Phi-4 demonstrates a respectable understanding in categories like Comparative Theology (89.0%) and Confessional Knowledge (75.0%). It has a moderate failure rate with 27 severe failures and 7 zeros.

- **Strengths**: Comparative Theology (89.0%), Confessional Knowledge (75.0%), and Error Detection (70.7%) — showing a decent grasp of theological concepts and the ability to differentiate between positions.
- **Weakness**: Catechism Recall (37.3%) and Doctrinal Position (36.5%) — these are its lowest scores, indicating difficulty with verbatim recall and direct affirmation of specific doctrinal points, which are crucial for these categories.
- **Architecture note**: A 14B dense model, it represents a larger footprint than Qwen3.5-9b but still fits within the 12GB VRAM, though with less headroom.

---

## Scoring Notes

- **Doctrinal Position and Error Detection (35% combined)** use regex pattern matching that favors direct affirm/deny answers over balanced multi-perspective responses — models that hedge or present comparative views may score lower than their understanding warrants.
- **Catechism Recall (25%)** rewards near-verbatim recall of catechism phrasing, giving a natural advantage to models trained on Reformed source texts.

---

## Recommendation

**google/gemma-4-26b-a4b-it is the clear choice** for local theological reasoning on a 12GB card. It offers the best overall performance, leads in key reasoning-heavy categories like Comparative Theology and Confessional Knowledge, and exhibits the lowest failure rate. Its MoE architecture provides a good balance of capability and VRAM efficiency.

**qwen/qwen3.5-9b** is a strong alternative, especially if superior error detection and biblical referencing are priorities. Its compact 9B dense architecture makes it highly memory-efficient, though it shows a higher incidence of complete failures.

**microsoft/phi-4** provides a foundational understanding but struggles with the specific recall and directness required by some categories, making it less suitable for tasks demanding precise confessional adherence.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 16, 2026.*