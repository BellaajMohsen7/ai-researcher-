import httpx
import time
from datetime import datetime, timedelta
from crewai.tools import tool
from config import settings

DEVTO_BASE_URL = "https://dev.to/api"

AI_TAGS = ["ai", "llm", "machinelearning"]


@tool("search_devto_articles")
def search_devto_articles(tag: str = "ai", per_page: int = 3) -> str:
    """Search Dev.to for latest AI articles and tutorials.
    Returns titles, descriptions, tags, reactions, and URLs.
    No API key required for public endpoints."""
    
    print("\n\n[RATE LIMIT RESET] Sleeping for 65 seconds to reset Groq 12K TPM limit... Hold tight!\n\n")
    time.sleep(65)

    headers = {"Content-Type": "application/json"}
    # Add API key if configured (increases rate limit)
    if settings.devto_api_key:
        headers["api-key"] = settings.devto_api_key

    results = []
    cutoff = datetime.now() - timedelta(days=2)

    for ai_tag in AI_TAGS:
        try:
            response = httpx.get(
                f"{DEVTO_BASE_URL}/articles",
                params={
                    "tag": ai_tag,
                    "per_page": per_page,
                    "top": 1,           # top articles from last 1 day
                    "state": "fresh",   # recently published
                },
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            articles = response.json()

            for art in articles:
                published_str = art.get("published_at", "")
                try:
                    published_dt = datetime.fromisoformat(
                        published_str.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                    if published_dt < cutoff:
                        continue
                except Exception:
                    pass

                results.append({
                    "title": art.get("title", ""),
                    "description": art.get("description", "")[:150],
                    "url": art.get("url", ""),
                    "source": "Dev.to",
                    "tag": ai_tag,
                    "reactions": art.get("positive_reactions_count", 0),
                    "comments": art.get("comments_count", 0),
                    "reading_time": art.get("reading_time_minutes", 0),
                    "published": published_str,
                    "author": art.get("user", {}).get("name", ""),
                })

        except Exception:
            continue

    # Deduplicate by URL and sort by reactions
    seen_urls = set()
    unique_results = []
    for item in results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique_results.append(item)

    unique_results.sort(key=lambda x: x["reactions"], reverse=True)
    return str(unique_results[:10]) if unique_results else "No Dev.to articles found."


@tool("search_devto_by_query")
def search_devto_by_query(query: str = "large language model") -> str:
    """Search Dev.to articles by a specific keyword query.
    Useful for finding tutorials and deep-dives on specific AI topics."""

    headers = {"Content-Type": "application/json"}
    if settings.devto_api_key:
        headers["api-key"] = settings.devto_api_key

    try:
        response = httpx.get(
            f"{DEVTO_BASE_URL}/articles/search",
            params={"q": query, "per_page": 8},
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        articles = response.json()

        results = []
        for art in articles:
            results.append({
                "title": art.get("title", ""),
                "description": art.get("description", "")[:150],
                "url": art.get("url", ""),
                "source": "Dev.to",
                "reactions": art.get("positive_reactions_count", 0),
                "tags": art.get("tag_list", []),
                "published": art.get("published_at", ""),
                "author": art.get("user", {}).get("name", ""),
            })

        results.sort(key=lambda x: x["reactions"], reverse=True)
        return str(results) if results else f"No Dev.to results for '{query}'."

    except Exception as e:
        return f"Dev.to search failed: {e}"