import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    # LLM Keys
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    hf_api_token: str = os.getenv("HF_API_TOKEN", "")

    # Data Source Keys
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    devto_api_key: str = os.getenv("DEVTO_API_KEY", "")  # optional

    # Schedule
    daily_cron_hour: int = int(os.getenv("DAILY_CRON_HOUR", "7"))
    daily_cron_minute: int = int(os.getenv("DAILY_CRON_MINUTE", "0"))
    weekly_report_day: str = os.getenv("WEEKLY_REPORT_DAY", "sun")

    # Paths
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))

    # LLM Models
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-flash-latest"

    # Categories we track
    categories: list = [
        "ai_models",
        "frameworks",
        "tools",
        "courses",
        "skills",
        "opportunities"
    ]

    @property
    def daily_dir(self) -> Path:
        path = self.data_dir / "daily"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def weekly_dir(self) -> Path:
        path = self.data_dir / "weekly"
        path.mkdir(parents=True, exist_ok=True)
        return path

settings = Settings()