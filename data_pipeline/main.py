"""
Main CostScope data pipeline orchestrator.

Current pipeline:

    ONS Private Rent
        ↓
    Download
        ↓
    Bronze storage
        ↓
    Metadata
        ↓
    Workbook inspection

Future stages will add:

    Validation
        ↓
    Silver transformation
        ↓
    Gold dimensional model
        ↓
    PostgreSQL
"""

from __future__ import annotations

import sys

from data_pipeline.config.settings import settings
from data_pipeline.extract.ons.private_rent import (
    extract_private_rent,
)
from data_pipeline.quality.ons.inspect_private_rent import (
    inspect_workbook,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def initialise_directories() -> None:
    """Ensure runtime directories exist."""

    directories = [
        settings.bronze_path,
        settings.silver_path,
        settings.gold_path,
        settings.logs_path,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


def run_pipeline() -> None:
    """Run the current CostScope data pipeline."""

    logger.info("=" * 70)
    logger.info("CostScope data pipeline started")
    logger.info("=" * 70)

    logger.info(
        "Environment: %s",
        settings.app_env,
    )

    initialise_directories()

    # ---------------------------------------------------------
    # ONS Private Rent
    # ---------------------------------------------------------

    workbook_path, metadata_path = extract_private_rent()

    logger.info(
        "Bronze workbook: %s",
        workbook_path,
    )

    logger.info(
        "Extraction metadata: %s",
        metadata_path,
    )

    workbook_structure = inspect_workbook(workbook_path)

    logger.info(
        "Workbook inspection complete: %s worksheets detected",
        len(workbook_structure),
    )

    logger.info("=" * 70)
    logger.info("CostScope pipeline completed successfully")
    logger.info("=" * 70)


def main() -> int:
    """CLI entry point."""

    try:
        run_pipeline()

        return 0

    except Exception:
        logger.exception("CostScope pipeline failed")

        return 1


if __name__ == "__main__":
    sys.exit(main())
