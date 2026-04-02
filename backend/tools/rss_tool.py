import feedparser
from datetime import datetime, timedelta
from crewai.tools import tool

AI_RSS_FEEDS = [
    "https://blog.google/technology/ai/rss/",
    "https://openai.com/blog/rss.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://www.deeplearning.ai/the-batch/feed/",
]


@tool("fetch_ai_rss_feeds")
def fetch_ai_rss_feeds(max_per_feed: int = 1) -> str:
    """Parse multiple AI RSS feeds for latest articles.
    Returns combined list of recent articles."""

    all_articles = []
    cutoff = datetime.now() - timedelta(days=2)

    for feed_url in AI_RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_per_feed]:
                published = None
                if hasattr(entry, "published_parsed"):
                    if entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])

                if published and published < cutoff:
                    continue

                all_articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:150],
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url),
                    "published": published.isoformat() if published else "unknown",
                })
        except Exception:
            continue

    return str(all_articles) if all_articles else "No RSS data."