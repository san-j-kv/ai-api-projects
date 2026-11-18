

import requests

def ask(question, system_prompt = None):
    messages = []
    if system_prompt is not None:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})
    payload = {"model": "llama3.2",
            "messages": messages,
            "stream": False}
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error)
        return
    reply_text = response.json()
    return reply_text["message"]["content"]

def main():
    question = input("Let's jump in, ask your query: ")
    system_prompt = "You are a banking analyst. Answer in exactly 3 bullet points."
    # The plain answer
    reply_without = ask(question)
    if reply_without is not None:
        print("WITHOUT: ",reply_without)
    # Then the system prompt
    reply_with = ask(question, system_prompt)
    if reply_with is not None:
        print("WITH: ",reply_with)


if __name__ == "__main__":
    main()



