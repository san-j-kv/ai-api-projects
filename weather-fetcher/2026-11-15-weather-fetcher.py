
import requests

class WeatherReport:
    def __init__ (self, name, temperature, wind):
        self.name = name
        self.temperature = temperature
        self.wind = wind

    def __str__ (self):
        return f"{self.name}: {self.temperature}°C, wind {self.wind} km/h"

def fetch_data(url):
# Fetching the JSON data from the URL
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

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
# Requesting user to input a city
    city = input("Enter city: ").strip()
    if city == "":
        print("Please enter a city name")
        return
# Defining url with city input from user
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
# Adding a function to fetch data
    try:
        data = fetch_data(url)
# Adding an exception handling for the data being fetched
    except requests.exceptions.RequestException as error:
        print("Could not fetch data: ", error)
        return
    results = data.get("results")
    if results is None:
        print("City not found")
        return
    rows = get_coordinates(results)
    req_row = rows[0]
    latitude = req_row["latitude"]
    longitude = req_row["longitude"]
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    try:
        weather_data = fetch_data(forecast_url)
    except requests.exceptions.RequestException as error2:
        print("Could not fetch data: ", error2)
        return
    weather = get_weather(weather_data)
    report = WeatherReport(req_row["name"], weather["temperature"], weather["wind"])
    print(report)

def get_weather(weather_data):
# Fetching Temperature and Wind values
    return{
            "temperature": weather_data["current"]["temperature_2m"],
            "wind": weather_data["current"]["wind_speed_10m"],
            }

if __name__ == "__main__":
    main()


