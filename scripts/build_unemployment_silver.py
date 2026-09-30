"""
Build and validate CostScope unemployment Silver.
"""

from data_pipeline.quality.nomis.unemployment_quality import (
    validate_unemployment_silver,
)
from data_pipeline.transform.nomis.unemployment import (
    load_raw_unemployment,
    standardise_unemployment,
    write_silver_unemployment,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build unemployment Silver."""

    logger.info("=" * 70)
    logger.info("Building CostScope Silver unemployment")
    logger.info("=" * 70)

    raw = load_raw_unemployment()

    silver = standardise_unemployment(raw)

    validate_unemployment_silver(silver)

    output = write_silver_unemployment(silver)

    derby = silver.loc[silver["location_id"] == "E06000015"]

    logger.info("=" * 70)
    logger.info("Silver unemployment completed")
    logger.info(
        "Rows: %s",
        f"{len(silver):,}",
    )
    logger.info(
        "Output: %s",
        output,
    )

    if not derby.empty:
        row = derby.iloc[0]

        logger.info(
            "Derby validation: %s | %s | %.1f%% | %s",
            row["location_name"],
            row["location_id"],
            row["unemployment_rate"],
            row["reference_period_label"],
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
