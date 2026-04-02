from newsapi import NewsApiClient
from datetime import datetime, timedelta
from crewai.tools import tool
from config import settings


@tool("search_ai_news")
def search_ai_news(query: str = "artificial intelligence") -> str:
    """Search NewsAPI for latest AI news headlines.
    Returns articles with titles, descriptions, sources."""

    if not settings.news_api_key:
        return "NewsAPI key not configured."

    newsapi = NewsApiClient(api_key=settings.news_api_key)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    articles = newsapi.get_everything(
        q=f"({query}) AND (AI OR 'machine learning' OR 'deep learning' OR LLM OR GPT)",
        from_param=yesterday,
        language="en",
        sort_by="publishedAt",
        page_size=3,
    )

    results = []
    for art in articles.get("articles", []):
        results.append({
            "title": art["title"],
            "description": art.get("description", "")[:150],
            "source": art["source"]["name"],
            "url": art["url"],
            "published": art["publishedAt"],
        })

    return str(results) if results else "No news found."