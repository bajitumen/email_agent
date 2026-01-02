
import pandas as pd
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import json
import re
import random
import time
from newsapi import NewsApiClient
import pgeocode
import os

def get_weather(zip_code):
    endpoint = "https://api.open-meteo.com/v1/forecast"
    nomi = pgeocode.Nominatim('us')
    result = nomi.query_postal_code(zip_code)
    params = {
        "latitude": result['latitude'],
        "longitude": result['longitude'],
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "timezone": "America/Los_Angeles"
    }
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        max_temp = weather_data['daily']['temperature_2m_max'][0]
        min_temp = weather_data['daily']['temperature_2m_min'][0]
        added_text = "Looks like the weather's perfect today!" if 70 <= max_temp <= 90 else "Bundle up or cool down!"
        return f"High: {max_temp}°F, Low: {min_temp}°F. {added_text}"
    except requests.RequestException:
        return "Weather data unavailable."

def get_news(
    terms,
    sources,
    news_key,
    days_back=1,
    max_articles=5
):

    newsapi = NewsApiClient(api_key=news_key)

    query = " OR ".join(f'"{term}"' for term in terms)

    from_date = (datetime.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    to_date = datetime.today().strftime('%Y-%m-%d')

    try:
        response = newsapi.get_everything(
            q=query,
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='relevancy'
        )
    except Exception:
        return "<p>News unavailable.</p>"
    
    articles = [
        a for a in response.get("articles", [])
        if a.get("source", {}).get("name") in sources
    ]

    news_text = """
    <p>Here are some relevant <b>news articles</b> for you:</p>
    <table style="width: 100%; border-collapse: collapse; background-color: transparent;">
        <tbody>
    """

    for idx, article in enumerate(articles[:max_articles], start=1):
        url = article.get("url")
        title = article.get("title", "Untitled")

        if not url:
            continue

        news_text += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 16px;">
                <a href="{url}" style="text-decoration: none; color: #555;">
                    {title}
                </a>
            </td>
        </tr>
        """

    news_text += """
        </tbody>
    </table>
    """

    return news_text

def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password):
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(login, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
