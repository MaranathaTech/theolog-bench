# theolog-bench: Frontier Cloud Models

Comparative evaluation of leading proprietary large language models on Reformed
theology.

Benchmark: 270 questions across 6 categories of Reformed theological knowledge.
Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash) for
confessional knowledge, error detection, and comparative theology.

---

## Overall Rankings

| # | Model | Architecture | Overall |
|---|---|---|---|
| 1 | **Claude Opus 4.7** | proprietary | **79.5%** |
| 2 | GPT-5.5 | proprietary | 79.5% |
| 3 | Grok 4.3 | proprietary, reasoning | 79.1% |
| 4 | Gemini 3.1 Pro Preview | proprietary | 77.1% |
| 5 | Claude Sonnet 4.6 | proprietary | 71.7% |

---

## Category Breakdown

| Category (weight) | Claude Opus 4.7 | GPT-5.5 | Grok 4.3 | Gemini 3.1 Pro Preview | Claude Sonnet 4.6 |
|---|---|---|---|---|---|
| Biblical Reference (15%) | 74.4 | **76.9** | 74.9 | 69.0 | 75.1 |
| Catechism Recall (25%) | **75.4** | 67.5 | 56.2 | 70.6 | 59.3 |
| Comparative Theology (10%) | 96.8 | **97.8** | 96.8 | 95.3 | 96.0 |
| Confessional Knowledge (15%) | 98.8 | **99.2** | 98.8 | 98.9 | 96.3 |
| Doctrinal Position (20%) | 60.1 | 66.5 | **75.3** | 53.4 | 45.5 |
| Error Detection (15%) | 86.2 | 87.5 | **95.2** | 94.0 | 83.3 |

---

## Detailed Analysis

### 1. Claude Opus 4.7 (proprietary) — 79.5%

**Top performer, tied with GPT-5.5.** Achieves the highest score in Catechism Recall (75.4%), a heavily weighted category (25%), and demonstrates near-perfect Confessional Knowledge (98.8%). It has the fewest severe failures (4/270) and only one zero score, indicating high reliability.

- **Strengths**: Catechism Recall (75.4%), Confessional Knowledge (98.8%), and Comparative Theology (96.8%). Its strong performance in Catechism Recall suggests good exposure to Reformed confessional standards.
- **Weakness**: Doctrinal Position (60.1%) and Biblical Reference (74.4%) are its lowest categories, though still strong overall.
- **Architecture note**: Proprietary model with estimated parameters in the 2-5 trillion range. Not runnable locally.

### 2. GPT-5.5 (proprietary) — 79.5%

**Tied for top overall score.** GPT-5.5 excels in several key areas, leading in Biblical Reference (76.9%), Comparative Theology (97.8%), and Confessional Knowledge (99.2%). While its overall score matches Claude Opus, it has slightly more severe failures (10/270) and zero scores (6).

- **Strengths**: Confessional Knowledge (99.2%), Comparative Theology (97.8%), and Biblical Reference (76.9%). Its ability to accurately cite Scripture is notable.
- **Weakness**: Catechism Recall (67.5%) is lower than Claude Opus, and Doctrinal Position (66.5%) is not its strongest.
- **Architecture note**: Proprietary model with unknown parameters. Not runnable locally.

### 3. Grok 4.3 (proprietary, reasoning) — 79.1%

**Strong reasoning capabilities.** Grok 4.3 stands out by leading in the Doctrinal Position (75.3%) and Error Detection (95.2%) categories, both of which require nuanced theological reasoning and the ability to identify subtle deviations. However, it has the highest number of severe failures (20/270) and zero scores (12) among the top models, suggesting some inconsistency.

- **Strengths**: Doctrinal Position (75.3%) and Error Detection (95.2%) are exceptional, indicating strong analytical and critical thinking skills in theology. Confessional Knowledge (98.8%) and Comparative Theology (96.8%) are also very high.
- **Weakness**: Catechism Recall (56.2%) is significantly lower than its peers, suggesting it may prioritize reasoning over verbatim memorization.
- **Architecture note**: Proprietary reasoning model, estimated at ~3T MoE. Not runnable locally.

### 4. Gemini 3.1 Pro Preview (proprietary) — 77.1%

**Consistent and reliable.** Gemini 3.1 Pro Preview shows strong performance across the board, with high scores in Confessional Knowledge (98.9%), Comparative Theology (95.3%), and Error Detection (94.0%). It has a low number of severe failures (7/270) and zero scores (6), indicating good reliability.

- **Strengths**: Confessional Knowledge (98.9%), Comparative Theology (95.3%), and Error Detection (94.0%).
- **Weakness**: Doctrinal Position (53.4%) and Biblical Reference (69.0%) are its lowest-scoring categories, suggesting areas for improvement in specific theological applications.
- **Architecture note**: Proprietary model with unknown parameters. Not runnable locally.

### 5. Claude Sonnet 4.6 (proprietary) — 71.7%

**Solid mid-tier performer.** While ranking fifth, Claude Sonnet 4.6 still demonstrates strong capabilities in Confessional Knowledge (96.3%) and Comparative Theology (96.0%). It has a moderate number of severe failures (19/270) and zero scores (4).

- **Strengths**: Confessional Knowledge (96.3%) and Comparative Theology (96.0%) are very strong, showing a good grasp of core theological concepts.
- **Weakness**: Doctrinal Position (45.5%) and Catechism Recall (59.3%) are its lowest categories, indicating a potential struggle with precise theological phrasing and nuanced positional arguments.
- **Architecture note**: Proprietary model with unknown parameters. Not runnable locally.

---

## Scoring Notes

- Doctrinal Position and Error Detection (35% combined) use regex pattern matching that favors direct affirm/deny answers over balanced multi-perspective responses — models that hedge or present comparative views may score lower than their understanding warrants.
- Catechism Recall (25%) rewards near-verbatim recall of catechism phrasing, giving a natural advantage to models trained on Reformed source texts.

---

## Recommendation

The top three models — **Claude Opus 4.7, GPT-5.5, and Grok 4.3** — are all excellent choices for frontier-level Reformed theological reasoning, with overall scores within 0.4 percentage points of each other.

- **Claude Opus 4.7** is recommended for tasks requiring high fidelity to confessional standards and catechism recall.
- **GPT-5.5** is ideal for tasks demanding strong biblical grounding and broad confessional knowledge.
- **Grok 4.3** is the best choice for tasks that heavily rely on complex theological reasoning, error detection, and nuanced doctrinal positioning.

Gemini 3.1 Pro Preview offers a very reliable and consistent performance, making it a strong general-purpose option. Claude Sonnet 4.6, while lower in overall score, still provides robust performance in core theological areas.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2 (improved position detection for multi-view responses).*
*Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 16, 2026.*