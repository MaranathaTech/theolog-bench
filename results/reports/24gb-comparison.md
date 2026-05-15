# theolog-bench: 24GB VRAM Tier

Comparative evaluation of open-weight LLMs that can run locally on a single
NVIDIA RTX 4070 Ti (24GB VRAM) at Q4 quantization.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **qwen/qwen3.6-35b-a3b** | 35B MoE (3B active) | **76.8%** |
| 2 | qwen/qwen3.6-27b | 27B dense | 76.4% |
| 3 | qwen/qwen3.5-27b | 27B dense | 75.9% |
| 4 | google/gemma-4-31b-it | 31B dense | 66.9% |
| 5 | z-ai/glm-4-32b | 32B dense | 66.7% |
| 6 | mistralai/mistral-small-3.2-24b-instruct | 24B dense | 65.6% |
| 7 | google/gemma-3-27b-it | 27B dense | 56.4% |

---

## Category Breakdown

| Category (weight) | qwen/qwen3.6-35b-a3b | qwen/qwen3.6-27b | qwen/qwen3.5-27b | google/gemma-4-31b-it | z-ai/glm-4-32b | mistralai/mistral-small-3.2-24b-instruct | google/gemma-3-27b-it |
|---|---|---|---|---|---|---|---|
| Biblical Reference (15%) | 74.6 | **76.8** | 75.0 | 62.8 | 55.5 | 66.4 | 41.1 |
| Catechism Recall (25%) | 58.5 | 57.1 | **64.8** | 44.8 | 47.1 | 45.3 | 41.1 |
| Comparative Theology (10%) | **97.8** | 97.7 | 92.7 | 92.9 | 88.0 | 90.5 | 81.2 |
| Confessional Knowledge (15%) | 83.2 | 83.7 | **84.5** | **84.5** | 71.6 | 81.3 | 70.2 |
| Doctrinal Position (20%) | **70.9** | 67.7 | 57.7 | 54.1 | 66.3 | 50.1 | 47.4 |
| Error Detection (15%) | 97.3 | 98.3 | **100.0** | 89.8 | 92.0 | 86.8 | 78.7 |

---

## Detailed Analysis

### 1. qwen/qwen3.6-35b-a3b (35B MoE, 3B active) — 76.8%

**Top performer in the 24GB tier.** This model demonstrates excellent performance, leading in the crucial Doctrinal Position category (20% weight) with 70.9% and tying for best in Comparative Theology (10% weight) with 97.8%. It has the lowest number of severe failures (10/270) and zeros (4) among all models, indicating high reliability.

- **Strengths**: Exceptional in Comparative Theology (97.8%) and Error Detection (97.3%), both requiring sophisticated theological discernment. Strong in Confessional Knowledge (83.2%) and Doctrinal Position (70.9%).
- **Weakness**: Catechism Recall (58.5%) is its weakest category, though still respectable for a general-purpose model.
- **Architecture note**: As a 35B MoE with only 3B active parameters, it offers a balance of performance and efficiency, fitting well within the 24GB VRAM limit.

### 2. qwen/qwen3.6-27b (27B dense) — 76.4%

**Strong runner-up, excelling in Biblical Reference.** This dense model from Qwen is a close second, showcasing superior Biblical Reference (15% weight) with 76.8%. It also performs exceptionally well in Error Detection (98.3%) and Comparative Theology (97.7%).

- **Strengths**: Leads in Biblical Reference (76.8%), indicating strong scriptural grounding. Excellent in Error Detection (98.3%) and Comparative Theology (97.7%).
- **Weakness**: Catechism Recall (57.1%) is its lowest score, similar to its MoE sibling.
- **Architecture note**: A 27B dense model, it provides consistent performance across the board, with a slightly higher number of severe failures (15/270) and zeros (9) compared to the top model.

### 3. qwen/qwen3.5-27b (27B dense) — 75.9%

