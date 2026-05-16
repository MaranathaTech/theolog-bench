# theolog-bench: Budget Cloud Tier

Comparative evaluation of open-weight LLMs available via API, focusing on models
that offer a balance of performance and cost-effectiveness in a cloud-hosted
environment.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **z-ai/glm-4.7** | 358B MoE (32B active) | **76.7%** |
| 2 | deepseek/deepseek-v4-flash | MoE (13B active) | 72.8% |
| 3 | minimax/minimax-m2.7 | 230B MoE (10B active) | 67.4% |
| 4 | meta-llama/llama-4-maverick | 400B MoE (17B active) | 67.0% |
| 5 | meta-llama/llama-4-scout | 17B MoE | 62.6% |

---

## Category Breakdown

| Category (weight) | z-ai/glm-4.7 | deepseek/v4-flash | minimax/m2.7 | llama-4-maverick | llama-4-scout |
|---|---|---|---|---|---|
| Biblical Reference (15%) | 67.9 | 67.2 | **70.5** | 64.8 | 64.3 |
| Catechism Recall (25%) | **67.1** | 52.3 | 42.9 | 51.7 | 43.8 |
| Comparative Theology (10%) | 95.8 | **97.1** | 96.0 | 90.8 | 88.0 |
| Confessional Knowledge (15%) | 86.0 | **96.0** | 81.3 | 84.2 | 68.0 |
| Doctrinal Position (20%) | **66.3** | 52.5 | 53.6 | 56.2 | 63.2 |
| Error Detection (15%) | 93.5 | **100.0** | 90.7 | 76.2 | 69.0 |

---

## Detailed Analysis

### 1. z-ai/glm-4.7 (358B MoE, 32B active) — 76.7%

**Top performer overall.** Demonstrates strong performance across the board, leading in two key categories: Catechism Recall (67.1%) and Doctrinal Position (66.3%). It also shows excellent ability in higher-order reasoning tasks like Comparative Theology (95.8%) and Error Detection (93.5%). With only 15 severe failures out of 270 questions, it exhibits high consistency.

- **Strengths**: Catechism Recall (67.1%), Doctrinal Position (66.3%), Comparative Theology (95.8%), and Error Detection (93.5%). Its low number of severe failures (15) indicates reliability.
- **Weaknesses**: While leading in Catechism Recall and Doctrinal Position, these are its relatively weaker categories compared to its top scores in other areas.
- **Architecture note**: A large 358B MoE model with 32B active parameters, suggesting a powerful architecture capable of nuanced theological understanding.

### 2. deepseek/deepseek-v4-flash (MoE, 13B active) — 72.8%

**Exceptional in detection and comparison.** This model achieves a perfect 100.0% in Error Detection and leads in Comparative Theology (97.1%) and Confessional Knowledge (96.0%). Its performance in these critical reasoning categories is outstanding. However, it shows a noticeable drop in Catechism Recall and Doctrinal Position.

- **Strengths**: Error Detection (100.0%), Comparative Theology (97.1%), and Confessional Knowledge (96.0%) are all top-tier, indicating strong analytical and evaluative capabilities.
- **Weaknesses**: Catechism Recall (52.3%) and Doctrinal Position (52.5%) are its lowest scores, suggesting it may struggle with direct recall or precise articulation of specific doctrinal stances compared to its strong reasoning abilities.
- **Architecture note**: An MoE model with 13B active parameters, indicating an efficient architecture that can deliver high performance in specific areas despite a smaller active parameter count.

### 3. minimax/minimax-m2.7 (230B MoE, 10B active) — 67.4%

**Strong in Biblical Reference and higher-order reasoning.** This model leads in Biblical Reference (70.5%) and performs very well in Comparative Theology (96.0%) and Error Detection (90.7%). Its lower score in Catechism Recall (42.9%) and Doctrinal Position (53.6%) pulls down its overall average.

- **Strengths**: Biblical Reference (70.5%), Comparative Theology (96.0%), and Error Detection (90.7%).
- **Weaknesses**: Catechism Recall (42.9%) and Doctrinal Position (53.6%) are its weakest points, with 17 zeros in Catechism Recall.
- **Architecture note**: A 230B MoE model with only 10B active parameters, suggesting a highly optimized architecture for inference speed, though this might impact consistency in direct recall tasks.

### 4. meta-llama/llama-4-maverick (400B MoE, 17B active) — 67.0%

**Consistent performer with low failure rate.** While not leading in any category, Llama-4-Maverick shows solid performance across the board, particularly in Comparative Theology (90.8%) and Confessional Knowledge (84.2%). It has the lowest number of severe failures (13) and zeros (4) among all models, indicating high reliability.

- **Strengths**: High consistency with the fewest severe failures (13) and zeros (4). Strong in Comparative Theology (90.8%) and Confessional Knowledge (84.2%).
- **Weaknesses**: Catechism Recall (51.7%) and Doctrinal Position (56.2%) are its relatively weaker areas.
- **Architecture note**: A very large 400B MoE model with 17B active parameters, providing a robust foundation for general theological understanding and reliability.

### 5. meta-llama/llama-4-scout (17B MoE) — 62.6%

**Entry-level performance.** As the smallest model tested, Llama-4-Scout provides a baseline performance. It performs reasonably well in Comparative Theology (88.0%) but struggles significantly in Confessional Knowledge (68.0%) and Error Detection (69.0%) compared to its larger counterparts.

- **Strengths**: Comparative Theology (88.0%) is its strongest category, showing some ability in complex reasoning.
- **Weaknesses**: Confessional Knowledge (68.0%), Error Detection (69.0%), and Catechism Recall (43.8%) are notably lower than other models, indicating limitations in depth of knowledge and nuanced understanding.
- **Architecture note**: A 17B MoE model, representing a more compact and potentially cost-effective option, but with expected trade-offs in overall performance.

---

## Scoring Notes

- Doctrinal Position and Error Detection (35% combined) use regex pattern matching that favors direct affirm/deny answers over balanced multi-perspective responses — models that hedge or present comparative views may score lower than their understanding warrants.
- Catechism Recall (25%) rewards near-verbatim recall of catechism phrasing, giving a natural advantage to models trained on Reformed source texts.

---

## Recommendation

**z-ai/glm-4.7 is the top recommendation** for a budget cloud tier model. It offers the highest overall score (76.7%) and demonstrates strong, consistent performance across all categories, leading in Catechism Recall and Doctrinal Position, and performing exceptionally well in higher-order reasoning tasks. Its low failure rate makes it a reliable choice.

For tasks heavily focused on **error detection and comparative theology**, **deepseek/deepseek-v4-flash** is an excellent alternative, achieving perfect scores in Error Detection and leading in Comparative Theology and Confessional Knowledge. However, users should be aware of its relatively weaker performance in direct recall tasks.

If **Biblical Reference** is a primary concern, **minimax/minimax-m2.7** stands out with the highest score in that category (70.5%), while still offering strong performance in other reasoning tasks.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 16, 2026.*