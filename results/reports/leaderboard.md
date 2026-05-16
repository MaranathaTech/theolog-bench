# theolog-bench Leaderboard

Full ranking of 33 LLMs on Reformed theology benchmark — 270 questions across 6 categories.

Scoring: automated pattern matching + LLM-as-judge (Gemini 2.5 Flash).

---

| # | Model | Tier | BibRef | Catech | Compar | Confes | Doctrn | ErrDet | **Overall** |
|--:|-------|------|-------:|-------:|-------:|-------:|-------:|-------:|------------:|
| 1 | **openai/gpt-5.5** | frontier | 76.9 | 67.5 | 97.8 | 99.2 | 66.5 | 87.5 | **79.5** |
| 2 | **anthropic/claude-opus-4.7** | frontier | 74.4 | 75.4 | 96.8 | 98.8 | 60.1 | 86.2 | **79.5** |
| 3 | x-ai/grok-4.3 | frontier | 74.9 | 56.2 | 96.8 | 98.8 | 75.3 | 95.2 | **79.1** |
| 4 | mistralai/mistral-medium-3-5 | 96gb | 74.7 | 55.2 | 96.7 | 93.4 | 75.1 | 96.2 | **78.1** |
| 5 | qwen/qwen3.5-122b-a10b | 96gb | 76.7 | 67.2 | 97.5 | 86.9 | 55.9 | 100.0 | **77.3** |
| 6 | google/gemini-3.1-pro-preview | frontier | 69.0 | 70.6 | 95.3 | 98.9 | 53.4 | 94.0 | **77.1** |
| 7 | qwen/qwen3.6-35b-a3b | 24gb | 74.6 | 58.5 | 97.8 | 83.2 | 70.9 | 97.3 | **76.9** |
| 8 | z-ai/glm-4.7 | budget | 67.9 | 67.1 | 95.8 | 86.0 | 66.3 | 93.5 | **76.7** |
| 9 | qwen/qwen3.6-27b | 24gb | 76.8 | 57.1 | 97.7 | 83.7 | 67.7 | 98.3 | **76.4** |
| 10 | qwen/qwen3.5-27b | 24gb | 75.0 | 64.8 | 92.7 | 84.5 | 57.7 | 100.0 | **75.9** |
| 11 | mistralai/mistral-large-2512 | mid | 70.4 | 57.3 | 96.6 | 93.4 | 66.5 | 92.8 | **75.8** |
| 12 | z-ai/glm-5 | mid | 60.8 | 65.8 | 92.2 | 93.9 | 57.8 | 94.2 | **74.6** |
| 13 | deepseek/deepseek-v4-pro | mid | 67.0 | 51.8 | 96.8 | 97.5 | 58.5 | 93.5 | **73.0** |
| 14 | deepseek/deepseek-v4-flash | budget | 67.2 | 52.3 | 97.1 | 96.0 | 52.5 | 100.0 | **72.8** |
| 15 | z-ai/glm-5.1 | mid | 59.4 | 61.9 | 95.5 | 92.0 | 55.1 | 91.2 | **72.4** |
| 16 | google/gemini-2.5-flash | mid | 70.7 | 53.5 | 91.7 | 88.9 | 60.2 | 91.8 | **72.3** |
| 17 | anthropic/claude-sonnet-4.6 | frontier | 75.1 | 59.3 | 96.0 | 96.3 | 45.5 | 83.3 | **71.7** |
| 18 | z-ai/glm-4-32b | 24gb | 69.5 | 48.4 | 94.4 | 78.7 | 72.1 | 89.0 | **71.5** |
| 19 | mistralai/mistral-small-3.2-24b | 24gb | 76.2 | 46.6 | 93.3 | 85.2 | 65.4 | 88.3 | **71.5** |
| 20 | google/gemma-4-31b-it | 24gb | 74.0 | 47.0 | 95.9 | 87.7 | 54.3 | 94.7 | **70.7** |
| 21 | xiaomi/mimo-v2.5-pro | mid | 72.5 | 57.1 | 97.0 | 94.5 | 46.8 | 78.8 | **70.2** |
| 22 | google/gemma-3-27b-it | 24gb | 70.2 | 51.1 | 93.8 | 82.0 | 52.8 | 97.8 | **70.2** |
| 23 | moonshotai/kimi-k2.6 | mid | 71.4 | 63.9 | 91.7 | 65.5 | 56.7 | 81.5 | **69.3** |
| 24 | google/gemma-4-26b-a4b-it | 12gb | 66.6 | 45.6 | 96.2 | 84.0 | 52.9 | 89.0 | **67.5** |
| 25 | minimax/minimax-m2.7 | budget | 70.5 | 42.9 | 96.0 | 81.3 | 53.6 | 90.7 | **67.4** |
| 26 | openai/gpt-4.1-mini | mid | 59.7 | 44.1 | 95.3 | 87.2 | 58.3 | 87.5 | **67.4** |
| 27 | meta-llama/llama-4-maverick | budget | 64.8 | 51.7 | 90.8 | 84.2 | 56.2 | 76.2 | **67.0** |
| 28 | meta-llama/llama-3.3-70b | 48gb | 71.3 | 46.6 | 90.4 | 83.5 | 60.8 | 69.5 | **66.5** |
| 29 | qwen/qwen3.5-9b | 12gb | 69.3 | 46.0 | 89.9 | 46.3 | 54.4 | 95.7 | **63.1** |
| 30 | meta-llama/llama-4-scout | budget | 64.3 | 43.8 | 88.0 | 68.0 | 63.2 | 69.0 | **62.6** |
| 31 | deepseek/deepseek-r1-distill-70b | 48gb | 67.8 | 33.6 | 88.8 | 83.0 | 39.9 | 79.0 | **59.7** |
| 32 | microsoft/phi-4 | 12gb | 54.6 | 37.3 | 89.0 | 75.0 | 36.5 | 70.7 | **55.6** |

