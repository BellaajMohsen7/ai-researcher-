from crewai import Agent, LLM


def create_analyst_agent(llm: LLM) -> Agent:
    return Agent(
        role="AI News Analyst",
        goal=(
            "Analyze raw crawled data and categorize every item "
            "into exactly one of these categories: "
            "ai_models, frameworks, tools, courses, skills, "
            "opportunities. Remove duplicates, verify relevance, "
            "and add importance scores (1-10)."
        ),
        backstory=(
            "You are a senior AI industry analyst with 10 years "
            "of experience. You can instantly recognize the "
            "significance of any AI development. You understand "
            "the difference between a new model release vs a "
            "framework update vs a tool launch. You are precise "
            "and never miscategorize items."
        ),
        llm=llm,           # ← injected
        verbose=True,
        allow_delegation=False,
        max_iter=7,
    )