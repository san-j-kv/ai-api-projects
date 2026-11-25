# Personal Research Assistant

A small command-line script that takes a topic, finds matching Wikipedia articles, and uses a local LLM to turn them into key points.

Built as a learning project, with AI assistance for code review and debugging.

## How it works

1. You enter a topic.
2. The script searches Wikipedia (Action API) and fetches the intro extracts of the top 3 articles.
3. The extracts are sent to a local model (llama3.2 via Ollama) with an instruction to use only that text.
4. The model returns JSON with `key_points`, which the script prints.

## Run it

Requirements: Python 3, `requests`, and [Ollama](https://ollama.com) running locally with `llama3.2` pulled.

```
ollama pull llama3.2
python research.py
```

## What I learned

- Grounding matters. My first version asked the LLM about Wikipedia without fetching anything, so it answered from memory. Fetching real text first fixed that.
- Prompts need explicit instructions. A vague prompt returned `{"key_points": []}`. Saying what to extract (5-8 one-sentence points) fixed it.
- Small local models make mistakes. In one run, an article title got merged into the first key point.
- Local models are slow without a GPU: about 66 seconds per run, with three articles.

## Limitations

- Only the first 3 search results are used, and only the intro of each article.
- Output quality depends on llama3.2 and isn't checked automatically.

## Next

- Plan sub-queries with the LLM, search for each, then write a structured Markdown report (prompt chaining).
