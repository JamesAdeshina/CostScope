"""
Application configuration for the CostScope data pipeline.

Configuration values are read from environment variables and the local
.env file using Pydantic Settings.

Keeping configuration outside the business logic makes the pipeline
portable between local development, GitHub Actions and production.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the repository root from this file:
#
# CostScope/
#   data_pipeline/
#       config/
#           settings.py
#
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration for the CostScope project."""

    app_name: str = "CostScope"
    app_env: str = "development"
    debug: bool = True

    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"

    # External services
    database_url: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # Public APIs
    postcodes_api_url: str = "https://api.postcodes.io"
    ons_api_base_url: str = "https://api.beta.ons.gov.uk/v1"

    # Data directories
    bronze_data_dir: str = "data/bronze"
    silver_data_dir: str = "data/silver"
    gold_data_dir: str = "data/gold"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def bronze_path(self) -> Path:
        """Return the absolute Bronze data directory."""

        return PROJECT_ROOT / self.bronze_data_dir

    @property
    def silver_path(self) -> Path:
        """Return the absolute Silver data directory."""

        return PROJECT_ROOT / self.silver_data_dir

    @property
    def gold_path(self) -> Path:
        """Return the absolute Gold data directory."""

        return PROJECT_ROOT / self.gold_data_dir

    @property
    def logs_path(self) -> Path:
        """Return the absolute application log directory."""

        return PROJECT_ROOT / self.log_dir


settings = Settings()
