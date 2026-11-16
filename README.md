# Weather Fetcher
A small Python command-line tool that shows the current temperature and wind speed for any city, using the free [Open-Meteo](https://open-meteo.com/) API. No API key is needed.

## Requirements
- Python 3
- `requests` (`pip install requests`)

## How to run
```
python 2026-11-15-weather-fetcher.py
```
Enter a city name when prompted.

## Example output
```
Enter city: Palakkad
Palakkad: 27.5°C, wind 8.3 km/h
```

## How it works
- `fetch_data(url)` sends a request and returns the parsed JSON, with a timeout and HTTP error checking.
- `get_coordinates(results)` keeps the name, latitude and longitude from the geocoding results.
- `get_weather(weather_data)` extracts the current temperature and wind speed.
- `WeatherReport` is a class that stores the values and formats the summary line.
- `main()` ties it together and handles empty input, unknown cities and network errors.

## Limitations
- Uses the first matching city (for example, the first "Chennai" returned).
- Shows only current temperature and wind speed.
