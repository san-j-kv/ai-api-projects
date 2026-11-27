import requests
import json
import datetime

# Wikipedia's search/extract endpoint
action_api = "https://en.wikipedia.org/w/api.php"

# Wikipedia asks API users to identify themselves, so requests carry a User-Agent
headers = {"User-Agent": "research-assistant/0.1 (https://github.com/san-j-kv/ai-api-projects)"}

def search_wikipedia(topic):
    # Call 1: search Wikipedia for the top 3 matching article titles
    search = requests.get(action_api, timeout=30, headers=headers, params={"action": "query", "list": "search", "srsearch": topic, "srlimit": 3, "format": "json"})
    search.raise_for_status()
     # The response is a list of dicts; pull just the title from each one
    items = search.json()["query"]["search"]
    titles = [item["title"] for item in items]
    if not titles:
        return [] # nothing found; the caller handles the empty list
    else:
        # The extracts API takes several titles joined by "|"
        joined = "|".join(titles)
    # Call 2: fetch the plain-text intro of every title in one request
    extracts = requests.get(action_api, timeout=30, headers=headers, params={"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1, "titles": joined, "format": "json"})
    extracts.raise_for_status()
    # Pages come back as a dict keyed by page id, so loop over .values()
    extract_response = extracts.json()["query"]["pages"]
    extract_text = [] # created BEFORE the loop so it keeps all articles
    for page in extract_response.values():
        extract_text.append({"title": page["title"], "extract": page.get("extract","")})
    return extract_text # returned AFTER the loop, once, with every article


def plan_queries(topic):
    # The system prompt tells the model its job, the exact JSON shape, and gives an example on a different topic (so it copies the style, not the content)
    system_prompt = 'You plan Wikipedia searches. Given a topic, return exactly 3 short search queries that cover different angles, such as causes, key players and consequences. Return only JSON like {"queries": ["...", "...", "..."]}. Use short keyword phrases, not questions. For example: ["Dot-com bubble causes", "Dot-com bubble key companies", "Dot-com bubble aftermath"]'
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": f"Topic: {topic}"})
    payload = {"model": "llama3.2",
            "messages": messages,
            "format": "json",
            "stream": False, # one complete reply, not chunks
            "options": {"temperature": 0, "num_ctx": 8192}} # temp 0 = repeatable; num_ctx = context size
    try:
        # Local Ollama server. Long timeout because local models can be slow
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=180)
        response.raise_for_status()
        # Ollama's reply wraps the model text in ["message"]["content"];
        # that text is itself JSON, so it is parsed a second time
        data = json.loads(response.json()["message"]["content"])
        queries = data["queries"]
        if not queries:
            return [topic] # model returned an empty list -> use the plain topic
        return queries
    except (json.JSONDecodeError, KeyError):
        return [topic] # bad JSON or missing "queries" key -> use the plain topic
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error)
        return [topic] # Ollama not running / timed out -> use the plain topic

# Chain step 4: turn the key points into a Markdown report, add sources, save to a file
def write_report(topic, key_points, articles):
    # Tell the model to use ONLY the given points; sources are added by code below, so the model can't invent them
    system_prompt = 'You write short research reports. You are given a topic and key points. Write a Markdown report with a # title, a ## Summary of 2-3 sentences, and a ## Key points section listing the given points. Use only the given points. Do not add facts or sources.'
    # Turn the list of key points into one text block, one "- point" per line
    points_text = ""
    for point in key_points:
        points_text += f"- {point}\n"
    # The Sources section is built from the real article titles, not by the LLM
    sources = "\n\n## Sources\n"
    for art in articles:
        # Wikipedia URL for each article: spaces in the title become underscores
        link = f"https://en.wikipedia.org/wiki/{art['title'].replace(' ','_')}"
        # Add one Markdown link line per article (must sit inside the loop)
        sources += f"- [{art['title']}]({link})\n"
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    # Label the key points clearly so the small model uses them as given
    messages.append({"role": "user", "content": f"Topic: {topic}\n\nKey Points: \n{points_text}"})
    # No "format": "json" here: we want plain Markdown text back, not JSON
    payload = {"model": "llama3.2",
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192}}
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=180)
        response.raise_for_status()
        # The reply is plain markdown text
        report = response.json()["message"]["content"]
        # LLM-written report + code-built sources = final report text
        full_report = report + sources
        # Today's date as text, e.g. 2026-11-27, for the filename
        date = str(datetime.date.today())
        # Filename-safe topic: lowercase, spaces become dashes
        slug = topic.lower().replace(' ','-')
        filename = f"{date}-{slug}-report.md"
        # "w" creates the file (or overwrites an existing one); utf-8 keeps special characters intact
        with open(filename,"w",encoding="utf-8") as f:
            f.write(full_report)
        print(f"Saved: {filename}")
        return full_report
    except KeyError as error2:
        print(f"Invalid JSON Key: {error2}") # expected key missing from the reply
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error) # network / Ollama problem
        return

def summarize(topic, articles):
    system_prompt = 'Extract 5 to 8 key points about the topic from the extracts. Each point is one short sentence. Return JSON: {"key_points": [...]}. Use only the extracts.'
    # Build one text block with every article. "+=" ADDS each article to the text (Plain "=" would overwrite, leaving only the last article.)
    # [:1500] trims each extract so the prompt fits comfortably in the context window
    article_text = ""
    for art in articles:
        article_text += f"Title: {art['title']}\n{art['extract'][:1500]}\n\n"
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": f"Topic: {topic}\n\n{article_text}"})
    payload = {"model": "llama3.2",
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192}}
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=180)
        response.raise_for_status()
        # Unwrap Ollama's reply and parse the model's JSON text into a Python dict
        return json.loads(response.json()["message"]["content"])
    except json.JSONDecodeError as error:
        print(f"Invalid JSON format: {error}") # model's text wasn't valid JSON
    except KeyError as error2:
        print(f"Invalid JSON Key: {error2}") # expected key missing from the reply
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error) # network / Ollama problem
        return

def main():
    # query   = the topic the user typed
    # queries = the list of 3 sub-queries from plan_queries
    # q       = one sub-query inside the loop
    query = input("Topic to summarize: ").strip()
    if query == "":
        print("Please enter the topic you would like to learn more about.")
        return
    # Chain step 1: plan the searches
    queries = plan_queries(query)
    all_articles = [] # every article collected across all sub-queries
    seen_titles = set() # titles already collected (a set makes duplicate checks easy)
    # Chain step 2: search Wikipedia once per sub-query
    for q in queries:
        print(f"Searching: {q}")
        try:
            articles = search_wikipedia(q)
        except requests.exceptions.RequestException as error:
            print("Could not fetch data: ", error)
            continue # skip this sub-query, keep going with the others
        # Different sub-queries often return the same page, so keep each title once
        for art in articles:
            if art["title"] not in seen_titles:
                seen_titles.add(art["title"])
                all_articles.append(art)
    if not all_articles:
        print("No articles found.")
        return
    # Chain step 3: summarize the combined articles, then print the result
    result = summarize(query, all_articles)
    if result is not None:
        print(json.dumps(result, indent=2)) # indent=2 makes the JSON readable
        write_report(query, result.get("key_points", []), all_articles) # Chain step 4: write the report; .get(..., []) gives an empty list instead of crashing if the key is missing
    else:
        print("No data available.")


# Run main() only when this file is run directly (not when imported)
if __name__ == "__main__":
    main()
