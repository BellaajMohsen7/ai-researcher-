from crewai import Agent, LLM
from tools.arxiv_tool import search_arxiv
from tools.news_tool import search_ai_news
from tools.github_tool import search_github_trending
from tools.devto_tool import search_devto_articles, search_devto_by_query
from tools.huggingface_tool import search_huggingface_models, fetch_huggingface_papers
from tools.rss_tool import fetch_ai_rss_feeds


def create_academic_crawler_agent(llm: LLM) -> Agent:
    return Agent(
        role="Academic Papers Crawler",
        goal="Find all latest AI/ML papers, model releases, and research from ArXiv and HuggingFace in the last 24 hours.",
        backstory="An expert academic researcher who monitors ArXiv and HuggingFace for cutting-edge AI developments.",
        tools=[search_arxiv, search_huggingface_models, fetch_huggingface_papers],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )

def create_news_crawler_agent(llm: LLM) -> Agent:
    return Agent(
        role="Social & News Crawler",
        goal="Find latest AI news, tutorials, new tools, and GitHub repositories from the last 24 hours.",
        backstory="A rapid news aggregator monitoring NewsAPI, Dev.to, GitHub, and RSS feeds for tech trends.",
        tools=[search_ai_news, search_github_trending, search_devto_articles, search_devto_by_query, fetch_ai_rss_feeds],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )