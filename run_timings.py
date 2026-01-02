import time
from dotenv import load_dotenv
import os
from functions import get_weather, get_news
import requests

load_dotenv()
news_key = os.getenv("NEWS_API_KEY")
if news_key:
    news_key = news_key.strip()

terms = ["housing", "palestine"]
sources = ["NPR", "CNN"]

print("Timing get_weather...")
start = time.time()
weather = get_weather("90042")
print(f"get_weather took {time.time() - start:.2f}s")
print(weather)

print("\nTiming get_news...")
start = time.time()
news_html = get_news(terms=terms, sources=sources, news_key=news_key, days_back=1, max_articles=2)
print(f"get_news took {time.time() - start:.2f}s")
print("news length:", len(news_html))

print("\nTiming dog image fetch...")
start = time.time()
try:
    r = requests.get("https://dog.ceo/api/breeds/image/random", timeout=10)
    r.raise_for_status()
    img = r.json().get("message")
    print(f"dog fetch took {time.time() - start:.2f}s, url: {img}")
except Exception as e:
    print("dog fetch error:", e)
