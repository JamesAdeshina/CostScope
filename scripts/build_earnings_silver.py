"""
Build and validate the CostScope ONS ASHE Silver earnings dataset.

Usage
-----

    python -m scripts.build_earnings_silver
"""

from data_pipeline.quality.ons.earnings_quality import (
    validate_earnings_silver,
)
from data_pipeline.transform.ons.earnings import (
    build_silver_earnings,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build and validate the Silver earnings dataset."""

    logger.info("=" * 70)
    logger.info("Building CostScope Silver earnings")
    logger.info("=" * 70)

    dataframe, output_path = build_silver_earnings()

    checks = validate_earnings_silver(dataframe)

    derby = dataframe.loc[dataframe["area_code"] == "E06000015"]

    logger.info("=" * 70)
    logger.info("Silver earnings completed")
    logger.info(
        "Rows: %s",
        f"{len(dataframe):,}",
    )
    logger.info(
        "Critical DQ checks passed: %s",
        sum(check.status == "PASS" for check in checks),
    )
    logger.info(
        "Output: %s",
        output_path,
    )

    if not derby.empty:
        record = derby.iloc[0]

        logger.info(
            "Derby validation: %s | %s | £%s | annual change %s%%",
            record["area_name"],
            record["area_code"],
            (
                f"{record['median_annual_pay']:,.0f}"
                if not record["median_annual_pay"] != record["median_annual_pay"]
                else "missing"
            ),
            (
                f"{record['median_annual_change_percent']:.1f}"
                if not record["median_annual_change_percent"]
                != record["median_annual_change_percent"]
                else "missing"
            ),
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
