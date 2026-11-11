"""Reads settings from environment variables (and from the .env file locally)."""
import os

from dotenv import load_dotenv

load_dotenv()  # loads values from .env if the file exists


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")


settings = Settings()
