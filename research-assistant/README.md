# Personal Research Assistant

A small command-line script that takes a topic, finds matching Wikipedia articles, and uses a local LLM to turn them into key points.

Built as a learning project, with AI assistance for code review and debugging.

## How it works (prompt chaining)

1. You enter a topic.
2. **Plan:** the LLM (llama3.2 via Ollama) turns the topic into 3 short Wikipedia search queries covering different angles. If this step fails, the script falls back to searching the plain topic.
3. **Search:** the script searches Wikipedia once per query (Action API) and fetches the intro extracts of the top 3 articles for each. Duplicate articles are dropped. A failed search is skipped, not fatal.
4. **Summarize:** the combined extracts are sent to the LLM with an instruction to use only that text. It returns JSON with `key_points`, which the script prints.

## Run it

Requirements: Python 3, `requests`, and [Ollama](https://ollama.com) running locally with `llama3.2` pulled.

```
ollama pull llama3.2
python research-assistant.py
```

## What I learned

- Grounding matters. My first version asked the LLM about Wikipedia without fetching anything, so it answered from memory. Fetching real text first fixed that.
- Prompts need explicit instructions. A vague prompt returned `{"key_points": []}`. Saying what to extract (5-8 one-sentence points) fixed it.
- The query planner returned full questions at first. Asking for short keyword phrases, with an example on a different topic, fixed that.
- Small local models make mistakes. In one run, an article title got merged into the first key point.
- Local models are slow without a GPU: about 90 seconds for a full run (three searches and a summary).
- Network calls fail. One Wikipedia search timed out in testing, and the script carried on with the other queries.

## Limitations

- Only the first 3 search results per query are used, and only the intro of each article.
- Output quality depends on llama3.2 and isn't checked automatically.

## Next

- Add a final step that turns the key points into a structured Markdown report saved to a file.
