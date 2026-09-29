"""
Configuration for the CostScope FastAPI application.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class APISettings(BaseSettings):
    """Runtime settings for the CostScope API."""

    app_name: str = "CostScope API"
    app_env: str = "development"
    debug: bool = True

    log_level: str = "INFO"
    log_dir: str = "logs"

    database_url: str | None = None

    gold_data_dir: str = "data/gold"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def gold_path(self) -> Path:
        """Return the absolute Gold-layer path."""

        return PROJECT_ROOT / self.gold_data_dir


settings = APISettings()
