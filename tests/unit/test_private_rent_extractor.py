"""
Unit tests for ONS private rent extraction utilities.
"""

from pathlib import Path

from data_pipeline.extract.ons.private_rent import (
    calculate_sha256,
    generate_run_id,
)


def test_generate_run_id_format() -> None:
    """Run IDs should follow the CostScope naming convention."""

    run_id = generate_run_id()

    assert run_id.startswith("run_")

    assert len(run_id) == len("run_YYYYMMDD_HHMMSS")


def test_calculate_sha256(
    tmp_path: Path,
) -> None:
    """Checksum utility should return a SHA-256 hash."""

    test_file = tmp_path / "sample.txt"

    test_file.write_text(
        "CostScope",
        encoding="utf-8",
    )

    result = calculate_sha256(test_file)

    assert len(result) == 64

    assert all(character in "0123456789abcdef" for character in result)
