# theolog-bench: Mid-Tier Cloud Models

Comparative evaluation of mid-tier cloud-hosted LLMs for Reformed theology.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **x-ai/grok-4-fast** | proprietary | **59.5%** |
| 2 | openai/gpt-4.1-mini | proprietary | 58.0% |
| 3 | deepseek/deepseek-v4-pro | 1.6T MoE, 49B active | 56.7% |
| 4 | mistralai/mistral-large-2512 | 675B MoE, 41B active | 54.9% |
| 5 | google/gemini-2.5-flash | proprietary | 52.6% |
| 6 | xiaomi/mimo-v2.5-pro | 1T MoE, 42B active | 37.6% |
| 7 | moonshotai/kimi-k2.6 | 1T MoE, 32B active | 20.0% |
| 8 | z-ai/glm-5 | 744B MoE, 40B active | 13.7% |
| 9 | z-ai/glm-5.1 | proprietary | 12.7% |

---

## Category Breakdown

| Category (weight) | x-ai/grok-4-fast | openai/gpt-4.1-mini | deepseek/deepseek-v4-pro | mistralai/mistral-large-2512 | google/gemini-2.5-flash | xiaomi/mimo-v2.5-pro | moonshotai/kimi-k2.6 | z-ai/glm-5 | z-ai/glm-5.1 |
|---|---|---|---|---|---|---|---|---|---|
| Biblical Reference (15%) | 48.7 | **63.9** | 49.6 | 49.5 | 43.7 | 32.1 | 12.8 | 2.7 | 5.3 |
| Catechism Recall (25%) | 20.6 | 14.6 | 26.0 | 12.6 | 15.8 | **48.3** | 20.7 | 5.4 | 6.0 |
| Comparative Theology (10%) | 92.2 | **93.8** | 89.8 | 93.5 | 85.8 | 70.4 | 50.0 | 48.8 | 59.0 |
| Confessional Knowledge (15%) | 83.7 | 86.5 | 90.5 | **91.0** | 86.6 | 42.2 | 18.4 | 28.1 | 19.1 |
| Doctrinal Position (20%) | **72.0** | 63.0 | 51.1 | 59.1 | 55.3 | 34.2 | 21.6 | 6.7 | 8.3 |
| Error Detection (15%) | **72.5** | 65.5 | 66.8 | 63.2 | 63.0 | 3.3 | 5.7 | 10.0 | 0.0 |

---

## Detailed Analysis

### 1. x-ai/grok-4-fast (proprietary) — 59.5%

**Top performer overall.** Grok-4-fast demonstrates strong performance in several key reasoning categories, leading in Doctrinal Position (72.0%) and Error Detection (72.5%). It also scores very well in Comparative Theology (92.2%) and Confessional Knowledge (83.7%). Its failure rate is moderate with 92 severe failures and 85 zeros out of 270 questions.

- **Strengths**: Doctrinal Position (20% weight), Error Detection (15% weight), and Comparative Theology (10% weight) — indicating robust theological reasoning.
- **Weakness**: Catechism Recall (25% weight) at 20.6% is a significant weakness, suggesting it struggles with verbatim recall of confessional standards. Biblical Reference (15% weight) is also relatively low at 48.7%.
- **Architecture note**: As a proprietary model, specific architectural details are not available.

### 2. openai/gpt-4.1-mini (proprietary) — 58.0%

**Strong all-rounder with best Biblical Reference.** GPT-4.1-mini is a close second, excelling in Biblical Reference (63.9%) and leading all models in Comparative Theology (93.8%). Its performance in Confessional Knowledge (86.5%) and Error Detection (65.5%) is also very strong. It has a slightly higher failure rate than Grok-4-fast, with 99 severe failures and 93 zeros.

- **Strengths**: Biblical Reference (15% weight), Comparative Theology (10% weight), and Confessional Knowledge (15% weight).
- **Weakness**: Catechism Recall (25% weight) is its lowest category at 14.6%, indicating a general struggle with verbatim recall, similar to other general-purpose models.
- **Architecture note**: Proprietary, but noted as approximately 7B parameters.

### 3. deepseek/deepseek-v4-pro (1.6T MoE, 49B active) — 56.7%

**Excellent confessional knowledge.** DeepSeek-v4-pro stands out for its Confessional Knowledge (90.5%) and strong Comparative Theology (89.8%). It has the lowest number of severe failures (89) and zeros (80) among the top 5 models, suggesting good consistency.

- **Strengths**: Confessional Knowledge (15% weight) and Comparative Theology (10% weight). Error Detection (66.8%) is also solid.
- **Weakness**: Doctrinal Position (20% weight) at 51.1% and Catechism Recall (25% weight) at 26.0% are areas for improvement.
- **Architecture note**: A large Mixture-of-Experts (MoE) model with 1.6 trillion parameters, but only 49 billion active per token, balancing capability with inference efficiency.

