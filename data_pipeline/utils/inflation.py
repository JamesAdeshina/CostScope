"""
Utilities for locating CostScope ONS CPI Bronze data.
"""

from pathlib import Path

from data_pipeline.config.settings import settings


def find_latest_inflation_run() -> Path:
    """Return the latest successful-looking CPI Bronze run directory."""

    root = settings.bronze_path / "ons" / "inflation"

    metadata_files = list(root.rglob("metadata.json"))

    if not metadata_files:
        raise FileNotFoundError(
            "No CPI Bronze ingestion found. "
            "Run `python -m scripts.extract_inflation` first."
        )

    latest_metadata = max(
        metadata_files,
        key=lambda path: path.stat().st_mtime,
    )

    return latest_metadata.parent
