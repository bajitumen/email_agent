
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
        if max_temp < 70:
            added_text = "It's chilly out there — bundle up!"
        elif max_temp > 90:
            added_text = "It's hot today — stay cool and hydrated!"
        else:
            added_text = "Looks like the weather's perfect today!"
        return f"High: {max_temp}°F, Low: {min_temp}°F. {added_text}"
    except requests.RequestException:
        return "Weather data unavailable."

from datetime import datetime, timedelta

def get_news(
    terms,
    sources,
    news_key,
    logo_dev_token,
    days_back=1,
    max_articles=5,
    logo_px=28,
):
    """
    Returns HTML with a square Logo.dev logo to the left of each headline.
    Logos are resolved using a source-name → domain mapping.
    """

    newsapi = NewsApiClient(api_key=news_key)

    query = " OR ".join(f'"{term}"' for term in terms)

    from_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    to_date = datetime.today().strftime("%Y-%m-%d")

    try:
        response = newsapi.get_everything(
            q=query,
            from_param=from_date,
            to=to_date,
            language="en",
            sort_by="relevancy",
        )
    except Exception:
        return "<p>News unavailable.</p>"

    articles = [
        a for a in response.get("articles", [])
        if a.get("source", {}).get("name") in sources
    ]

    def logo_dev_url(domain: str) -> str:
        # request higher res for crisp rendering
        size = max(64, logo_px * 2)
        return f"https://img.logo.dev/{domain}?token={logo_dev_token}&size={size}&format=png"

    news_text = """
    <p>Here are some relevant <b>news articles</b> for you:</p>
    <table style="width: 100%; border-collapse: collapse; background-color: transparent;">
      <tbody>
    """

    for article in articles[:max_articles]:
        url = article.get("url")
        title = article.get("title", "Untitled")
        source_name = article.get("source", {}).get("name", "")

        if not url:
            continue

        domain = SOURCE_DOMAIN_MAP.get(source_name)

        if domain:
            logo_html = f"""
              <img
                src="{logo_dev_url(domain)}"
                alt="{source_name} logo"
                width="{logo_px}"
                height="{logo_px}"
                style="
                  display:block;
                  width:{logo_px}px;
                  height:{logo_px}px;
                  border-radius:4px;
                "
                loading="lazy"
                referrerpolicy="no-referrer"
              />
            """
        else:
            # fallback spacer keeps alignment clean
            logo_html = f'<div style="width:{logo_px}px; height:{logo_px}px;"></div>'

        news_text += f"""
        <tr>
          <td style="
            padding: 8px 10px 8px 0;
            border-bottom: 1px solid #ddd;
            width: {logo_px + 10}px;
            vertical-align: top;
          ">
            {logo_html}
          </td>
          <td style="
            padding: 8px 0;
            border-bottom: 1px solid #ddd;
            font-size: 16px;
            vertical-align: top;
          ">
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