---

### Category Weights

| Category | Weight | Description |
|----------|-------:|-------------|
| Catechism Recall | 25% | Verbatim recall of catechism Q&A |
| Doctrinal Position | 20% | TULIP, Solas, Reformed distinctives |
| Biblical Reference | 15% | Scripture citation accuracy |
| Confessional Knowledge | 15% | Knowledge of confessional teaching |
| Error Detection | 15% | Identifying heterodox statements |
| Comparative Theology | 10% | Reformed vs other traditions |

### Tier Key

| Tier | Description |
|------|-------------|
| 12gb | RTX 3060/4060 — up to ~14B dense at Q4 |
| 24gb | RTX 3090/4090/5090 — 24B-35B at Q4 |
| 48gb | A6000 / dual-GPU — 70B dense at Q4 |
| 96gb | RTX PRO 6000 / A100 — 70B-128B at Q4 |
| budget | Cloud API, <$0.15/run |
| mid | Cloud API, $0.08-$0.55/run |
| frontier | Cloud API, >$1.50/run |

### Scoring Notes

**Position detection bias:** Doctrinal Position (20%) and Error Detection (15%) use regex
pattern matching to detect affirm/deny positions. This method favors models that give
direct, declarative answers ("No, this is false. Reformed theology rejects...") over
models that present balanced multi-perspective responses ("The Arminian view holds X,
while Reformed theology teaches Y..."). Models known for hedged or comparative response
styles (e.g., Claude, GPT) may score lower in these categories than their actual
theological understanding warrants.

**Catechism Recall (25%)** rewards verbatim or near-verbatim recall of catechism
phrasing. Models trained on Reformed source texts have a natural advantage here. A model
that correctly explains doctrine in its own words but doesn't use traditional catechism
language is capped at ~60% in this category.

---

*Generated by theolog-bench. Scores use weighted category averages.*
*Scorer: v2. Judge model: Gemini 2.5 Flash via OpenRouter.*
*Run date: May 16, 2026.*
