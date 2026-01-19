
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from newsapi import NewsApiClient
import pgeocode
from urllib.parse import urlparse

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

def get_news(
    terms,
    sources,
    news_key,
    logo_token,
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
    
    all_articles = response.get("articles", [])

    # Try strict source name matching first
    articles = [
        a for a in all_articles
        if a.get("source", {}).get("name") in sources
    ]

    # If nothing matched, try a case-insensitive partial match (e.g., "Slate" vs "Slate Magazine")
    if not articles:
        normalized_sources = [s.lower().replace('magazine', '').strip() for s in sources]
        matched = []
        for a in all_articles:
            name = (a.get("source", {}).get("name") or "").lower()
            if any(ns in name or name in ns for ns in normalized_sources):
                matched.append(a)
        # preserve order and dedupe by URL
        articles = list({a.get('url'): a for a in matched}.values())

    # Fallback: if still no results, show top articles so the newsletter isn't empty
    fallback_used = False
    if not articles:
        articles = all_articles[:max_articles]
        fallback_used = True

    news_text = """
    <p>Here are some relevant <b>news articles</b> for you:</p>
    """

    if fallback_used:
        news_text += "<p><i>No articles found from preferred sources — showing top results instead.</i></p>"

    news_text += """
    <table style="width: 100%; border-collapse: collapse; background-color: transparent;">
        <tbody>
    """

    for idx, article in enumerate(articles[:max_articles], start=1):
        url = article.get("url")
        title = article.get("title", "Untitled")

        if not url:
            continue

        domain = urlparse(url).netloc.replace("www.", "")
        logo_url = f"https://img.logo.dev/{domain}?token={logo_token}"

        news_text += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; width: 40px; vertical-align: middle;">
                <img src="{logo_url}" alt="" style="width: 32px; height: 32px; border-radius: 4px; object-fit: contain;">
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 16px; vertical-align: middle;">
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
