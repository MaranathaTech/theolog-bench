# theolog-bench: Budget Cloud Models

Comparative evaluation of open-weight LLMs available via API, focusing on
cost-effective models suitable for theological reasoning tasks.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **minimax/minimax-m2.7** | 230B MoE (10B active) | **52.9%** |
| 2 | deepseek/deepseek-v4-flash | MoE (13B active) | 52.6% |
| 3 | meta-llama/llama-4-maverick | 400B MoE (17B active) | 52.5% |
| 4 | meta-llama/llama-4-scout | 17B MoE | 50.1% |
| 5 | z-ai/glm-4.7 | 358B MoE (32B active) | 27.1% |

---

## Category Breakdown

| Category (weight) | minimax/minimax-m2.7 | deepseek/deepseek-v4-flash | meta-llama/llama-4-maverick | meta-llama/llama-4-scout | z-ai/glm-4.7 |
|---|---|---|---|---|---|
| Catechism Recall (25%) | **24.4** | 15.6 | **24.4** | 10.9 | 24.2 |
| Confessional Knowledge (15%) | 73.3 | **82.6** | 70.0 | 64.6 | 49.4 |
| Doctrinal Position (20%) | 42.4 | 54.5 | **63.0** | 57.9 | 19.8 |
| Biblical Reference (15%) | 48.3 | 50.6 | 58.1 | **60.5** | 13.3 |
| Error Detection (15%) | **77.5** | 69.0 | 37.8 | 56.8 | 6.7 |
| Comparative Theology (10%) | 85.0 | 74.8 | **89.2** | 85.0 | 66.8 |

---

## Detailed Analysis

### 1. minimax/minimax-m2.7 (230B MoE, 10B active) — 52.9%

**Top performer by a narrow margin.** This model shows a balanced performance
across categories, leading in Error Detection (77.5%) and performing strongly
in Comparative Theology (85.0%) and Confessional Knowledge (73.3%). It has the
lowest number of severe failures (72/270) and zeros (59) among the top three,
indicating more consistent output.

- **Strengths**: Error Detection (77.5%), Comparative Theology (85.0%), and
  Confessional Knowledge (73.3%) — categories requiring nuanced understanding
  and evaluation.
- **Weakness**: Doctrinal Position (42.4%) and Catechism Recall (24.4%) are its
  lowest scores, suggesting it struggles with precise articulation of specific
  doctrines and verbatim recall.
- **Architecture note**: A large 230B MoE model with 10B active parameters,
  offering a good balance of performance for its likely cost-tier.

### 2. deepseek/deepseek-v4-flash (MoE, 13B active) — 52.6%

**Strong in confessional knowledge.** This model is a close second overall,
distinguishing itself by leading in the Confessional Knowledge category (82.6%).
It also performs well in Error Detection (69.0%) and Comparative Theology (74.8%).
However, it has a higher rate of severe failures (102/270) and zeros (98) compared
to minimax/minimax-m2.7.

- **Strengths**: Confessional Knowledge (82.6%), Comparative Theology (74.8%),
  and Error Detection (69.0%).
- **Weakness**: Catechism Recall (15.6%) is its weakest category, indicating
  difficulty with precise memorization or reproduction of confessional texts.
  Biblical Reference (50.6%) is also relatively low.
- **Architecture note**: An MoE model with 13B active parameters, providing
  efficient inference for its performance level.

### 3. meta-llama/llama-4-maverick (400B MoE, 17B active) — 52.5%

**Best in comparative theology and doctrinal position.** This model ties for
the best Catechism Recall (24.4%) and leads decisively in Comparative Theology
(89.2%) and Doctrinal Position (63.0%), which are important weighted categories.
However, its performance in Error Detection (37.8%) is notably weak, contributing
to its slightly lower overall score despite strengths elsewhere. It shares a
similar failure rate (107 severe failures, 98 zeros) with deepseek-v4-flash.

- **Strengths**: Comparative Theology (89.2%), Doctrinal Position (63.0%), and
  Biblical Reference (58.1%).
- **Weakness**: Error Detection (37.8%) is a significant weakness, suggesting
  it struggles to reliably identify heterodox statements.
- **Architecture note**: A very large 400B MoE model with 17B active parameters,
  indicating a substantial underlying knowledge base.

### 4. meta-llama/llama-4-scout (17B MoE) — 50.1%

**Best at biblical reference.** This smaller Llama model leads all tested models
in Biblical Reference (60.5%), suggesting a strong understanding or recall of
scriptural passages. It also performs well in Comparative Theology (85.0%).
However, it has the lowest Catechism Recall (10.9%) among all models, and a high
number of severe failures (107/270) and zeros (99).

- **Strengths**: Biblical Reference (60.5%) and Comparative Theology (85.0%).
- **Weakness**: Catechism Recall (10.9%) is a significant area for improvement.
  Error Detection (56.8%) is also not as strong as the top two models.
- **Architecture note**: A smaller 17B MoE model, likely designed for efficiency
  and specific tasks, which aligns with its strong Biblical Reference score.

### 5. z-ai/glm-4.7 (358B MoE, 32B active) — 27.1%

**Not suitable for this task.** This model performed significantly lower than
the others, with an overall score of 27.1%. It exhibited a very high number of
severe failures (169/270) and zeros (166), indicating a general inability to
answer most questions effectively within the benchmark's scoring parameters.

- **Root cause**: While it shows some capability in Comparative Theology (66.8%)
  and Catechism Recall (24.2%), its scores in critical categories like Biblical
  Reference (13.3%) and Error Detection (6.7%) are extremely low. This suggests
  a fundamental mismatch with the theological reasoning requirements of the benchmark.
- **Verdict**: Not recommended for Reformed theological evaluation based on these
  results.

---

## Recommendation

For budget-conscious cloud deployments focused on Reformed theological reasoning,
**minimax/minimax-m2.7 is the recommended choice.** It offers the most balanced
performance, leading in a key category (Error Detection) and demonstrating
consistent output with the fewest severe failures. Its overall score of 52.9%
places it marginally above its closest competitors.

If strong Confessional Knowledge is a priority, **deepseek/deepseek-v4-flash**
is a strong alternative, leading in that category with 82.6%.

For tasks heavily reliant on Comparative Theology or Doctrinal Position,
**meta-llama/llama-4-maverick** excels, but its weakness in Error Detection
should be considered.

**Avoid z-ai/glm-4.7** for general theological Q&A, as its performance is
significantly below the other models tested.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 15, 2026.*