# theolog-bench: Frontier Cloud Models

Comparative evaluation of leading proprietary large language models, focusing on
their performance in Reformed theology.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **x-ai/grok-4.3** | proprietary, reasoning | **79.4%** |
| 2 | google/gemini-3.1-pro-preview | proprietary | 76.8% |
| 3 | anthropic/claude-opus-4.7 | proprietary | 66.7% |
| 4 | openai/gpt-5.5 | proprietary | 63.3% |
| 5 | anthropic/claude-sonnet-4.6 | proprietary | 61.6% |

---

## Category Breakdown

| Category (weight) | x-ai/grok-4.3 | google/gemini-3.1-pro-preview | anthropic/claude-opus-4.7 | openai/gpt-5.5 | anthropic/claude-sonnet-4.6 |
|---|---|---|---|---|---|
| Biblical Reference (15%) | 71.6 | 67.1 | 68.2 | 50.3 | **73.0** |
| Catechism Recall (25%) | 60.2 | **69.9** | 53.6 | 45.1 | 35.3 |
| Comparative Theology (10%) | **96.0** | 86.0 | 92.0 | 91.0 | 95.9 |
| Confessional Knowledge (15%) | 93.7 | **98.8** | 96.4 | 77.5 | 94.4 |
| Doctrinal Position (20%) | **77.8** | 61.2 | 48.5 | 68.6 | 42.9 |
| Error Detection (15%) | **95.7** | 91.0 | 64.7 | 67.2 | 63.3 |

---

## Detailed Analysis

### 1. x-ai/grok-4.3 (proprietary, reasoning) — 79.4%

**Top performer overall.** Grok-4.3 demonstrates exceptional performance in
categories requiring advanced theological reasoning and discernment. It leads
in 3 of the 6 categories, including the highly weighted Doctrinal Position
(20%) and Error Detection (15%), as well as Comparative Theology (10%). Its
failure rate is remarkably low, with only 12 severe failures and 7 zeros out
of 270 questions.

- **Strengths**: Comparative Theology (96.0%), Error Detection (95.7%), and
  Confessional Knowledge (93.7%) highlight its ability to navigate complex
  theological nuances and identify deviations.
- **Weaknesses**: Biblical Reference (71.6%) and Catechism Recall (60.2%) are
  its lowest scores, though still strong compared to other models. This suggests
  a slight preference for reasoning over verbatim recall or direct scriptural
  citation.
- **Architecture note**: Described as a "reasoning" model with ~3T MoE
  parameters, its strong performance in complex categories aligns with its
  design for sophisticated problem-solving.

### 2. google/gemini-3.1-pro-preview (proprietary) — 76.8%

**Strong contender with excellent recall.** Gemini 3.1 Pro Preview is a close
second, excelling particularly in recall-based categories. It leads in
Catechism Recall (25% weight) and Confessional Knowledge (15% weight),
demonstrating a robust understanding of established theological standards. Its
failure rate is on par with Grok-4.3, with 10 severe failures and 7 zeros.

- **Strengths**: Confessional Knowledge (98.8%) and Catechism Recall (69.9%)
  are outstanding, indicating strong memorization and accurate reproduction of
  theological content. Error Detection (91.0%) is also very strong.
- **Weaknesses**: Doctrinal Position (61.2%) and Biblical Reference (67.1%) are
  its comparatively weaker areas, suggesting that while it recalls well, its
  ability to articulate nuanced doctrinal stances or cite scripture precisely
  is slightly less developed than its top-tier peers.
- **Architecture note**: As a proprietary model, specific architectural details
  are unknown, but its performance profile suggests a strong emphasis on factual
  accuracy and knowledge retrieval.

### 3. anthropic/claude-opus-4.7 (proprietary) — 66.7%

**Reliable, but with more failures.** Claude Opus 4.7 provides solid performance
across the board, particularly in knowledge-intensive categories. While not
leading any category, its scores in Confessional Knowledge (96.4%) and
Comparative Theology (92.0%) are very high. However, its failure rate is
significantly higher than the top two, with 51 severe failures and 47 zeros.

- **Strengths**: Confessional Knowledge (96.4%) and Comparative Theology (92.0%)
  show its capacity for deep theological understanding. Biblical Reference
  (68.2%) is also respectable.
- **Weaknesses**: Catechism Recall (53.6%) and Doctrinal Position (48.5%) are
  its lowest scores, indicating potential struggles with verbatim recall and
  articulating precise doctrinal nuances compared to the leaders. The higher
  number of zeros suggests occasional complete failures to answer.
- **Architecture note**: Estimated at ~2-5T parameters, its broad knowledge base
  is evident, but the higher failure rate suggests less consistent performance
  than the top models.

### 4. openai/gpt-5.5 (proprietary) — 63.3%

**Consistent but not leading.** GPT-5.5 offers a generally consistent
performance, particularly strong in Comparative Theology (91.0%). However, it
struggles more with recall and biblical citation compared to other frontier
models. It has a notable number of severe failures (66) and zeros (56).

- **Strengths**: Comparative Theology (91.0%) is a highlight, showing its ability
  to analyze and compare different theological viewpoints. Doctrinal Position
  (68.6%) is also decent.
- **Weaknesses**: Biblical Reference (50.3%) and Catechism Recall (45.1%) are
  its weakest points, indicating challenges in accurately citing scripture or
  recalling confessional standards verbatim. Its Confessional Knowledge (77.5%)
  is also significantly lower than its peers.
- **Architecture note**: As a proprietary model, details are unknown, but its
  performance suggests a general-purpose capability that is less specialized
  for theological recall and precision than the top models.

### 5. anthropic/claude-sonnet-4.6 (proprietary) — 61.6%

**Best at Scripture, but with significant recall issues.** Claude Sonnet 4.6
stands out for its leading performance in Biblical Reference (73.0%),
suggesting strong training on scriptural texts. It also performs very well in
Comparative Theology (95.9%) and Confessional Knowledge (94.4%). However, it
has the highest number of severe failures (73) and zeros (65) among all models
tested, particularly in Catechism Recall and Doctrinal Position.

- **Strengths**: Biblical Reference (73.0%) is its strongest suit, making it
  the best model for scriptural citation. Comparative Theology (95.9%) and
  Confessional Knowledge (94.4%) are also very high.
- **Weaknesses**: Catechism Recall (35.3%) and Doctrinal Position (42.9%) are
  its most significant weaknesses, indicating a struggle with verbatim recall
  of confessional standards and articulating precise doctrinal stances. The
  high number of zeros points to frequent complete failures in these areas.
- **Architecture note**: While details are proprietary, its bimodal performance
  (excellent in some areas, very weak in others) suggests a different internal
  knowledge representation or retrieval mechanism compared to Opus.

---

## Recommendation

For comprehensive and nuanced theological reasoning, **x-ai/grok-4.3 is the
clear leader**, demonstrating superior performance across critical reasoning
categories and the lowest failure rate.

If strong recall of confessional standards and high accuracy in knowledge
retrieval are paramount, **google/gemini-3.1-pro-preview** is an excellent
alternative, leading in Catechism Recall and Confessional Knowledge.

While **anthropic/claude-sonnet-4.6** excels in Biblical Reference, its
significant weaknesses in Catechism Recall and Doctrinal Position, coupled
with the highest failure rate, make it less suitable for a broad range of
theological tasks compared to the top two.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 15, 2026.*