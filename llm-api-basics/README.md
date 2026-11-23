# LLM API Basics

Small scripts that call a local LLM (Ollama, `llama3.2`) over its HTTP API. Part of my AI learning plan; no paid API keys needed.

## What's here

| File | What it does |
|---|---|
| `2026-11-17-ollama-chat.py` | Sends one question to Ollama's `/api/chat` endpoint and prints the reply. Handles connection errors and timeouts. |
| `2026-11-17-ollama-system-prompt.py` | Asks the same question with and without a system prompt, to compare the answers. |
| `2026-11-18-json-output.py` | Classifies customer emails into structured JSON (`intent`, `urgency`, `summary`) using `"format": "json"`, a detailed system prompt and `temperature: 0`. |
| `2026-11-23-tool-calling.py` | Function (tool) calling: the model asks for a `get_weather` function, my code runs it against the free Open-Meteo API and sends the result back for a final answer. |

## What I learned

- A **system prompt** sets the model's role, rules and output format before the user's question.
- **Valid JSON is not the same as correct JSON.** `"format": "json"` guarantees the shape, not the accuracy of the content.
- My first classifier prompt had no definitions, and one email (a request to update an address) was labelled a "query". Adding **one-line definitions** for each intent, plus **a few examples**, fixed it.
- `temperature: 0` makes the output more consistent between runs.
- Parsing model output needs its own error handling (`JSONDecodeError`, missing keys), separate from network errors.
- **Tool calling:** the model never runs anything itself. It only replies with the name of a function and its arguments. My code runs the function, appends the result as a `tool` message, and calls the API again so the model can write the final answer.
- Tools are looked up in a dictionary (`available_functions`), so an unknown function name returns an error message instead of crashing.
- Tool functions should **return error strings** (city not found, network error) rather than raising, so the model can explain the problem to the user.
- A system message is just the first item in `messages`. A `system_prompt` key in the payload is silently ignored.

## Limitations

- Tested on only 3 sample emails. A real evaluation would use 20-50 labelled emails and count the misses.
- `llama3.2` is a small local model. Prompt wording matters more than it would with a larger model, and small changes in whitespace can change results.
- `llama3.2` sometimes writes a fake tool call as plain text (for example `{"name": "console.log", ...}`) for questions that need no tool, even with a firm system prompt. Larger or hosted models handle this better, so tool reliability depends on the model.
- The weather tool uses the first geocoding match for a city name, so ambiguous names (for example "Springfield") may resolve to the wrong place.

## How to run

1. Install and start [Ollama](https://ollama.com), then run `ollama pull llama3.2`.
2. `pip install requests`
3. `python 2026-11-23-tool-calling.py` (or any other script above)
