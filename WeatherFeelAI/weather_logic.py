# weather_logic.py

weather_data = {
    0: ("🧊 Freezing", "#00BFFF"),
    10: ("🥶 Very Cold", "#87CEFA"),
    15: ("❄️ Cold", "#ADD8E6"),
    20: ("🌤 Pleasant", "#90EE90"),
    25: ("😊 Comfortable", "#32CD32"),
    30: ("☀️ Warm", "#FFD700"),
    35: ("🔥 Hot", "#FF8C00"),
    40: ("🥵 Very Hot", "#FF4500")
}


def predict_weather(temp):

    closest = min(weather_data.keys(), key=lambda x: abs(x-temp))

    return weather_data[closest]


def clothing(temp):

    if temp < 10:
        return "🧥 Heavy Jacket, Gloves and Woollen Cap"

    elif temp < 20:
        return "🧥 Jacket or Sweater"

    elif temp < 30:
        return "👕 Cotton T-shirt"

    elif temp < 35:
        return "👕 Light Cotton Clothes"

    return "🩳 Thin Cotton Clothes and Cap"


def hydration(temp):

    if temp < 20:
        return "Drink about 2 litres of water."

    elif temp < 30:
        return "Drink 2.5 litres of water."

    return "Drink 3-4 litres of water."


def safety(temp):

    if temp < 10:
        return "Stay warm and avoid cold winds."

    elif temp < 20:
        return "Perfect weather for outdoor activities."

    elif temp < 30:
        return "Use sunscreen if outdoors."

    return "Avoid direct sunlight between 12 PM and 3 PM."


def mood(temp):

    if temp < 10:
        return "☕ Perfect weather for coffee."

    elif temp < 20:
        return "🚶 Great weather for a walk."

    elif temp < 30:
        return "🌸 Beautiful day outside."

    return "🍦 Time for an ice cream!"


def quote():

    import random

    quotes = [

        "Every day brings a different sky.",

        "Enjoy every season of life.",

        "Nature always has something beautiful to show.",

        "Sunshine is the best medicine.",

        "After every storm comes sunshine."

    ]

    return random.choice(quotes)