# theolog-bench: 24GB VRAM Tier

Comparative evaluation of open-weight LLMs that can run locally on a single
NVIDIA RTX 4090 (24GB VRAM) at Q4 quantization.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **Qwen 3.6 35B-A3B** | 35B MoE (3B active) | **76.8%** |
| 2 | Qwen 3.6 27B | 27B dense | 76.4% |
| 3 | Qwen 3.5 27B | 27B dense | 75.9% |
| 4 | Mistral Small 3.2 24B | 24B dense | 71.5% |
| 5 | GLM-4 32B | 32B dense | 71.5% |
| 6 | Gemma 4 31B-IT | 31B dense | 70.7% |
| 7 | Gemma 3 27B-IT | 27B dense | 70.2% |

---

## Category Breakdown

| Category (weight) | Qwen 3.6 35B-A3B | Qwen 3.6 27B | Qwen 3.5 27B | Mistral Small 3.2 24B | GLM-4 32B | Gemma 4 31B-IT | Gemma 3 27B-IT |
|---|---|---|---|---|---|---|---|
| Biblical Reference (15%) | 74.6 | **76.8** | 75.0 | 76.2 | 69.5 | 74.0 | 70.2 |
| Catechism Recall (25%) | 58.5 | 57.1 | **64.8** | 46.6 | 48.4 | 47.0 | 51.1 |
| Comparative Theology (10%) | **97.8** | 97.7 | 92.7 | 93.3 | 94.4 | 95.9 | 93.8 |
| Confessional Knowledge (15%) | 83.2 | 83.7 | 84.5 | 85.2 | 78.7 | **87.7** | 82.0 |
| Doctrinal Position (20%) | 70.9 | 67.7 | 57.7 | 65.4 | **72.1** | 54.3 | 52.8 |
| Error Detection (15%) | 97.3 | 98.3 | **100.0** | 88.3 | 89.0 | 94.7 | 97.8 |

---

## Detailed Analysis

### 1. Qwen 3.6 35B-A3B (35B MoE, 3B active) — 76.8%

**Top performer in the 24GB tier.** This MoE model demonstrates excellent
performance, particularly in categories requiring nuanced understanding and
detection of theological positions. It leads in Comparative Theology (97.8%) and
shows strong Error Detection (97.3%). Its low number of severe failures (10/270)
and zeros (4) indicate high reliability.

- **Strengths**: Comparative Theology (97.8%), Error Detection (97.3%), and
  Confessional Knowledge (83.2%). Its ability to discern subtle theological
  differences is a significant advantage.
- **Weakness**: Catechism Recall (58.5%) and Doctrinal Position (70.9%) are its
  lowest scores, though still respectable. Like many general-purpose models, it
  struggles with verbatim recall of confessional standards.
- **Architecture note**: As an MoE model with only 3B active parameters, it
  offers efficient inference while leveraging a larger parameter count for
  knowledge. This allows it to fit within 24GB VRAM while delivering top-tier
  performance.

### 2. Qwen 3.6 27B (27B dense) — 76.4%

**Strong dense model, excelling in Biblical Reference.** A close second to its
MoE sibling, this dense model shows remarkable strength in Biblical Reference
(76.8%), outperforming all other models in this category. It also boasts
excellent Error Detection (98.3%) and Comparative Theology (97.7%) scores.

- **Strengths**: Biblical Reference (76.8%), Error Detection (98.3%), and
  Comparative Theology (97.7%). Its strong performance in Biblical Reference
  suggests robust training on scriptural texts.
- **Weakness**: Catechism Recall (57.1%) and Doctrinal Position (67.7%) are its
  comparative weak points, similar to other Qwen models.
- **Architecture note**: A 27B dense model, it provides consistent performance
  across the board. Its memory footprint is well within the 24GB limit, making
  it a reliable choice for local deployment.

### 3. Qwen 3.5 27B (27B dense) — 75.9%

**Best in Catechism Recall and perfect Error Detection.** This model stands out
with a perfect score in Error Detection (100.0%) and the highest Catechism
Recall (64.8%) among all models tested in this tier. This indicates a strong
ability to identify theological inaccuracies and a better grasp of confessional
phrasing.

- **Strengths**: Error Detection (100.0%), Catechism Recall (64.8%), and
  Confessional Knowledge (84.5%). Its verbatim recall ability is notable for a
  general-purpose model.
- **Weakness**: Doctrinal Position (57.7%) is its lowest category, suggesting
  it might be less adept at articulating complex doctrinal nuances compared to
  its Qwen counterparts.
