from crewai import Agent, LLM


def create_writer_agent(llm: LLM) -> Agent:
    return Agent(
        role="AI Report Writer",
        goal=(
            "Take the analyzed and categorized AI news data "
            "and produce a structured JSON output following "
            "the exact schema. Each item must have: name, "
            "description, source_url, importance_score, "
            "and category. Also write a brief executive "
            "summary of today's most important developments."
        ),
        backstory=(
            "You are a technical writer who specializes in "
            "AI industry briefings. You write concise, "
            "informative summaries. You always output valid "
            "JSON. You never invent information - you only "
            "report what the analyst verified."
        ),
        llm=llm,           # ← injected
        verbose=True,
        allow_delegation=False,
        max_iter=8,
    )