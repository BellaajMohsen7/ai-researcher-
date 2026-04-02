import httpx
from bs4 import BeautifulSoup
from crewai.tools import tool


@tool("search_github_trending")
def search_github_trending(language: str = "") -> str:
    """Scrape GitHub trending repos related to AI/ML.
    Returns repo names, descriptions, stars, language."""

    url = "https://github.com/trending"
    if language:
        url += f"/{language}"
    url += "?since=daily"

    headers = {"User-Agent": "Mozilla/5.0 AI-News-Bot/1.0"}
    response = httpx.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    repos = []
    articles = soup.select("article.Box-row")

    ai_keywords = [
        "ai", "ml", "llm", "gpt", "transformer",
        "neural", "deep-learning", "machine-learning",
        "nlp", "computer-vision", "diffusion", "agent",
        "rag", "embedding", "fine-tun", "model",
    ]

    for article in articles[:10]:
        name_tag = article.select_one("h2 a")
        desc_tag = article.select_one("p")
        stars_tag = article.select_one("span.d-inline-block.float-sm-right")

        if name_tag:
            name = name_tag.text.strip().replace("\n", "")
            name = " ".join(name.split())
            desc = (desc_tag.text.strip()[:150] if desc_tag else "")
            full_text = f"{name} {desc}".lower()

            if any(kw in full_text for kw in ai_keywords):
                repos.append({
                    "repo": name,
                    "description": desc,
                    "stars_today": stars_tag.text.strip() if stars_tag else "N/A",
                    "url": "https://github.com/" + name.replace(" ", ""),
                })

    return str(repos) if repos else "No trending AI repos."