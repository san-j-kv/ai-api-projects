
import requests

def ask(question):
    payload = {"model": "llama3.2",
        "messages": [{"role": "user", "content": question}],
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
    reply = ask(question)
    if reply is not None:
        print(reply)


if __name__ == "__main__":
    main()


