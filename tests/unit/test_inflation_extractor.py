"""
Unit tests for the ONS CPI Bronze extractor.
"""

from pathlib import Path

from data_pipeline.config.sources import (
    ONS_CPI_SERIES,
)
from data_pipeline.extract.ons.inflation import (
    calculate_sha256,
    generate_run_id,
)


def test_cpi_series_configuration() -> None:
    """CostScope should configure the three headline CPI series."""

    assert ONS_CPI_SERIES["annual_rate"]["series_id"] == "D7G7"

    assert ONS_CPI_SERIES["monthly_rate"]["series_id"] == "D7OE"

    assert ONS_CPI_SERIES["index"]["series_id"] == "D7BT"


def test_inflation_run_id_format() -> None:
    """Inflation ingestion should generate a run-prefixed ID."""

    run_id = generate_run_id()

    assert run_id.startswith("run_")

    assert len(run_id) == 19


def test_inflation_sha256(
    tmp_path: Path,
) -> None:
    """Bronze CPI JSON should support deterministic checksums."""

    path = tmp_path / "sample.json"

    path.write_text(
        '{"metric": "CPI_ANNUAL_RATE"}',
        encoding="utf-8",
    )

    first = calculate_sha256(path)

    second = calculate_sha256(path)

    assert first == second
    assert len(first) == 64
