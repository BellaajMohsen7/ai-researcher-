import os
import sys
import asyncio
import logging

# Fix Windows encoding for CrewAI's stdout override
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agents.crew_setup import AIDailyNewsCrew

logging.basicConfig(level=logging.INFO)


async def run_test():
    print("\n--- STARTING CREWAI TEST ---\n")

    try:
        crew = AIDailyNewsCrew()

        print("\nAgents are now crawling and analyzing...\n")
        result = await crew.run()

        print("\n--- CREW FINISHED SUCCESSFULLY! ---\n")

        stats = result.get("stats", {})
        print(f"Items Collected: {stats.get('total_items')}")
        print(f"LLM Provider Used: {stats.get('llm_provider_used')}")

    except Exception as e:
        print(f"\n--- ERROR RUNNING CREW ---\n{e}")


if __name__ == "__main__":
    asyncio.run(run_test())
