import json
import os
from datetime import datetime
from crewai import Agent, Crew, Task, Process, LLM
from agents.crawler_agent import create_academic_crawler_agent, create_news_crawler_agent
from agents.analyst_agent import create_analyst_agent
from agents.writer_agent import create_writer_agent
from storage.json_store import store, DailyNewsSchema
from config import settings
import logging

logger = logging.getLogger(__name__)


def get_crawler_llm() -> tuple[LLM, str]:
    """Get an LLM suitable for fast, repetitive tool calling (Groq)."""
    if settings.groq_api_key:
        try:
            llm = LLM(
                model=f"openai/{settings.groq_model}",
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
                temperature=0.3,
            )
            logger.info("CrewAI Crawler will use: Groq")
            return llm, "groq"
        except Exception as e:
            logger.warning(f"Groq LLM init failed: {e}")
    raise RuntimeError("No suitable LLM found for Crawler.")

def get_processor_llm() -> tuple[LLM, str]:
    """Get an LLM suitable for huge context windows (Gemini)."""
    if settings.gemini_api_key:
        try:
            llm = LLM(
                model=f"gemini/{settings.gemini_model}",
                api_key=settings.gemini_api_key,
                temperature=0.3,
            )
            logger.info("CrewAI Processor will use: Gemini")
            return llm, "gemini"
        except Exception as e:
            logger.warning(f"Gemini LLM init failed: {e}")
    
    # Fallback to Groq if Gemini isn't available
    if settings.groq_api_key:
        try:
            llm = LLM(
                model=f"openai/{settings.groq_model}",
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
                temperature=0.3,
            )
            logger.info("CrewAI Processor will use: Groq (Gemini unavailable)")
            return llm, "groq"
        except Exception:
            pass
            
    raise RuntimeError("No suitable LLM found for Processors.")


class AIDailyNewsCrew:
    """The main crew that runs every day at 7 AM."""

    def __init__(self):
        # Resolve LLMs for specific jobs
        self.crawler_llm, self.crawler_provider = get_crawler_llm()
        self.processor_llm, self.llm_provider = get_processor_llm()

        # Split architecture: Groq for fast tools, Gemini for massive context
        self.academic_crawler = create_academic_crawler_agent(self.crawler_llm)
        self.news_crawler = create_news_crawler_agent(self.crawler_llm)
        self.analyst = create_analyst_agent(self.processor_llm)
        self.writer = create_writer_agent(self.processor_llm)

    def _create_tasks(self) -> list:
        today = datetime.now().strftime("%Y-%m-%d")

        crawl_academic_task = Task(
            description=(
                f"Date: {today}\n"
                "Search ALL available sources for AI academic research and models:\n"
                "1. Search ArXiv for new AI/ML papers\n"
                "2. Check HuggingFace for new models\n"
                "3. Fetch HuggingFace daily papers\n\n"
                "Collect EVERYTHING. Do not filter yet."
            ),
            expected_output=(
                "A raw list of all AI papers and models "
                "from ArXiv and HuggingFace, including titles, "
                "descriptions and URLs."
            ),
            agent=self.academic_crawler,
        )

        crawl_news_task = Task(
            description=(
                f"Date: {today}\n"
                "Search ALL available sources for AI news and trends:\n"
                "1. Search NewsAPI for AI news articles\n"
                "2. Check GitHub trending for AI repos\n"
                "3. Search Dev.to for AI articles and tutorials\n"
                "4. Parse AI RSS feeds\n\n"
                "Collect EVERYTHING. Do not filter yet."
            ),
            expected_output=(
                "A raw list of all AI news, tutorials, and repositories "
                "including titles, descriptions, and URLs."
            ),
            agent=self.news_crawler,
        )

        analyze_task = Task(
            description=(
                "Take all the raw crawled data and:\n"
                "1. Remove duplicates (same news from different sources)\n"
                "2. Categorize each item into EXACTLY one:\n"
                "   - ai_models: new model releases/updates\n"
                "   - frameworks: ML framework news\n"
                "   - tools: new AI tools, apps, platforms\n"
                "   - courses: learning resources, tutorials\n"
                "   - skills: skills in demand, career advice\n"
                "   - opportunities: jobs, grants, competitions\n"
                "3. Rate importance 1-10 for each item\n"
                "4. Keep only genuinely AI-related items"
            ),
            expected_output=(
                "Categorized list of AI news items, each with "
                "a category, importance score, and dedup flag."
            ),
            agent=self.analyst,
            context=[crawl_academic_task, crawl_news_task],
        )

        write_task = Task(
            description=(
                "Produce the final structured JSON output.\n"
                "Schema for EACH item in every category:\n"
                "{\n"
                '  "name": "Item title",\n'
                '  "description": "2-3 sentence summary",\n'
                '  "source_url": "https://...",\n'
                '  "source_name": "ArXiv/Dev.to/etc",\n'
                '  "importance_score": 8,\n'
                '  "tags": ["llm", "open-source"]\n'
                "}\n\n"
                "Also add an 'executive_summary' field: "
                "a 3-5 sentence overview of today's top AI developments.\n\n"
                "OUTPUT MUST BE VALID JSON with keys: "
                "executive_summary, ai_models, frameworks, "
                "tools, courses, skills, opportunities."
            ),
            expected_output=(
                "Valid JSON with all categorized items "
                "and an executive summary. Nothing else."
            ),
            agent=self.writer,
            context=[analyze_task],
        )

        return [crawl_academic_task, crawl_news_task, analyze_task, write_task]

    async def run(self) -> dict:
        """Execute the full crew pipeline."""
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Starting daily crew run for {today} | LLM: {self.llm_provider}")

        tasks = self._create_tasks()
        crew = Crew(
            agents=[self.academic_crawler, self.news_crawler, self.analyst, self.writer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        try:
            result = crew.kickoff()
            result_text = str(result)

            # Parse JSON from result — clean markdown if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1]
                result_text = result_text.split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
                result_text = result_text.split("```")[0]

            data = json.loads(result_text.strip())

            # Merge with schema
            daily = DailyNewsSchema.empty(today)
            for cat in settings.categories:
                if cat in data:
                    daily[cat] = data[cat]
            if "executive_summary" in data:
                daily["executive_summary"] = data["executive_summary"]
            daily["stats"]["llm_provider_used"] = self.llm_provider  # ← tracks which was used

            # Save
            path = store.save_daily(today, daily)
            logger.info(f"Saved daily data to {path}")
            return daily

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            daily = DailyNewsSchema.empty(today)
            daily["raw_result"] = str(result)
            daily["stats"]["llm_provider_used"] = self.llm_provider
            store.save_daily(today, daily)
            return daily

        except Exception as e:
            logger.error(f"Crew run failed: {e}")
            raise