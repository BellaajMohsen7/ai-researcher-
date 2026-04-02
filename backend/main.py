import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings
from agents.crew_setup import AIDailyNewsCrew
from reports.weekly_report import weekly_reporter
from storage.json_store import store

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("ai-news")

# Scheduler
scheduler = AsyncIOScheduler()


# === Scheduled Jobs ===

async def daily_news_job():
    """Runs every day at 7:00 AM."""
    logger.info("=== DAILY NEWS COLLECTION STARTED ===")
    try:
        crew = AIDailyNewsCrew()
        result = await crew.run()
        total = result.get("stats", {}).get("total_items", 0)
        logger.info(f"=== DAILY COMPLETE: {total} items collected ===")
    except Exception as e:
        logger.error(f"=== DAILY JOB FAILED: {e} ===")


async def weekly_report_job():
    """Runs every Sunday at 8:00 AM."""
    logger.info("=== WEEKLY REPORT GENERATION STARTED ===")
    try:
        report = await weekly_reporter.generate()
        logger.info("=== WEEKLY REPORT COMPLETE ===")
    except Exception as e:
        logger.error(f"=== WEEKLY REPORT FAILED: {e} ===")


# === App Lifespan ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI News Aggregator...")

    # Schedule daily job at 7:00 AM
    scheduler.add_job(
        daily_news_job,
        CronTrigger(hour=settings.daily_cron_hour, minute=settings.daily_cron_minute),
        id="daily_news",
        name="Daily AI News Collection",
    )

    # Schedule weekly report on Sunday at 8:00 AM
    scheduler.add_job(
        weekly_report_job,
        CronTrigger(day_of_week="sun", hour=8, minute=0),
        id="weekly_report",
        name="Weekly Report Generation",
    )

    scheduler.start()
    logger.info(
        f"Scheduler started. Daily at {settings.daily_cron_hour}:{settings.daily_cron_minute:02d}, "
        f"Weekly on Sunday 08:00"
    )

    yield  # App runs here

    scheduler.shutdown()
    logger.info("Scheduler stopped.")


# === FastAPI App ===

app = FastAPI(
    title="AI News Aggregator API",
    description="Automated daily AI news collection and weekly intelligence reports.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === API ENDPOINTS ===

@app.get("/")
async def root():
    return {
        "name": "AI News Aggregator API",
        "version": "1.0.0",
        "endpoints": {
            "today": "/api/news/today",
            "by_date": "/api/news/{date}",
            "category": "/api/news/category/{category}",
            "weekly": "/api/reports/weekly/latest",
            "trigger": "/api/trigger/daily",
        }
    }


@app.get("/api/news/today")
async def get_today_news():
    """Get today's collected AI news."""
    today = datetime.now().strftime("%Y-%m-%d")
    data = store.load_daily(today)
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No data collected yet today. Wait for 7 AM or trigger manually."
        )
    return data


@app.get("/api/news/{date}")
async def get_news_by_date(date: str):
    """Get AI news for a specific date (YYYY-MM-DD)."""
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD.")

    data = store.load_daily(date)
    if not data:
        raise HTTPException(404, f"No data found for {date}.")
    return data


@app.get("/api/news/category/{category}")
async def get_category_news(category: str, days: int = Query(default=7, ge=1, le=30)):
    """Get news for a specific category over N days."""
    if category not in settings.categories:
        raise HTTPException(400, f"Invalid category. Choose from: {settings.categories}")

    daily_data = store.load_last_7_days()
    items = []
    for day in daily_data:
        for item in day.get(category, []):
            item["_date"] = day["date"]
            items.append(item)

    return {"category": category, "days": days, "count": len(items), "items": items}


@app.get("/api/news/search")
async def search_news(q: str = Query(..., min_length=2)):
    """Search across all collected news."""
    daily_data = store.load_last_7_days()
    results = []
    q_lower = q.lower()

    for day in daily_data:
        for cat in settings.categories:
            for item in day.get(cat, []):
                text = f"{item.get('name', '')} {item.get('description', '')}".lower()
                if q_lower in text:
                    item["_date"] = day["date"]
                    item["_category"] = cat
                    results.append(item)

    return {"query": q, "count": len(results), "results": results}


@app.get("/api/reports/weekly/latest")
async def get_latest_weekly_report():
    """Get the most recent weekly report."""
    reports = store.list_weekly_reports()
    if not reports:
        raise HTTPException(404, "No weekly reports generated yet.")
    report = store.load_weekly_report(reports[-1])
    return report


@app.get("/api/reports/weekly/{week_id}")
async def get_weekly_report(week_id: str):
    """Get a specific weekly report (e.g., 2025-W04)."""
    report = store.load_weekly_report(week_id)
    if not report:
        raise HTTPException(404, f"No report found for {week_id}.")
    return report


@app.get("/api/reports/weekly")
async def list_weekly_reports():
    """List all available weekly reports."""
    reports = store.list_weekly_reports()
    return {"reports": reports, "count": len(reports)}


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics."""
    daily_files = store.list_daily_files()
    weekly_files = store.list_weekly_reports()

    latest = None
    if daily_files:
        latest = store.load_daily(daily_files[-1])

    return {
        "total_daily_collections": len(daily_files),
        "total_weekly_reports": len(weekly_files),
        "latest_collection": daily_files[-1] if daily_files else None,
        "latest_stats": latest.get("stats") if latest else None,
        "available_dates": daily_files[-7:],
    }


# === MANUAL TRIGGERS ===

@app.post("/api/trigger/daily")
async def trigger_daily_collection():
    """Manually trigger daily news collection."""
    logger.info("Manual daily trigger requested")
    asyncio.create_task(daily_news_job())
    return {
        "status": "started",
        "message": "Daily collection triggered. Check /api/news/today in a few minutes.",
    }


@app.post("/api/trigger/weekly")
async def trigger_weekly_report():
    """Manually trigger weekly report generation."""
    logger.info("Manual weekly trigger requested")
    asyncio.create_task(weekly_report_job())
    return {"status": "started", "message": "Weekly report generation triggered."}


@app.get("/api/scheduler/status")
async def scheduler_status():
    """Check scheduled jobs status."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({"id": job.id, "name": job.name, "next_run": str(job.next_run_time)})
    return {"jobs": jobs}


# === Run ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)