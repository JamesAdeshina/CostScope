"""
Configuration for the CostScope FastAPI application.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class APISettings(BaseSettings):
    """Runtime configuration for the CostScope API."""

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------
    app_name: str = "CostScope"
    app_env: str = "development"
    debug: bool = True

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------
    log_level: str = "INFO"
    log_dir: str = "logs"

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    database_url: str | None = None

    # ---------------------------------------------------------
    # External services
    # ---------------------------------------------------------
    postcodes_api_url: str = "https://api.postcodes.io"

    # ---------------------------------------------------------
    # Gold data
    # ---------------------------------------------------------
    gold_data_dir: str = "data/gold"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def gold_path(self) -> Path:
        """Return the absolute Gold-layer directory."""

        return PROJECT_ROOT / self.gold_data_dir


settings = APISettings()
