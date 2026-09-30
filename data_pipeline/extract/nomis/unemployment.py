"""
Bronze extractor for Nomis model-based unemployment estimates.

Dataset
-------
NM_127_1
    model-based estimates of unemployment

The extractor intentionally requests Nomis' canonical dimension fields:
GEOGRAPHY, GEOGRAPHY_NAME, ITEM, ITEM_NAME, TIME, TIME_NAME and
OBS_VALUE.

We do not depend on GEOGRAPHY_CODE being populated in CSV output.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from data_pipeline.config.nomis_sources import (
    NOMIS_API_BASE_URL,
    NOMIS_UNEMPLOYMENT_DATASET_ID,
    NOMIS_UNEMPLOYMENT_DATASET_NAME,
    NOMIS_UNEMPLOYMENT_PUBLISHER,
    NOMIS_VALUE_MEASURE,
)
from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class UnemploymentExtractionMetadata:
    """Metadata for one unemployment Bronze ingestion."""

    run_id: str
    dataset_id: str
    dataset_name: str
    publisher: str
    source_url: str
    started_at: str
    completed_at: str
    status: str
    filename: str
    size_bytes: int
    sha256: str


def generate_run_id() -> str:
    """Create UTC run identifier."""

    return datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S")


def calculate_sha256(
    file_path: Path,
) -> str:
    """Calculate SHA-256."""

    digest = hashlib.sha256()

    with file_path.open("rb") as file_handle:
        for chunk in iter(
            lambda: file_handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=2,
        min=2,
        max=10,
    ),
    reraise=True,
)
def request_unemployment_csv() -> requests.Response:
    """Request latest model-based unemployment observations."""

    url = f"{NOMIS_API_BASE_URL}/dataset/{NOMIS_UNEMPLOYMENT_DATASET_ID}.data.csv"

    params = {
        "time": "latest",
        "measures": NOMIS_VALUE_MEASURE,
        "select": (
            "GEOGRAPHY,"
            "GEOGRAPHY_NAME,"
            "ITEM,"
            "ITEM_NAME,"
            "TIME,"
            "TIME_NAME,"
            "OBS_VALUE,"
            "OBS_STATUS,"
            "OBS_CONF"
        ),
    }

    logger.info("Requesting Nomis model-based unemployment")

    response = requests.get(
        url,
        params=params,
        timeout=90,
        headers={
            "User-Agent": "CostScope/0.5",
            "Accept": "text/csv",
        },
    )

    response.raise_for_status()

    if not response.content:
        raise ValueError("Nomis returned an empty unemployment response.")

    content_type = response.headers.get(
        "content-type",
        "",
    ).lower()

    if "html" in content_type or response.text.lstrip().lower().startswith(
        "<!doctype html"
    ):
        raise ValueError("Nomis returned HTML instead of unemployment CSV.")

    return response


def extract_unemployment() -> tuple[
    Path,
    Path,
]:
    """Download latest unemployment data into Bronze."""

    started_at = datetime.now(UTC)

    run_id = generate_run_id()

    ingestion_date = started_at.strftime("%Y-%m-%d")

    run_directory = (
        settings.bronze_path
        / "nomis"
        / "unemployment"
        / f"ingestion_date={ingestion_date}"
        / run_id
    )

    run_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = run_directory / "model_based_unemployment.csv"

    metadata_path = run_directory / "metadata.json"

    logger.info("=" * 70)
    logger.info("Nomis unemployment extraction started")
    logger.info(
        "Run ID: %s",
        run_id,
    )
    logger.info("=" * 70)

    response = request_unemployment_csv()

    temporary = destination.with_suffix(".csv.part")

    temporary.write_bytes(response.content)

    temporary.replace(destination)

    checksum = calculate_sha256(destination)

    completed_at = datetime.now(UTC)

    metadata = UnemploymentExtractionMetadata(
        run_id=run_id,
        dataset_id=(NOMIS_UNEMPLOYMENT_DATASET_ID),
        dataset_name=(NOMIS_UNEMPLOYMENT_DATASET_NAME),
        publisher=(NOMIS_UNEMPLOYMENT_PUBLISHER),
        source_url=response.url,
        started_at=(started_at.isoformat()),
        completed_at=(completed_at.isoformat()),
        status="SUCCESS",
        filename=destination.name,
        size_bytes=(destination.stat().st_size),
        sha256=checksum,
    )

    with metadata_path.open(
        "w",
        encoding="utf-8",
    ) as file_handle:
        json.dump(
            asdict(metadata),
            file_handle,
            indent=2,
        )

    logger.info(
        "Nomis unemployment Bronze written: %s",
        destination,
    )

    logger.info(
        "Bronze size: %s bytes",
        f"{destination.stat().st_size:,}",
    )

    logger.info(
        "SHA-256: %s",
        checksum,
    )

    return (
        destination,
        metadata_path,
    )
