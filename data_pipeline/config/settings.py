"""
Central configuration for the CostScope data platform.

Configuration is loaded from environment variables and the local `.env`
file using Pydantic Settings.

Environment variables may override the defaults defined here, allowing
the same application code to run locally, in CI/CD and in production.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root:
#
# CostScope/
# ├── data_pipeline/
# │   └── config/
# │       └── settings.py
# └── ...
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration for CostScope."""

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
    # Database / cloud services
    # ---------------------------------------------------------
    database_url: str | None = None

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # ---------------------------------------------------------
    # Public APIs
    # ---------------------------------------------------------
    postcodes_api_url: str = "https://api.postcodes.io"
    ons_api_base_url: str = "https://api.beta.ons.gov.uk/v1"

    # ---------------------------------------------------------
    # ONS datasets
    #
    # Dataset URLs are given defaults so local development and
    # test collection do not fail simply because an environment
    # variable has not been supplied.
    #
    # Environment variables can still override these values.
    # ---------------------------------------------------------
    ons_private_rent_dataset_url: str = (
        "https://www.ons.gov.uk/file?"
        "uri=%2Feconomy%2Finflationandpriceindices%2Fdatasets%2F"
        "priceindexofprivaterentsukmonthlypricestatistics%2F"
        "16september2026%2F"
        "priceindexofprivaterentsukmonthlypricestatistics.xlsx"
    )

    # ---------------------------------------------------------
    # Data directories
    # ---------------------------------------------------------
    bronze_data_dir: str = "data/bronze"
    silver_data_dir: str = "data/silver"
    gold_data_dir: str = "data/gold"

    # ---------------------------------------------------------
    # Pydantic Settings configuration
    # ---------------------------------------------------------
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
