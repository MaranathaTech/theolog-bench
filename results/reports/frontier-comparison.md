# theolog-bench: Frontier Cloud Models

Comparative evaluation of leading proprietary large language models available
via API, focusing on their performance in Reformed theology.

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
| 6 | x-ai/grok-4-fast | proprietary | 59.5% |

---

## Category Breakdown

| Category (weight) | Grok 4.3 | Gemini 3.1 Pro | Claude Opus 4.7 | GPT-5.5 | Claude Sonnet 4.6 | Grok 4 Fast |
|---|---|---|---|---|---|---|
| Biblical Reference (15%) | 71.6 | 67.1 | 68.2 | 50.3 | **73.0** | 48.7 |
| Catechism Recall (25%) | 60.2 | **69.9** | 53.6 | 45.1 | 35.3 | 20.6 |
| Comparative Theology (10%) | **96.0** | 86.0 | 92.0 | 91.0 | 95.9 | 92.2 |
| Confessional Knowledge (15%) | 93.7 | **98.8** | 96.4 | 77.5 | 94.4 | 83.7 |
| Doctrinal Position (20%) | **77.8** | 61.2 | 48.5 | 68.6 | 42.9 | 72.0 |
| Error Detection (15%) | **95.7** | 91.0 | 64.7 | 67.2 | 63.3 | 72.5 |

---

## Detailed Analysis

### 1. x-ai/grok-4.3 (proprietary, reasoning) — 79.4%

**Top performer overall.** Grok 4.3 demonstrates exceptional reasoning capabilities,
leading in 4 of the 6 categories, including the highly weighted Doctrinal Position (20%)
and Error Detection (15%), as well as Comparative Theology (10%). It exhibits the
lowest number of severe failures (12/270) and zeros (7) among all models tested.

- **Strengths**: Comparative Theology (96.0%), Error Detection (95.7%), and
  Confessional Knowledge (93.7%). Its strong performance in these categories
  suggests advanced theological reasoning and discernment.
- **Weaknesses**: Biblical Reference (71.6%) and Catechism Recall (60.2%) are
  its relatively weaker areas, though still strong compared to other models.
  Its Catechism Recall is notably lower than Gemini 3.1 Pro.
- **Architecture note**: Described as a "reasoning" model, its architecture
  likely emphasizes complex logical processing, which aligns with its high
  scores in categories requiring nuanced theological understanding.

### 2. google/gemini-3.1-pro-preview (proprietary) — 76.8%

**Strong runner-up with excellent confessional recall.** Gemini 3.1 Pro shows
outstanding performance in Confessional Knowledge (98.8%) and leads decisively
in Catechism Recall (69.9%), a category where many models struggle. It has a
very low failure rate, with only 10 severe failures and 7 zeros.

- **Strengths**: Confessional Knowledge (98.8%), Catechism Recall (69.9%), and
  Error Detection (91.0%). Its ability to accurately recall and apply
  confessional standards is a significant advantage.
- **Weaknesses**: Doctrinal Position (61.2%) is its lowest score, indicating
  potential areas for improvement in synthesizing complex doctrinal arguments.
  Biblical Reference (67.1%) is also not its strongest suit.
- **Architecture note**: As a general-purpose frontier model, its broad
  training likely contributes to its strong performance across various
  theological sub-domains, particularly in factual recall.

### 3. anthropic/claude-opus-4.7 (proprietary) — 66.7%

**Solid performance, but with higher failure rates.** Claude Opus 4.7 performs
respectably, particularly in Confessional Knowledge (96.4%) and Comparative
Theology (92.0%). However, it shows a higher number of severe failures (51/270)
and zeros (47) compared to the top two models.

- **Strengths**: Confessional Knowledge (96.4%), Comparative Theology (92.0%),
  and Biblical Reference (68.2%). It demonstrates a good grasp of core
  theological concepts and inter-theological comparisons.
- **Weaknesses**: Doctrinal Position (48.5%) and Catechism Recall (53.6%) are
  its weakest areas, suggesting challenges in articulating complex doctrinal
  nuances and verbatim recall.
- **Architecture note**: As a large proprietary model, its performance is
  generally strong, but the higher failure rate in certain categories indicates
  less consistency than the top two.

### 4. openai/gpt-5.5 (proprietary) — 63.3%

**Consistent but not leading.** GPT-5.5 offers a balanced performance across
categories but does not lead in any. It shows a moderate number of severe
failures (66/270) and zeros (56).

- **Strengths**: Comparative Theology (91.0%) and Confessional Knowledge (77.5%).
  It can effectively compare theological positions.
- **Weaknesses**: Biblical Reference (50.3%) and Catechism Recall (45.1%) are
  its lowest scores, indicating potential areas for improvement in direct
  scriptural citation and confessional memorization.
- **Architecture note**: As a flagship model, its broad general knowledge is
  evident, but it may lack the specialized theological fine-tuning seen in
  higher-ranked models for specific tasks.

### 5. anthropic/claude-sonnet-4.6 (proprietary) — 61.6%

**Strong in Biblical Reference, but struggles with recall.** Claude Sonnet 4.6
surprisingly leads in Biblical Reference (73.0%), outperforming all other
models in this category. However, it has a high number of severe failures
(73/270) and zeros (65), particularly struggling with Catechism Recall.

- **Strengths**: Biblical Reference (73.0%), Comparative Theology (95.9%), and
  Confessional Knowledge (94.4%). Its ability to cite scripture accurately is
  a notable highlight.
- **Weaknesses**: Catechism Recall (35.3%) and Doctrinal Position (42.9%) are
  significant weaknesses, suggesting difficulties in precise confessional
  formulation and complex doctrinal articulation.
- **Architecture note**: While part of the Claude family, Sonnet's performance
  profile differs from Opus, indicating potential architectural or training
  differences that favor biblical citation over verbatim recall.

### 6. x-ai/grok-4-fast (proprietary) — 59.5%

**Lowest overall, with high failure rates.** Grok 4 Fast is the lowest-scoring
model in this comparison, with the highest number of severe failures (92/270)
and zeros (85). While it shows some strengths in higher-level reasoning, its
recall capabilities are significantly limited.

- **Strengths**: Comparative Theology (92.2%), Confessional Knowledge (83.7%),
  and Error Detection (72.5%). It can still perform well in tasks requiring
  broader theological understanding.
- **Weaknesses**: Catechism Recall (20.6%) and Biblical Reference (48.7%) are
  its most significant weaknesses, indicating a struggle with precise factual
  recall and scriptural citation.
- **Architecture note**: Likely a smaller or more optimized version of Grok 4.3,
  trading off overall performance and consistency for potentially faster
  inference or lower resource usage.

---

## Recommendation

**x-ai/grok-4.3 is the clear leader** among frontier cloud models for
Reformed theology evaluation. Its superior performance across most categories,
especially in doctrinal position and error detection, combined with the lowest
failure rate, makes it the most reliable choice for nuanced theological tasks.

**google/gemini-3.1-pro-preview is a strong alternative**, particularly if
accurate Catechism Recall and Confessional Knowledge are paramount. Its
exceptionally low failure rate and high scores in these critical areas make it
a highly dependable option.

For tasks heavily reliant on **Biblical Reference, anthropic/claude-sonnet-4.6**
surprisingly excels, but its overall lower score and high failure rate in
other categories should be considered.

**Avoid x-ai/grok-4-fast** for tasks requiring high accuracy or reliable recall,
as its performance is significantly lower than other frontier models.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 14, 2026.*