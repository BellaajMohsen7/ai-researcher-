import arxiv
from datetime import datetime, timedelta
from crewai.tools import tool


@tool("search_arxiv")
def search_arxiv(query: str = "artificial intelligence") -> str:
    """Search ArXiv for latest AI papers from last 24h.
    Returns titles, summaries, and links."""

    search = arxiv.Search(
        query=f"cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND {query}",
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    results = []
    yesterday = datetime.now() - timedelta(days=2)

    for paper in search.results():
        if paper.published.replace(tzinfo=None) >= yesterday:
            results.append({
                "title": paper.title,
                "summary": paper.summary[:150],
                "url": paper.entry_id,
                "published": paper.published.isoformat(),
                "authors": [a.name for a in paper.authors[:3]],
                "categories": paper.categories,
            })

    return str(results) if results else "No new papers found."