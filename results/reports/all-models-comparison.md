This report presents a comprehensive benchmark comparison of 37 large language models using theolog-bench, an evaluation suite designed to assess understanding and application of Reformed theology. The models were evaluated across several key categories, including Biblical Reference, Catechism Recall, Comparative Theology, Confessional Knowledge, Doctrinal Position, and Error Detection. This benchmark aims to provide insights into the capabilities of current LLMs in a specialized theological domain.

### Overall Rankings

| # | Model | Architecture | Overall Score |
|---|---|---|---|
| 1 | **openai/gpt-5.5** | proprietary | **90.5%** |
| 2 | anthropic/claude-opus-4.7 | proprietary | 85.2% |
| 3 | x-ai/grok-4.3 | proprietary, reasoning | 84.9% |
| 4 | google/gemini-3.1-pro-preview | proprietary | 84.1% |
| 5 | mistralai/mistral-medium-3-5 | 128B dense | 82.9% |
| 6 | z-ai/glm-4.7 | 358B MoE, 32B active | 82.5% |
| 7 | qwen/qwen3.5-122b-a10b | 122B MoE, 10B active | 82.1% |
| 8 | qwen/qwen3.5-27b | 27B dense | 82.0% |
| 9 | qwen/qwen3.6-35b-a3b | 35B MoE, 3B active | 81.7% |
| 10 | mistralai/mistral-large-2512 | 675B MoE, 41B active | 81.4% |
| 11 | qwen/qwen3.6-27b | 27B dense | 80.9% |
| 12 | z-ai/glm-5 | 744B MoE, 40B active | 80.8% |
| 13 | anthropic/claude-sonnet-4.6 | proprietary | 80.1% |
| 14 | deepseek/deepseek-v4-flash | MoE, 13B active | 79.9% |
| 15 | deepseek/deepseek-v4-pro | 1.6T MoE, 49B active | 79.8% |
| 16 | z-ai/glm-5.1 | proprietary | 79.8% |
| 17 | moonshotai/kimi-k2.6 | 1T MoE, 32B active | 78.5% |
| 18 | google/gemini-2.5-flash | proprietary | 77.5% |
| 19 | xiaomi/mimo-v2.5-pro | 1T MoE, 42B active | 77.2% |
| 20 | google/gemma-4-31b-it | 31B dense | 76.8% |
| 21 | mistralai/mistral-small-3.2-24b-instruct | 24B dense | 76.1% |
| 22 | google/gemma-4-26b-a4b-it | 26B MoE, 4B active | 75.8% |
| 23 | z-ai/glm-4-32b | 32B dense | 75.4% |
| 24 | x-ai/grok-4-fast | proprietary | 75.1% |
| 25 | openai/gpt-4.1-mini | proprietary | 74.8% |
| 26 | meta-llama/llama-4-maverick | 400B MoE, 17B active | 73.5% |
| 27 | meta-llama/llama-3.3-70b-instruct | 70B dense | 73.3% |
| 28 | minimax/minimax-m2.7 | 230B MoE, 10B active | 72.3% |
| 29 | qwen/qwen3.5-9b | 9B dense | 68.8% |
| 30 | meta-llama/llama-4-scout | 17B MoE | 68.1% |
| 31 | deepseek/deepseek-r1-distill-llama-70b | 70B dense (R1 distill) | 67.1% |
| 32 | google/gemma-3-27b-it | 27B dense | 65.9% |
| 33 | microsoft/phi-4 | 14B dense | 58.1% |
| 34 | reformed-qwen3-1.7b | 1.7B dense | 35.3% |
| 35 | qwen/qwen3-32b | unknown | 25.3% |
| 36 | qwen/qwen3-30b-a3b | unknown | 23.1% |
| 37 | qwen/qwen3-14b | unknown | 16.7% |

### Category Breakdown

