"""One-time script to seed existing JSON data into Supabase."""
import json
import os
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from storage.supabase_sync import SupabaseSync

def seed():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        print("ERROR: Set SUPABASE_URL and SUPABASE_KEY in .env")
        return

    sb = SupabaseSync(url, key)
    if not sb.enabled:
        print("ERROR: Could not connect to Supabase")
        return

    data_dir = Path(__file__).parent.parent / "data"

    # Seed daily collections
    daily_dir = data_dir / "daily"
    if daily_dir.exists():
        for f in sorted(daily_dir.glob("*.json")):
            date_str = f.stem
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            sb.push_daily(date_str, data)
            print(f"  [OK] Daily {date_str}")

    # Seed weekly reports
    weekly_dir = data_dir / "weekly"
    if weekly_dir.exists():
        for f in sorted(weekly_dir.glob("week-*.json")):
            week_id = f.stem.replace("week-", "")
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            sb.push_weekly(week_id, data)
            print(f"  [OK] Weekly {week_id}")

    print("\nDone! All data seeded to Supabase.")

if __name__ == "__main__":
    seed()