**Consistent and reliable, with perfect error detection.** Another strong contender from Qwen, this model achieves a perfect 100.0% in Error Detection (15% weight) and leads in Catechism Recall (25% weight) with 64.8%. It also ties for best in Confessional Knowledge (15% weight) with 84.5%.

- **Strengths**: Unmatched Error Detection (100.0%) and best in Catechism Recall (64.8%). Strong in Confessional Knowledge (84.5%) and Comparative Theology (92.7%).
- **Weakness**: Doctrinal Position (57.7%) is its weakest category, significantly lower than its Qwen 3.6 counterparts.
- **Architecture note**: A 27B dense model, it shows a good balance of capabilities, with a low number of severe failures (12/270) and zeros (9).

### 4. google/gemma-4-31b-it (31B dense) — 66.9%

**Solid mid-tier performer with strong confessional knowledge.** This Gemma model provides a respectable overall score, tying for best in Confessional Knowledge (15% weight) with 84.5%. It also has the lowest number of zeros (1) among all models.

- **Strengths**: Excellent in Confessional Knowledge (84.5%) and Comparative Theology (92.9%). Very low failure rate with only 9 severe failures and 1 zero.
- **Weakness**: Catechism Recall (44.8%) and Doctrinal Position (54.1%) are significantly lower than the Qwen models.
- **Architecture note**: A 31B dense model, it offers a reliable, if not top-tier, performance for its size.

### 5. z-ai/glm-4-32b (32B dense) — 66.7%

**Competent across categories, but not outstanding.** This model from Zhipu AI delivers a consistent performance, particularly in Error Detection (92.0%) and Comparative Theology (88.0%).

- **Strengths**: Good performance in Error Detection (92.0%) and Comparative Theology (88.0%).
- **Weakness**: Biblical Reference (55.5%) and Catechism Recall (47.1%) are notable weaknesses, pulling down its overall score.
- **Architecture note**: A 32B dense model, it's a capable option but doesn't lead in any major category. It has a moderate number of severe failures (17/270).

### 6. mistralai/mistral-small-3.2-24b-instruct (24B dense) — 65.6%

**Entry-level performance for the tier.** This Mistral model provides a baseline for the 24GB VRAM category. It shows good ability in Comparative Theology (90.5%) and Error Detection (86.8%).

- **Strengths**: Strong in Comparative Theology (90.5%) and Error Detection (86.8%).
- **Weakness**: Doctrinal Position (50.1%) and Catechism Recall (45.3%) are among the lowest in the tier.
- **Architecture note**: As a 24B dense model, it's one of the smaller models in this comparison, which might contribute to its lower overall score. It has the highest number of severe failures (18/270).

### 7. google/gemma-3-27b-it (27B dense) — 56.4%

**Lowest performer in this tier.** This older Gemma model struggles significantly compared to the other models, particularly in the heavily weighted Catechism Recall and Doctrinal Position categories.

- **Strengths**: Its best categories are Comparative Theology (81.2%) and Error Detection (78.7%), but these are still lower than other models.
- **Weakness**: Very weak in Catechism Recall (41.1%) and Biblical Reference (41.1%), which are critical for theological benchmarks.
- **Architecture note**: A 27B dense model, its performance indicates that newer iterations or different architectures are more suitable for this task. It has a high number of severe failures (17/270).

---

## Recommendation

For the 24GB VRAM tier, the **Qwen models are the clear leaders**, offering superior performance across the board.

**qwen/qwen3.6-35b-a3b is the top recommendation** due to its leading overall score (76.8%), lowest failure rate, and strong performance in high-weighted categories like Doctrinal Position and Comparative Theology. Its MoE architecture also suggests potential for efficient inference.

If Catechism Recall and perfect Error Detection are paramount, **qwen/qwen3.5-27b** is an excellent choice, leading in both these categories and tying for best in Confessional Knowledge.

The **Gemma models (especially Gemma 3)** and **Mistral Small** are generally less competitive in this theological benchmark, particularly in core knowledge recall and doctrinal understanding.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 15, 2026.*