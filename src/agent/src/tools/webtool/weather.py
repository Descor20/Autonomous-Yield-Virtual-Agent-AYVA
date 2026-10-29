import requests

def get_weather(latitude: str, longitude: str):
    """
    Récupère la météo en fonction d'une localisation
    """
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["current"]