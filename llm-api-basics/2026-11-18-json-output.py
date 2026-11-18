
import requests
import json

emails = ["Dear Customer Support Team, My approved personal loan was scheduled for disbursement over two weeks ago, yet the funds have still not been credited to my account. This unacceptable delay is causing me severe financial inconvenience, and I have received no clear updates despite multiple follow-ups. Please resolve this and release the funds within the next 24 hours, or I will be forced to cancel my application and move all my banking accounts to another institution immediately.", "Hello, I am looking to open a new Fixed Deposit with your bank and would like to know the latest interest rates for tenures ranging from 1 to 3 years. Could you also share the applicable rates for senior citizens and any minimum deposit requirements? There is no rush, so please reply whenever convenient.", "Dear Support Team, I recently relocated and need to update the registered residential address linked to my savings account so I can receive my new debit card and upcoming bank statements at the correct location. I have attached a scanned copy of my utility bill as proof of my new address. Please process this update within the next few business days."]

system_prompt = """Classify the customer email. Reply only with JSON: {"intent": "complaint|query|request", "urgency": "low|medium|high", "summary": "one sentence"}.
    Examples:
        complaint: "customer is unhappy about something that went wrong",
        query: "customer wants information",
        request: "customer wants the bank to perform an action",
        summary: "one complete sentence, written in the third person.",
        Email: "My card was blocked and nobody has called me back." → intent: complaint;
        Email: "What documents are needed to open a current account?" → intent: query;
        Email: "Please increase my card limit to 2 lakh." → intent: request"""


def ask(email, system_prompt = None):
    messages = []
    if system_prompt is not None:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": email})
    payload = {"model": "llama3.2",
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0}}
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=60)
        response.raise_for_status()
        reply_text = response.json()
        data = json.loads(reply_text["message"]["content"])
        return data
    except json.JSONDecodeError as error:
        print(f"Invalid JSON format: {error}")
    except KeyError as error2:
        print(f"Invalid JSON Key: {error2}")
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error)
        return

def main():
    for email in emails:
        reply_with = ask(email, system_prompt)
        if reply_with is not None:
            reply_intent = reply_with.get("intent","MISSING")
            reply_urgency = reply_with.get("urgency","MISSING")
            reply_summary = reply_with.get("summary","MISSING")
            print(f"{reply_intent} | {reply_urgency} | {reply_summary}")


if __name__ == "__main__":
    main()





