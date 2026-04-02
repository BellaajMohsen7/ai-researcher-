import json
from datetime import datetime
from collections import Counter
from storage.json_store import store
from llm.provider import llm
from config import settings
import logging

logger = logging.getLogger(__name__)


class WeeklyReportGenerator:
    """Generates weekly intelligence report from 7 days data."""

    async def generate(self) -> dict:
        """Generate weekly report from last 7 days."""
        logger.info("Generating weekly report...")

        daily_data = store.load_last_7_days()

        if not daily_data:
            return {"error": "No daily data found for report."}

        # === Aggregate statistics ===
        stats = {
            "days_collected": len(daily_data),
            "date_range": {
                "start": daily_data[0]["date"],
                "end": daily_data[-1]["date"],
            },
            "total_items_by_category": {},
            "total_items": 0,
        }

        all_items = {cat: [] for cat in settings.categories}
        all_tags = []

        for day in daily_data:
            for cat in settings.categories:
                items = day.get(cat, [])
                all_items[cat].extend(items)
                for item in items:
                    all_tags.extend(item.get("tags", []))

        for cat in settings.categories:
            count = len(all_items[cat])
            stats["total_items_by_category"][cat] = count
            stats["total_items"] += count

        # === Top items per category (by importance) ===
        top_items = {}
        for cat in settings.categories:
            sorted_items = sorted(
                all_items[cat],
                key=lambda x: x.get("importance_score", 0),
                reverse=True,
            )
            top_items[cat] = sorted_items[:5]

        # === Tag cloud / trending topics ===
        tag_counts = Counter(all_tags)
        trending_tags = tag_counts.most_common(20)

        # === Generate AI summary ===
        summary_prompt = f"""
        Analyze this week's AI news data and write a comprehensive weekly intelligence report.

        Data collected from {stats['date_range']['start']} to {stats['date_range']['end']}.
        Total items: {stats['total_items']}
        Breakdown: {json.dumps(stats['total_items_by_category'])}
        Top trending tags: {trending_tags}

        Top AI Models this week:
        {json.dumps(top_items.get('ai_models', [])[:5], indent=2)}

        Top Tools this week:
        {json.dumps(top_items.get('tools', [])[:5], indent=2)}

        Top Frameworks:
        {json.dumps(top_items.get('frameworks', [])[:5], indent=2)}

        Write a report with these sections:
        1. Executive Summary (5-7 sentences)
        2. Key Trends (3-5 bullet points)
        3. Model Releases Highlights
        4. Notable Tools & Frameworks
        5. Learning Opportunities
        6. Career & Skills Outlook
        7. What to Watch Next Week

        Output as JSON with these section keys.
        """

        try:
            ai_summary = await llm.generate_json(
                summary_prompt,
                system_prompt="You are an AI industry analyst writing a weekly intelligence report.",
            )
        except Exception as e:
            logger.error(f"AI summary failed: {e}")
            ai_summary = {"executive_summary": "Report generation failed."}

        # === Build final report ===
        report = {
            "stats": stats,
            "top_items": top_items,
            "all_items": all_items,
            "trending_tags": [{"tag": t, "count": c} for t, c in trending_tags],
            "ai_analysis": ai_summary,
            "daily_summaries": [
                {
                    "date": d["date"],
                    "total": d.get("stats", {}).get("total_items", 0),
                    "summary": d.get("executive_summary", ""),
                }
                for d in daily_data
            ],
        }

        path = store.save_weekly_report(report)
        logger.info(f"Weekly report saved to {path}")
        return report


weekly_reporter = WeeklyReportGenerator()