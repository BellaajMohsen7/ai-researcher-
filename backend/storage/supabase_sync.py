import json
import logging
from typing import Optional

logger = logging.getLogger("ai-news.supabase")

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("supabase-py not installed, Supabase sync disabled")


class SupabaseSync:
    """Syncs JSON data to Supabase for persistence."""

    def __init__(self, url: str, key: str):
        self.client: Optional[Client] = None
        if not url or not key:
            logger.info("Supabase credentials not set, sync disabled")
            return
        if not SUPABASE_AVAILABLE:
            return
        try:
            self.client = create_client(url, key)
            logger.info("Supabase sync enabled")
        except Exception as e:
            logger.error(f"Failed to init Supabase: {e}")

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def push_daily(self, date_str: str, data: dict):
        """Push daily collection to Supabase."""
        if not self.enabled:
            return
        try:
            self.client.table("daily_collections").upsert({
                "date": date_str,
                "data": data,
            }).execute()
            logger.info(f"Synced daily {date_str} to Supabase")
        except Exception as e:
            logger.error(f"Supabase push_daily failed: {e}")

    def pull_daily(self, date_str: str) -> Optional[dict]:
        """Pull daily collection from Supabase."""
        if not self.enabled:
            return None
        try:
            res = self.client.table("daily_collections") \
                .select("data") \
                .eq("date", date_str) \
                .maybe_single() \
                .execute()
            if res and res.data:
                return res.data["data"]
        except Exception as e:
            logger.error(f"Supabase pull_daily failed: {e}")
        return None

    def list_daily_dates(self) -> list:
        """List all available daily dates from Supabase."""
        if not self.enabled:
            return []
        try:
            res = self.client.table("daily_collections") \
                .select("date") \
                .order("date") \
                .execute()
            return [r["date"] for r in res.data]
        except Exception as e:
            logger.error(f"Supabase list_daily failed: {e}")
        return []

    def push_weekly(self, week_id: str, data: dict):
        """Push weekly report to Supabase."""
        if not self.enabled:
            return
        try:
            self.client.table("weekly_reports").upsert({
                "week_id": week_id,
                "data": data,
            }).execute()
            logger.info(f"Synced weekly {week_id} to Supabase")
        except Exception as e:
            logger.error(f"Supabase push_weekly failed: {e}")

    def pull_weekly(self, week_id: str) -> Optional[dict]:
        """Pull weekly report from Supabase."""
        if not self.enabled:
            return None
        try:
            res = self.client.table("weekly_reports") \
                .select("data") \
                .eq("week_id", week_id) \
                .maybe_single() \
                .execute()
            if res and res.data:
                return res.data["data"]
        except Exception as e:
            logger.error(f"Supabase pull_weekly failed: {e}")
        return None

    def list_weekly_ids(self) -> list:
        """List all available weekly report IDs from Supabase."""
        if not self.enabled:
            return []
        try:
            res = self.client.table("weekly_reports") \
                .select("week_id") \
                .order("week_id") \
                .execute()
            return [r["week_id"] for r in res.data]
        except Exception as e:
            logger.error(f"Supabase list_weekly failed: {e}")
        return []