| Model | Biblical Reference (15%) | Catechism Recall (25%) | Comparative Theology (10%) | Confessional Knowledge (15%) | Doctrinal Position (20%) | Error Detection (15%) |
|---|---|---|---|---|---|---|
| openai/gpt-5.5 | 76.9% | **82.5%** | 97.5% | **99.2%** | **94.1%** | 99.4% |
| anthropic/claude-opus-4.7 | 74.4% | 75.2% | 96.5% | 98.9% | 79.0% | 99.5% |
| x-ai/grok-4.3 | 74.9% | 64.6% | 96.8% | 98.8% | 90.3% | 99.9% |
| google/gemini-3.1-pro-preview | 69.0% | 66.7% | 95.3% | 98.8% | 89.1% | 99.7% |
| mistralai/mistral-medium-3-5 | 74.7% | 60.1% | 96.3% | 93.3% | 90.6% | 99.8% |
| z-ai/glm-4.7 | 67.9% | 69.3% | 96.0% | 86.0% | 87.9% | 99.4% |
| qwen/qwen3.5-122b-a10b | 76.7% | 62.3% | 97.5% | 86.8% | 86.1% | 99.9% |
| qwen/qwen3.5-27b | 75.0% | 62.4% | 97.5% | 85.5% | 87.9% | 99.7% |
| qwen/qwen3.6-35b-a3b | 74.6% | 60.9% | 97.7% | 85.2% | 88.7% | 99.8% |
| mistralai/mistral-large-2512 | 70.4% | 60.5% | 96.3% | 93.9% | 85.5% | 99.6% |
| qwen/qwen3.6-27b | 76.8% | 57.7% | **97.8%** | 82.9% | 88.8% | 99.9% |
| z-ai/glm-5 | 60.8% | 66.6% | 92.0% | 94.0% | 84.9% | 98.5% |
| anthropic/claude-sonnet-4.6 | 75.1% | 65.6% | 96.2% | 96.3% | 67.8% | 99.0% |
| deepseek/deepseek-v4-flash | 67.2% | 58.0% | 97.1% | 95.9% | 81.5% | 99.6% |
| deepseek/deepseek-v4-pro | 67.0% | 55.9% | 96.8% | 97.5% | 82.4% | **100.0%** |
| z-ai/glm-5.1 | 59.4% | 61.4% | 95.3% | 91.9% | 86.8% | 99.1% |
| moonshotai/kimi-k2.6 | 71.4% | 68.3% | 91.5% | 65.6% | 91.7% | 89.5% |
| google/gemini-2.5-flash | 70.7% | 50.4% | 92.0% | 88.9% | 84.2% | 99.6% |
| xiaomi/mimo-v2.5-pro | 72.5% | 55.8% | 96.7% | 95.4% | 68.4% | 98.2% |
| google/gemma-4-31b-it | 74.0% | 46.3% | 96.0% | 87.5% | 82.4% | 99.7% |
| mistralai/mistral-small-3.2-24b-instruct | 76.2% | 45.8% | 93.2% | 84.6% | 81.5% | 99.6% |
| google/gemma-4-26b-a4b-it | 66.6% | 44.0% | 96.3% | 84.2% | 88.1% | 99.5% |
| z-ai/glm-4-32b | 69.5% | 53.9% | 94.0% | 78.2% | 77.7% | 99.0% |
| x-ai/grok-4-fast | 48.7% | 55.8% | 91.8% | 84.7% | 86.4% | 97.7% |
| openai/gpt-4.1-mini | 59.7% | 49.6% | 95.2% | 86.6% | 80.1% | 99.5% |
| meta-llama/llama-4-maverick | 64.8% | 50.9% | 90.8% | 84.7% | 72.8% | 98.0% |
| meta-llama/llama-3.3-70b-instruct | 71.3% | 45.2% | 89.7% | 83.3% | 74.9% | 98.8% |
| minimax/minimax-m2.7 | 70.5% | 44.0% | 95.7% | 81.4% | 71.1% | 98.5% |
| qwen/qwen3.5-9b | 69.3% | 41.5% | 89.6% | 46.9% | 88.0% | 96.4% |
| meta-llama/llama-4-scout | 64.3% | 41.8% | 87.8% | 68.6% | 72.6% | 96.3% |
| deepseek/deepseek-r1-distill-llama-70b | 67.8% | 36.3% | 89.0% | 83.1% | 61.2% | 95.2% |
| google/gemma-3-27b-it | 70.2% | 28.8% | 94.0% | 81.3% | 60.8% | 95.9% |
| microsoft/phi-4 | 54.6% | 25.8% | 88.2% | 74.5% | 52.1% | 86.8% |
| reformed-qwen3-1.7b | 14.3% | 50.5% | 13.8% | 37.8% | 62.5% | 6.8% |
| qwen/qwen3-32b | 16.3% | 16.1% | 72.9% | 29.5% | 8.3% | 36.1% |
| qwen/qwen3-30b-a3b | 17.4% | 14.7% | 62.0% | 30.4% | 20.4% | 13.0% |
| qwen/qwen3-14b | 13.7% | 12.7% | 48.5% | 19.1% | 14.2% | 6.4% |

### Detailed Analysis

#### Model: openai/gpt-5.5
*   **Vendor:** OpenAI
*   **Architecture:** proprietary
*   **Parameters:** unknown
*   **Local capable:** False
*   **Overall:** 90.5%
*   **Severe failures:** 13/270
*   **Zeros:** 7
*   **Strengths:** This model demonstrates exceptional performance across the board, securing the top overall ranking. It excels particularly in Confessional Knowledge (99.2%), Doctrinal Position (94.1%), and Catechism Recall (82.5%), which are heavily weighted categories. Its Error Detection score is also very high at 99.4%.
*   **Weaknesses:** While still strong, its lowest scores were in Biblical Reference (76.9%).
*   **Failure Patterns:** With only 13 severe failures and 7 zeros out of 270 questions, `gpt-5.5` exhibits remarkable consistency and accuracy.
*   **Architecture Notes:** As a proprietary model, specific architectural details are not disclosed, but its performance indicates a highly capable and well-trained system.

#### Model: anthropic/claude-opus-4.7
*   **Vendor:** Anthropic
*   **Architecture:** proprietary
*   **Parameters:** ~2-5T
*   **Local capable:** False
*   **Overall:** 85.2%
*   **Severe failures:** 22/270
*   **Zeros:** 12
*   **Strengths:** `claude-opus-4.7` shows strong performance in Error Detection (99.5%), Confessional Knowledge (98.9%), and Comparative Theology (96.5%).
*   **Weaknesses:** Its performance in Catechism Recall (75.2%) and Biblical Reference (74.4%) is relatively lower compared to its other strong categories. Doctrinal Position (79.0%) is also a comparative weakness.
*   **Failure Patterns:** The model had 22 severe failures and 12 zeros, indicating occasional significant misinterpretations or inability to answer.
*   **Architecture Notes:** A proprietary model from Anthropic, estimated to be very large (~2-5T parameters).

#### Model: x-ai/grok-4.3
*   **Vendor:** xAI
*   **Architecture:** proprietary, reasoning
*   **Parameters:** ~3T MoE
*   **Local capable:** False
*   **Overall:** 84.9%
*   **Severe failures:** 28/270
*   **Zeros:** 26
*   **Strengths:** `grok-4.3` performs exceptionally well in Error Detection (99.9%), Confessional Knowledge (98.8%), and Comparative Theology (96.8%). It also scores well in Doctrinal Position (90.3