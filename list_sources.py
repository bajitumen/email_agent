from newsapi import NewsApiClient

api_key = input("Enter your NewsAPI key: ")
newsapi = NewsApiClient(api_key=api_key)

sources = newsapi.get_sources(language='en', country='us')

print("\n=== US English News Sources ===\n")
for source in sources.get('sources', []):
    print(f"- {source['name']}")

print(f"\nTotal: {len(sources.get('sources', []))} sources")
