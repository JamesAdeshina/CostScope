"""
Utilities for CostScope unemployment data.
"""

from pathlib import Path

from data_pipeline.config.settings import settings


def find_latest_unemployment_file() -> Path:
    """Return the latest unemployment Bronze CSV."""

    root = settings.bronze_path / "nomis" / "unemployment"

    files = list(root.rglob("model_based_unemployment.csv"))

    if not files:
        raise FileNotFoundError(
            "No unemployment Bronze data found. "
            "Run `python -m scripts.extract_unemployment` first."
        )

    return max(
        files,
        key=lambda path: path.stat().st_mtime,
    )
