# theolog-bench: Mid-Tier Cloud Models

Comparative evaluation of leading cloud-based LLMs, focusing on their performance
across various Reformed theological knowledge domains.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **mistralai/mistral-large-2512** | 675B MoE, 41B active | **75.8%** |
| 2 | z-ai/glm-5 | 744B MoE, 40B active | 74.6% |
| 3 | deepseek/deepseek-v4-pro | 1.6T MoE, 49B active | 73.0% |
| 4 | z-ai/glm-5.1 | proprietary | 72.4% |
| 5 | google/gemini-2.5-flash | proprietary | 72.3% |
| 6 | xiaomi/mimo-v2.5-pro | 1T MoE, 42B active | 70.2% |
| 7 | moonshotai/kimi-k2.6 | 1T MoE, 32B active | 69.2% |
| 8 | openai/gpt-4.1-mini | proprietary | 67.4% |

---

## Category Breakdown

| Category (weight) | Mistral Large 2512 | GLM-5 | DeepSeek v4 Pro | GLM-5.1 | Gemini 2.5 Flash | MiMO v2.5 Pro | Kimi K2.6 | GPT-4.1 Mini |
|---|---|---|---|---|---|---|---|---|
| Biblical Reference (15%) | 70.4 | 60.8 | 67.0 | 59.4 | 70.7 | **72.5** | 71.4 | 59.7 |
| Catechism Recall (25%) | 57.3 | **65.8** | 51.8 | 61.9 | 53.5 | 57.1 | 63.9 | 44.1 |
| Comparative Theology (10%) | 96.6 | 92.2 | 96.8 | 95.5 | 91.7 | **97.0** | 91.7 | 95.3 |
| Confessional Knowledge (15%) | 93.4 | 93.9 | **97.5** | 92.0 | 88.9 | 94.5 | 65.5 | 87.2 |
| Doctrinal Position (20%) | **66.5** | 57.8 | 58.5 | 55.1 | 60.2 | 46.8 | 56.7 | 58.3 |
| Error Detection (15%) | 92.8 | **94.2** | 93.5 | 91.2 | 91.8 | 78.8 | 81.5 | 87.5 |

---

## Detailed Analysis

### 1. mistralai/mistral-large-2512 (675B MoE, 41B active) — 75.8%

**Top performer overall.** Mistral Large 2512 demonstrates strong performance
across the board, leading in the highly-weighted Doctrinal Position category (20%)
with 66.5%. It exhibits a very low failure rate with only 3 severe failures and 2 zeros
out of 270 questions, indicating high reliability.

- **Strengths**: Excels in Doctrinal Position (66.5%), Comparative Theology (96.6%),
  Confessional Knowledge (93.4%), and Error Detection (92.8%). Its ability to
  articulate doctrinal stances and detect errors is particularly strong.
- **Weakness**: Catechism Recall (57.3%) is its weakest category, though still
  a respectable score for a general-purpose model.
- **Architecture note**: A large MoE model with 675B parameters and 41B active,
  it leverages a vast parameter space for nuanced understanding.

### 2. z-ai/glm-5 (744B MoE, 40B active) — 74.6%

**Strong contender with excellent error detection.** GLM-5 is a close second,
distinguishing itself with the highest score in Error Detection (94.2%). It
also performs exceptionally well in Catechism Recall (65.8%), leading all models
in this critical category (25% weight).

- **Strengths**: Leads in Catechism Recall (65.8%) and Error Detection (94.2%).
  Also strong in Confessional Knowledge (93.9%) and Comparative Theology (92.2%).
- **Weakness**: Its scores in Biblical Reference (60.8%) and Doctrinal Position (57.8%)
  are comparatively lower than its other strong categories.
- **Architecture note**: Similar to Mistral Large 2512, this 744B MoE model with
  40B active parameters showcases the power of large-scale sparse architectures.

### 3. deepseek/deepseek-v4-pro (1.6T MoE, 49B active) — 73.0%

**Confessional knowledge powerhouse.** DeepSeek v4 Pro achieves the highest score
in Confessional Knowledge (97.5%), a key category (15% weight), and also leads
in Comparative Theology (96.8%). However, it has a higher number of severe failures
(21) and zeros (15) compared to the top two models.

- **Strengths**: Dominates Confessional Knowledge (97.5%) and Comparative Theology (96.8%).
  Also strong in Error Detection (93.5%).
- **Weakness**: Catechism Recall (51.8%) is its lowest category, and it shows
  a tendency for more complete failures (15 zeros).
- **Architecture note**: The largest model by total parameters at 1.6T MoE with
  49B active, suggesting a broad but potentially less consistent knowledge base.

### 4. z-ai/glm-5.1 (proprietary) — 72.4%

**Consistent performer.** GLM-5.1, a proprietary model, demonstrates solid and
consistent performance across most categories, with no major outliers in its
strengths or weaknesses. Its failure rate is moderate with 14 severe failures
and 9 zeros.

