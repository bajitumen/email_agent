import requests
from datetime import datetime
import random
import os
from functions import get_weather, send_email, get_news, get_horoscope

news_key = os.getenv("NEWS_API_KEY")
logo_token = os.getenv("LOGO_DEV_TOKEN")

intros = {
    "Huzzah, another day begins!": 10,
    "Yippee! You're gonna have a great day.": 20,
    "Let's gooooo, today's gonna be a good day.": 10,
    "Let's get this day started!": 30,
    "Hmm... did we snugabug today?": 5,
    "It's gonna be a good day, I have a feeling.": 5,
    "Your horoscope today is that you're gonna slay.": 5,
    "You are so loved, but especially today!": 5,
    "So are you still in bed...er what?": 10,
    "So how's the puppy doing?": 5,
    "Sooo, do you mitch me already...er what?": 5
}

intros_list = list(intros.keys())
weights = list(intros.values())

intro = random.choices(intros_list, weights=weights, k=1)[0]

weather_report = get_weather("90042")
horoscope = get_horoscope("aries")

today = datetime.today()
day_name = today.strftime('%A')

terms = ["housing", "palestine", "ariana grande", "los angeles", "lebanon", "beyonce",
         "climate change", "environmental justice", "beyonce", "sabrina carpenter", 
         "chappell roan", "transportation", "urban planning", "transit justice", "queer", "gaza",
         "mental health", "self care", "wellness", "food justice", "olivia dean",
         "immigrant", "iran", "refugee"]

sources = ["NPR", "Eater", "The Atlantic", "Rolling Stone", "Time", "New York Magazine",
           "The New Yorker", "Al Jazeera English", "Mondoweiss", "CNN", "Democracy Now!", "Slate Magazine", "Billboard",
           "The Huffington Post", "The Washington Post", "Politico", "New York Magazine"]

la_sources = ["Los Angeles Times", "LAist", "KTLA", "LA Magazine", "KCRW"]

news_text = get_news(
    terms=terms,
    sources=sources,
    la_sources=la_sources,
    news_key=news_key,
    logo_token=logo_token,
    days_back=1,
    max_articles=5,
    la_articles=2
)

sender_email = "tumendemberelbaji@gmail.com"
receiver_email = "vy.tran27@gmail.com"
subject = f"{today.strftime('%-m/%-d/%Y')}: Vy Newsletter"

r = random.randint(200, 255)
g = random.randint(200, 255)
b = random.randint(200, 255)

background_color = f'rgba({r}, {g}, {b}, 1)'

dog_api_url = "https://dog.ceo/api/breeds/image/random"
response = requests.get(dog_api_url, timeout=10)
dog = response.json()["message"]

body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 40px 0;">
        <div style="background-color: {background_color}; padding: 21px; margin: 0 auto; border-radius: 10px; max-width: 600px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="background-color: rgba(255, 255, 255, 0.7); padding: 20px; margin: 0 auto; border-radius: 10px; max-width: 600px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
                <p style="font-size: 16px; color: #555555;"><b>Dearest Vy,</b></p>
                <p style="font-size: 16px; color: #555555;">{intro}</p>
                <p style="font-size: 16px; color: #555555;">{weather_report}</p>
                <div style="font-size: 16px; color: #555555;">{news_text}</div>
                <div style="text-align: center; margin-top: 20px;">
                    <img src="{dog}" style="max-width: 400px; border-radius: 10px;">
                </div>
                <p style="font-size: 16px; color: #555555; margin-left: 20px;">Love,<br>Baji &#x2764;</p>
                <p style="font-size: 16px; color: #555555;">{horoscope}</p>
            </div>
        </div>
        </body>
    </html>
"""

smtp_server = "smtp.gmail.com"
smtp_port = 587

login = os.getenv("SMTP_LOGIN")
password = os.getenv("SMTP_PASSWORD")

send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password)
