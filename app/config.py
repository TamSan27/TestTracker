"""Reads settings from environment variables (and from the .env file locally)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # loads values from .env if the file exists

BASE_DIR = Path(__file__).resolve().parent.parent


def _flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    allow_private_urls: bool = _flag("ALLOW_PRIVATE_URLS")
    run_timeout: int = int(os.getenv("RUN_TIMEOUT_SECONDS", "180"))
    max_html_bytes: int = 2 * 1024 * 1024
    database_path: Path = BASE_DIR / os.getenv("DATABASE_PATH", "tracker.db")
    reports_dir: Path = BASE_DIR / os.getenv("REPORTS_DIR", "reports")


settings = Settings()