### 4. mistralai/mistral-large-2512 (675B MoE, 41B active) — 54.9%

**Highest Confessional Knowledge.** Mistral-Large-2512 achieves the highest score in Confessional Knowledge (91.0%) and performs exceptionally well in Comparative Theology (93.5%). Its overall performance is solid, though it has a slightly higher number of severe failures (96) and zeros (88) than DeepSeek-v4-pro.

- **Strengths**: Confessional Knowledge (15% weight) and Comparative Theology (10% weight).
- **Weakness**: Catechism Recall (25% weight) is notably low at 12.6%, indicating a significant challenge in this area. Biblical Reference (15% weight) is also a weaker point at 49.5%.
- **Architecture note**: Another MoE model with 675 billion parameters and 41 billion active, designed for high performance.

### 5. google/gemini-2.5-flash (proprietary) — 52.6%

**Consistent mid-tier performer.** Gemini-2.5-flash shows consistent performance across categories, with strong scores in Confessional Knowledge (86.6%) and Comparative Theology (85.8%). Its failure rate is comparable to other top models, with 98 severe failures and 90 zeros.

- **Strengths**: Confessional Knowledge (15% weight) and Comparative Theology (10% weight).
- **Weakness**: Biblical Reference (15% weight) at 43.7% and Catechism Recall (25% weight) at 15.8% are its primary areas for improvement.
- **Architecture note**: Proprietary model from Google.

### 6. xiaomi/mimo-v2.5-pro (1T MoE, 42B active) — 37.6%

**Uniquely strong in Catechism Recall.** MiMo-v2.5-pro is an interesting case, leading all models in Catechism Recall (48.3%), a category where most other models struggle significantly. However, its overall score is dragged down by very poor performance in Error Detection (3.3%) and lower scores in other key categories. It has 101 severe failures and 76 zeros.

- **Strengths**: Catechism Recall (25% weight) is its standout feature. Comparative Theology (70.4%) is also decent.
- **Weakness**: Error Detection (15% weight) is a critical failure point at 3.3%. Confessional Knowledge (42.2%) and Doctrinal Position (34.2%) are also weak.
- **Architecture note**: A 1T MoE model with 42B active parameters.

### 7. moonshotai/kimi-k2.6 (1T MoE, 32B active) — 20.0%

**Struggles significantly with theological reasoning.** Kimi-k2.6 shows a marked drop in performance compared to the top 6, with 200 severe failures and 184 zeros. While it achieves 50.0% in Comparative Theology, its scores in other categories are very low.

- **Strengths**: Comparative Theology (10% weight) is its only category above 50%.
- **Weakness**: Error Detection (5.7%), Biblical Reference (12.8%), and Confessional Knowledge (18.4%) are all very poor, indicating a general lack of theological understanding.
- **Architecture note**: A 1T MoE model with 32B active parameters.

### 8. z-ai/glm-5 (744B MoE, 40B active) — 13.7%

**Near total failure.** GLM-5 performs very poorly, with 232 severe failures and 232 zeros, indicating it failed almost every question. Its highest score is 48.8% in Comparative Theology, but all other categories are in single or low double digits.

- **Strengths**: Comparative Theology (48.8%) is its only notable score.
- **Weakness**: Catechism Recall (5.4%), Biblical Reference (2.7%), Doctrinal Position (6.7%), and Error Detection (10.0%) are all extremely low.
- **Architecture note**: A 744B MoE model with 40B active parameters.

### 9. z-ai/glm-5.1 (proprietary) — 12.7%

**Worst performer.** GLM-5.1 is the lowest-scoring model, with 234 severe failures and 229 zeros. It scores 0.0% in Error Detection, indicating a complete inability to identify theological errors.

- **Strengths**: Comparative Theology (59.0%) is surprisingly its highest score, but this is an outlier given its overall performance.
- **Weakness**: Error Detection (0.0%), Biblical Reference (5.3%), Catechism Recall (6.0%), and Doctrinal Position (8.3%) are all extremely poor.
- **Architecture note**: Proprietary model.

---

## Recommendation

For general Reformed theological evaluation among mid-tier cloud models, **x-ai/grok-4-fast** is the top choice, closely followed by **openai/gpt-4.1-mini** and **deepseek/deepseek-v4-pro**. These models demonstrate strong reasoning capabilities in the more nuanced categories like Doctrinal Position, Error Detection, and Comparative Theology.

If verbatim Catechism Recall (25% weight) is a primary requirement, **xiaomi/mimo-v2.5-pro** is surprisingly the best performer in that specific category, though its overall score is significantly lower due to critical weaknesses in other areas, especially Error Detection.

Models from Moonshot AI and Zhipu AI (Kimi-k2.6, GLM-5, GLM-5.1) are generally not suitable for theological tasks based on this benchmark, exhibiting high failure rates and very low scores across most categories.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 15, 2026.*