"""
Configuration for the CostScope FastAPI application.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class APISettings(BaseSettings):
    """Configuration used by the CostScope API."""

    app_name: str = "CostScope"
    app_env: str = "development"
    debug: bool = True

    database_url: str | None = None

    postcodes_api_url: str = "https://api.postcodes.io"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


api_settings = APISettings()
