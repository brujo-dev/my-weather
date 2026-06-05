import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENWEATHER_API_KEY", "")


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=it"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.HTTPError:
        if response.status_code != 404:
            print(f"[get_weather] HTTP error {response.status_code} for city '{city}'")
        return None
    except requests.exceptions.ConnectionError:
        return None


def get_weather_emoji(description):
    desc = (description or "").lower()
    if "temporale" in desc:
        return "⛈️"
    if "neve" in desc:
        return "❄️"
    if "pioggia" in desc or "piogg" in desc:
        return "🌧️"
    if "nebbia" in desc or "foschia" in desc:
        return "🌫️"
    if "nuvoloso" in desc or "nuvol" in desc:
        return "☁️"
    if "sereno" in desc or "sole" in desc:
        return "☀️"
    return "🌡️"


def format_weather(data):
    if not data or "weather" not in data or "main" not in data:
        return None
    icon = data["weather"][0].get("icon", "01d")
    description = data["weather"][0]["description"]
    return {
        "city": data["name"],
        "country": data.get("sys", {}).get("country", ""),
        "lat": data.get("coord", {}).get("lat"),
        "lon": data.get("coord", {}).get("lon"),
        "temperature": data["main"]["temp"],
        "description": description,
        "emoji": get_weather_emoji(description),
        "humidity": data["main"]["humidity"],
        "icon": icon,
        "is_night": icon.endswith("n"),
    }


def get_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "it", "cnt": 4}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError):
        return []

    forecast = []
    for entry in data.get("list", []):
        time = datetime.fromtimestamp(entry["dt"]).strftime("%H:%M")
        forecast.append({
            "time": time,
            "temp": entry["main"]["temp"],
            "description": entry["weather"][0]["description"],
        })
    return forecast


def get_forecast_5days(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "it"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.HTTPError:
        return None
    except requests.exceptions.ConnectionError:
        return None

    forecast = []
    for entry in data.get("list", []):
        if "12:00:00" not in entry.get("dt_txt", ""):
            continue
        date = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%A %d/%m")
        forecast.append({
            "date": date,
            "temp": int(entry["main"]["temp"]),
            "temp_min": int(entry["main"]["temp_min"]),
            "temp_max": int(entry["main"]["temp_max"]),
            "description": entry["weather"][0]["description"],
            "humidity": entry["main"]["humidity"],
        })
        if len(forecast) == 5:
            break

    return forecast


if __name__ == "__main__":
    data = get_weather("Rome")
    result = format_weather(data)
    print(result)
    print(get_forecast("Rome"))
