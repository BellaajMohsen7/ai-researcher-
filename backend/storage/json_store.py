import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from config import settings


class DailyNewsSchema:
    """Schema for a single day's data."""
    @staticmethod
    def empty(date_str: str) -> dict:
        return {
            "date": date_str,
            "collected_at": datetime.now().isoformat(),
            "ai_models": [],
            "frameworks": [],
            "tools": [],
            "courses": [],
            "skills": [],
            "opportunities": [],
            "raw_sources": {
                "arxiv": [],
                "news": [],
                "devto": [],
                "github": [],
                "huggingface": [],
                "rss": [],
            },
            "stats": {
                "total_items": 0,
                "sources_scraped": 0,
                "llm_provider_used": "",
            }
        }


class JsonStore:
    """Read/write daily JSON data and weekly reports."""

    def __init__(self):
        self.daily_dir = settings.daily_dir
        self.weekly_dir = settings.weekly_dir

    def _daily_path(self, date_str: str) -> Path:
        return self.daily_dir / f"{date_str}.json"

    def _weekly_path(self, week_id: str) -> Path:
        return self.weekly_dir / f"week-{week_id}.json"

    def save_daily(self, date_str: str, data: dict) -> Path:
        """Save one day's collected data."""
        path = self._daily_path(date_str)
        total = sum(len(data.get(cat, [])) for cat in settings.categories)
        data["stats"]["total_items"] = total
        data["date"] = date_str

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    def load_daily(self, date_str: str) -> Optional[dict]:
        """Load one day's data."""
        path = self._daily_path(date_str)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def load_date_range(self, start: str, end: str) -> list:
        """Load all daily data between two dates."""
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        results = []
        current = start_dt
        while current <= end_dt:
            date_str = current.strftime("%Y-%m-%d")
            data = self.load_daily(date_str)
            if data:
                results.append(data)
            current += timedelta(days=1)
        return results

    def load_last_7_days(self) -> list:
        """Load the last 7 days of data."""
        end = datetime.now()
        start = end - timedelta(days=6)
        return self.load_date_range(
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        )

    def save_weekly_report(self, report: dict) -> Path:
        """Save weekly report."""
        year = datetime.now().isocalendar()[0]
        week_num = datetime.now().isocalendar()[1]
        week_id = f"{year}-W{week_num:02d}"
        report["week_id"] = week_id
        report["generated_at"] = datetime.now().isoformat()

        path = self._weekly_path(week_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return path

    def load_weekly_report(self, week_id: str) -> Optional[dict]:
        """Load a specific weekly report."""
        path = self._weekly_path(week_id)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_weekly_reports(self) -> list:
        """List all available weekly reports."""
        files = sorted(self.weekly_dir.glob("week-*.json"))
        return [f.stem.replace("week-", "") for f in files]

    def list_daily_files(self) -> list:
        """List all available daily files."""
        files = sorted(self.daily_dir.glob("*.json"))
        return [f.stem for f in files]


# Singleton
store = JsonStore()