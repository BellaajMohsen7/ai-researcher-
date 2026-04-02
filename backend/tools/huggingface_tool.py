import httpx
from crewai.tools import tool


@tool("search_huggingface_models")
def search_huggingface_models(query: str = "") -> str:
    """Search HuggingFace for trending/new AI models.
    Returns model names, downloads, and descriptions."""

    url = "https://huggingface.co/api/models"
    params = {
        "sort": "lastModified",
        "direction": -1,
        "limit": 5,
        "full": False,
    }
    if query:
        params["search"] = query

    response = httpx.get(url, params=params, timeout=15)
    models = response.json()

    results = []
    for m in models:
        results.append({
            "model_id": m.get("modelId", ""),
            "pipeline_tag": m.get("pipeline_tag", ""),
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
            "last_modified": m.get("lastModified", ""),
            "url": f"https://huggingface.co/{m.get('modelId', '')}",
        })

    return str(results) if results else "No HF models found."


@tool("fetch_huggingface_papers")
def fetch_huggingface_papers(max_papers: int = 5) -> str:
    """Fetch today's papers from HuggingFace Daily Papers.
    Args:
        max_papers: Maximum number of papers to fetch (default 15)."""

    url = "https://huggingface.co/api/daily_papers"
    response = httpx.get(url, timeout=15)
    papers = response.json()

    results = []
    for p in papers[:max_papers]:
        paper = p.get("paper", {})
        results.append({
            "title": paper.get("title", ""),
            "summary": paper.get("summary", "")[:150],
            "authors": [a.get("name", "") for a in paper.get("authors", [])[:3]],
            "url": f"https://huggingface.co/papers/{paper.get('id', '')}",
            "upvotes": p.get("numUpvotes", 0),
        })

    return str(results) if results else "No HF papers today."