- **Architecture note**: Another 27B dense model from Qwen, it demonstrates
  that specific training or architectural choices can significantly impact
  performance in key categories like recall and error identification.

### 4. Mistral Small 3.2 24B (24B dense) — 71.5%

**Solid all-rounder with strong confessional knowledge.** This Mistral model
ties for fourth place, showing consistent performance across categories. It
excels in Confessional Knowledge (85.2%) and Comparative Theology (93.3%),
demonstrating a good understanding of Reformed doctrines.

- **Strengths**: Confessional Knowledge (85.2%), Comparative Theology (93.3%),
  and Biblical Reference (76.2%). It provides a balanced theological understanding.
- **Weakness**: Catechism Recall (46.6%) is its lowest score, indicating a
  tendency to paraphrase rather than quote directly. Doctrinal Position (65.4%)
  is also a relative weakness.
- **Architecture note**: A 24B dense model, it fits perfectly within the 24GB
  VRAM constraint, offering a strong performance-to-memory ratio.

### 5. GLM-4 32B (32B dense) — 71.5%

**Leads in Doctrinal Position.** Tying with Mistral Small, GLM-4 32B achieves
the highest score in Doctrinal Position (72.1%), indicating a strong ability
to articulate and defend specific theological stances. It also performs well
in Comparative Theology (94.4%).

- **Strengths**: Doctrinal Position (72.1%), Comparative Theology (94.4%), and
  Error Detection (89.0%). Its ability to handle doctrinal questions is a key
  differentiator.
- **Weakness**: Biblical Reference (69.5%) and Catechism Recall (48.4%) are its
  lowest-scoring categories. It may not be as adept at direct scriptural citation
  or verbatim confessional recall.
- **Architecture note**: A 32B dense model, it pushes the limits of the 24GB
  VRAM tier but manages to fit, offering a powerful option for doctrinal analysis.

### 6. Gemma 4 31B-IT (31B dense) — 70.7%

**Best in Confessional Knowledge.** This Gemma model demonstrates the highest
score in Confessional Knowledge (87.7%), indicating a deep understanding of
Reformed theological tenets. It also performs exceptionally well in Comparative
Theology (95.9%) and Error Detection (94.7%).

- **Strengths**: Confessional Knowledge (87.7%), Comparative Theology (95.9%),
  and Error Detection (94.7%). Its strong grasp of core doctrines is a significant
  advantage.
- **Weakness**: Doctrinal Position (54.3%) and Catechism Recall (47.0%) are its
  lowest categories, suggesting it might struggle with articulating complex
  positions or verbatim recall.
- **Architecture note**: A 31B dense model, it is another large model for this
  tier, showcasing Google's capabilities in fitting powerful models into
  constrained environments.

### 7. Gemma 3 27B-IT (27B dense) — 70.2%

**Consistent performer with high error detection.** The Gemma 3 model provides
a reliable baseline, with very low severe failures (6/270) and zeros (4). It
shows strong Error Detection (97.8%) and Comparative Theology (93.8%).

- **Strengths**: Error Detection (97.8%), Comparative Theology (93.8%), and
  Confessional Knowledge (82.0%). Its consistency and ability to identify errors
  are notable.
- **Weakness**: Doctrinal Position (52.8%) and Catechism Recall (51.1%) are its
  weakest areas, similar to its Gemma 4 counterpart.
- **Architecture note**: A 27B dense model, it represents a solid, stable option
  for local theological reasoning within the 24GB VRAM limit.

---

## Scoring Notes

(a) Doctrinal Position and Error Detection (35% combined) use regex pattern
matching that favors direct affirm/deny answers over balanced multi-perspective
responses — models that hedge or present comparative views may score lower than
their understanding warrants.
(b) Catechism Recall (25%) rewards near-verbatim recall of catechism phrasing,
giving a natural advantage to models trained on Reformed source texts.

---

## Recommendation

The **Qwen 3.6 35B-A3B** is the top recommendation for local theological
reasoning on a 24GB card. Its leading overall score of 76.8%, combined with
its strong performance in high-weight categories like Comparative Theology and
Error Detection, makes it an excellent choice. Its MoE architecture also
suggests efficient inference for its knowledge base.

For those prioritizing verbatim recall of confessional standards, **Qwen 3.5 27B**
is a strong contender, leading in Catechism Recall (64.8%) and achieving a perfect
100.0% in Error Detection.

If a strong grasp of specific doctrinal positions is paramount, **GLM-4 32B**
stands out with the highest score in Doctrinal Position (72.1%).

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 16, 2026.*