- **Strengths**: Strong in Comparative Theology (95.5%), Confessional Knowledge (92.0%),
  and Error Detection (91.2%).
- **Weakness**: Biblical Reference (59.4%) and Doctrinal Position (55.1%) are
  its lowest scoring categories.
- **Architecture note**: As a proprietary model, specific architectural details
  are not available, but its performance suggests a well-rounded design.

### 5. google/gemini-2.5-flash (proprietary) — 72.3%

**Reliable and balanced.** Gemini 2.5 Flash, also proprietary, delivers a balanced
performance, particularly strong in its ability to detect errors and engage in
comparative theology. It has a similar failure profile to GLM-5.1 with 15 severe
failures and 10 zeros.

- **Strengths**: Excellent in Error Detection (91.8%) and Comparative Theology (91.7%).
  Also performs well in Biblical Reference (70.7%).
- **Weakness**: Catechism Recall (53.5%) and Doctrinal Position (60.2%) are its
  comparatively weaker areas.
- **Architecture note**: Proprietary, but its "Flash" designation suggests an
  emphasis on speed and efficiency, which doesn't seem to compromise its theological
  understanding significantly.

### 6. xiaomi/mimo-v2.5-pro (1T MoE, 42B active) — 70.2%

**Biblical and comparative theology specialist.** MiMO v2.5 Pro stands out as
the best performer in Biblical Reference (72.5%) and Comparative Theology (97.0%).
However, it shows a notable drop in Doctrinal Position (46.8%) and Error Detection (78.8%).

- **Strengths**: Leads in Biblical Reference (72.5%) and Comparative Theology (97.0%).
  Also strong in Confessional Knowledge (94.5%).
- **Weakness**: Significantly lower in Doctrinal Position (46.8%) and Error Detection (78.8%),
  suggesting some difficulty with nuanced theological reasoning and critique.
- **Architecture note**: A 1T MoE model with 42B active parameters, it demonstrates
  that sheer size doesn't always translate to consistent performance across all tasks.

### 7. moonshotai/kimi-k2.6 (1T MoE, 32B active) — 69.2%

**Struggles with confessional knowledge.** Kimi K2.6 shows a significant weakness
in Confessional Knowledge (65.5%), which is a weighted category (15%). It also
has the highest number of severe failures (28) and zeros (26) among all models,
indicating less reliability.

- **Strengths**: Strong in Biblical Reference (71.4%) and Comparative Theology (91.7%).
- **Weakness**: Confessional Knowledge (65.5%) is a major weakness. The high
  number of zeros (26) suggests inconsistent performance.
- **Architecture note**: A 1T MoE model with 32B active parameters, it seems to
  struggle with the depth of confessional understanding compared to its peers.

### 8. openai/gpt-4.1-mini (proprietary) — 67.4%

**Smallest model, lowest recall.** GPT-4.1 Mini, likely the smallest model by
parameter count (~7B), predictably scores lowest overall. Its Catechism Recall
(44.1%) is the lowest among all models, highlighting the challenge for smaller
models in verbatim recall.

- **Strengths**: Despite its size, it performs well in Comparative Theology (95.3%)
  and Error Detection (87.5%), demonstrating strong reasoning capabilities.
- **Weakness**: Catechism Recall (44.1%) is its most significant weakness, and
  it also struggles with Biblical Reference (59.7%).
- **Architecture note**: As a proprietary model, its exact architecture is unknown,
  but its "Mini" designation and performance suggest a highly optimized, smaller
  model that prioritizes reasoning over rote memorization.

---

## Scoring Notes

(a) Doctrinal Position and Error Detection (35% combined) use regex pattern matching
that favors direct affirm/deny answers over balanced multi-perspective responses —
models that hedge or present comparative views may score lower than their
understanding warrants; (b) Catechism Recall (25%) rewards near-verbatim recall
of catechism phrasing, giving a natural advantage to models trained on Reformed
source texts.

---

## Recommendation

**mistralai/mistral-large-2512 is the top recommendation** for general Reformed
theology tasks among mid-tier cloud models. Its leading overall score (75.8%),
strong performance in the high-weighted Doctrinal Position category (66.5%),
and exceptionally low failure rate (3 severe failures) make it the most reliable
and capable option.

For tasks heavily reliant on **Catechism Recall**, **z-ai/glm-5** is a strong
alternative, leading this category with 65.8%. If **Confessional Knowledge** is
paramount, **deepseek/deepseek-v4-pro** excels with 97.5%.

Models like **xiaomi/mimo-v2.5-pro** and **moonshotai/kimi-k2.6** show
specialized strengths but suffer from more pronounced weaknesses in other
critical areas, making them less suitable for broad theological applications.
**openai/gpt-4.1-mini**, while impressive for its likely small size, is
outperformed by its larger peers in this domain.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 16, 2026.*