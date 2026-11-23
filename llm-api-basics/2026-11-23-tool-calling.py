import requests


def fetch_data(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


tools = [
            {"type": "function",
            "function": {
                "name": "get_weather",
                "description": "returns the latest weather data for the chosen location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to be fetched as a string"},
                                  },
                    "required": ["location"]
                              }
                        }
            }
        ]


def chat(messages):
    payload = {"model": "llama3.2",
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0},
            "tools": tools}
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=60)
        response.raise_for_status()
        reply_text = response.json()
        return reply_text["message"]
    except KeyError as error2:
        print(f"Invalid JSON Key: {error2}")
    except requests.exceptions.RequestException as error:
        print("Unable to fetch the response: ", error)
        return

def get_weather(location):
    city = location.strip()
    if city == "":
        return "Please enter a city name"
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    try:
        data = fetch_data(url)
    except requests.exceptions.RequestException as error:
        return f"Could not fetch data: {error}"
    results = data.get("results")
    if results is None:
        return "City not found"
    rows = get_coordinates(results)
    req_row = rows[0]
    latitude = req_row["latitude"]
    longitude = req_row["longitude"]
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    try:
        weather_data = fetch_data(forecast_url)
    except requests.exceptions.RequestException as error2:
        return f"Could not fetch data: {error2}"
    temperature = weather_data["current"]["temperature_2m"]
    wind = weather_data["current"]["wind_speed_10m"]
    return f'{req_row["name"]}: {temperature}°C, wind {wind} km/h'

available_functions = {"get_weather": get_weather}


def get_coordinates(results):
# Restricting the data to the fields we are interested in
    rows = []
    for place in results:
        rows.append({
            "name": place["name"],
            "latitude": place["latitude"],
            "longitude": place["longitude"]
            })
    return rows

def main():
    messages = [{"role": "system", "content": "You are a helpful assistant. Answer normally. Call get_weather only when the user asks about the weather. Never invent other tools."}, {"role": "user", "content": "What's the weather in London?"}]
    reply = chat(messages)
    if reply is None:
        return
    if reply.get("tool_calls"):
        messages.append(reply)
        for call in reply["tool_calls"]:
            name = call["function"]["name"]
            arguments = call["function"]["arguments"]
            function = available_functions.get(name)
            if function is None:
                result = f"Unknown Function: {name}"
            else:
                result = function(arguments["location"])
            messages.append({"role": "tool", "tool_name": name, "content": str(result)})
        final = chat(messages)
        if final is not None:
            print (final["content"])
    else:
        print (reply["content"])


if __name__ == "__main__":
    main()
