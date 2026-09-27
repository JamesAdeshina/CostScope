"""
CostScope data pipeline entry point.

The pipeline will eventually orchestrate:

    Extract
        ↓
    Bronze
        ↓
    Validate
        ↓
    Transform
        ↓
    Silver
        ↓
    Model
        ↓
    Gold
        ↓
    PostgreSQL

At this stage the module verifies that the project configuration,
directories and logging infrastructure are working correctly.
"""

from __future__ import annotations

import sys

from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def initialise_directories() -> None:
    """
    Ensure required runtime directories exist.

    Git tracks the base directories using .gitkeep files, but this
    function makes pipeline execution resilient if a directory is removed
    locally or when the project runs in CI.
    """

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

        logger.debug(
            "Verified directory: %s",
            directory,
        )


def run_pipeline() -> None:
    """Run the CostScope pipeline."""

    logger.info("=" * 70)
    logger.info("CostScope data pipeline started")
    logger.info("=" * 70)

    logger.info(
        "Environment: %s",
        settings.app_env,
    )

    initialise_directories()

    # Dataset pipelines will be introduced incrementally.
    #
    # The first implementation will be:
    #
    # ONS Private Rent
    #     ↓
    # Bronze
    #     ↓
    # Validation
    #     ↓
    # Silver
    #     ↓
    # Gold
    #
    # Keeping this entry point small allows individual dataset pipelines
    # to remain independently testable.

    logger.info("Pipeline infrastructure initialised successfully.")

    logger.info("=" * 70)
    logger.info("CostScope pipeline completed successfully")
    logger.info("=" * 70)


def main() -> int:
    """
    CLI entry point.

    Returns
    -------
    int
        Operating-system exit code.

        0 = success
        1 = failure
    """

    try:
        run_pipeline()

        return 0

    except Exception:
        logger.exception("CostScope pipeline failed with an unhandled exception.")

        return 1


if __name__ == "__main__":
    sys.exit(main())
