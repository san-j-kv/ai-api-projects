# LLM API Basics

Small scripts that call a local LLM (Ollama, `llama3.2`) over its HTTP API. Part of my AI learning plan; no paid API keys needed.

## What's here

| File | What it does |
|---|---|
| `2026-11-17-ollama-chat.py` | Sends one question to Ollama's `/api/chat` endpoint and prints the reply. Handles connection errors and timeouts. |
| `2026-11-17-ollama-system-prompt.py` | Asks the same question with and without a system prompt, to compare the answers. |
| `2026-11-18-json-output.py` | Classifies customer emails into structured JSON (`intent`, `urgency`, `summary`) using `"format": "json"`, a detailed system prompt and `temperature: 0`. |

## What I learned

- A **system prompt** sets the model's role, rules and output format before the user's question.
- **Valid JSON is not the same as correct JSON.** `"format": "json"` guarantees the shape, not the accuracy of the content.
- My first classifier prompt had no definitions, and one email (a request to update an address) was labelled a "query". Adding **one-line definitions** for each intent, plus **a few examples**, fixed it.
- `temperature: 0` makes the output more consistent between runs.
- Parsing model output needs its own error handling (`JSONDecodeError`, missing keys), separate from network errors.

## Limitations

- Tested on only 3 sample emails. A real evaluation would use 20-50 labelled emails and count the misses.
- `llama3.2` is a small local model. Prompt wording matters more than it would with a larger model, and small changes in whitespace can change results.

## How to run

1. Install and start [Ollama](https://ollama.com), then run `ollama pull llama3.2`.
2. `pip install requests`
3. `python 2026-11-18-json-output.py`
