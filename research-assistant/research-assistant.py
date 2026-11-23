import requests
import json


action_api = "https://en.wikipedia.org/w/api.php"

headers = {"User-Agent": "research-assistant/0.1 (https://github.com/san-j-kv/ai-api-projects)"}

def search_wikipedia(topic):
    search = requests.get(action_api, timeout=30, headers=headers, params={"action": "query", "list": "search", "srsearch": topic, "srlimit": 3, "format": "json"})
    search.raise_for_status()
    items = search.json()["query"]["search"]
    titles = [item["title"] for item in items]
    if not titles:
        return []
    else:
        joined = "|".join(titles)
    extracts = requests.get(action_api, timeout=30, headers=headers, params={"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1, "titles": joined, "format": "json"})
    extracts.raise_for_status()
    extract_response = extracts.json()["query"]["pages"]
    extract_text = []
    for page in extract_response.values():
        extract_text.append({"title": page["title"], "extract": page.get("extract","")})
    return extract_text


def summarize(topic, articles):
    system_prompt = 'Extract 5 to 8 key points about the topic from the extracts. Each point is one short sentence. Return JSON: {"key_points": [...]}. Use only the extracts.'
    article_text = ""
    for art in articles:
        article_text += f"Title: {art['title']}\n{art['extract']}\n\n"
    print(len(article_text))
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
        return json.loads(response.json()["message"]["content"])
    except json.JSONDecodeError as error:
        print(f"Invalid JSON format: {error}")
    except KeyError as error2:
        print(f"Invalid JSON Key: {error2}")
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error)
        return

def main():
    query = input("Topic to summarize: ").strip()
    if query == "":
        print("Please enter the topic you would like to learn more about.")
        return
    try:
        data = search_wikipedia(query)
    except requests.exceptions.RequestException as error:
        print("Could not fetch data: ", error)
        return
    if not data:
        print("No articles found.")
        return
    result = summarize(query, data)
    if result is not None:
        print(json.dumps(result, indent=2))
    else:
        print("No data available.")


if __name__ == "__main__":
    main()
