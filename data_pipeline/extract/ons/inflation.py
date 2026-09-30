"""
ONS consumer-price inflation Bronze extractor.

The extractor uses the official ONS Beta API to discover the canonical
URI for each MM23 time series before requesting its data.

This avoids hardcoding undocumented data endpoints and makes the
pipeline more resilient to changes in ONS page URLs.

Series
------
D7G7
    CPI annual rate, all items.

D7OE
    CPI monthly rate, all items.

D7BT
    CPI index, all items, 2015=100.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from data_pipeline.config.settings import settings
from data_pipeline.config.sources import (
    ONS_API_BASE_URL,
    ONS_CPI_DATASET_ID,
    ONS_CPI_DATASET_NAME,
    ONS_CPI_PUBLISHER,
    ONS_CPI_RELEASE_DATE,
    ONS_CPI_SERIES,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


DATASET_CODE = "ons_cpi_mm23"


@dataclass
class InflationSeriesMetadata:
    """Metadata for one downloaded ONS CPI time series."""

    series_name: str
    series_id: str
    metric_code: str
    canonical_uri: str
    bronze_filename: str
    sha256: str


@dataclass
class InflationExtractionMetadata:
    """Metadata describing one complete CPI Bronze ingestion."""

    run_id: str
    dataset_code: str
    dataset_id: str
    dataset_name: str
    publisher: str
    release_date: str
    started_at: str
    completed_at: str
    status: str
    series: list[InflationSeriesMetadata]


def generate_run_id() -> str:
    """Create a UTC run identifier."""

    return datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S")


def calculate_sha256(
    file_path: Path,
) -> str:
    """Calculate SHA-256 for a Bronze file."""

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
def get_json(
    url: str,
    *,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Request JSON from the ONS API with retries."""

    logger.info(
        "Requesting ONS API: %s",
        url,
    )

    response = requests.get(
        url,
        params=params,
        timeout=60,
        headers={
            "User-Agent": "CostScope/0.3",
            "Accept": "application/json",
        },
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError("ONS API returned an unexpected non-object JSON response.")

    return payload


def discover_series_uri(
    series_id: str,
) -> str:
    """
    Discover the canonical ONS content URI for a time series.

    ONS recommends searching by CDID and then using the returned URI
    with its data endpoint.
    """

    search_url = f"{ONS_API_BASE_URL}/search"

    payload = get_json(
        search_url,
        params={
            "content_type": "timeseries",
            "cdids": series_id.upper(),
        },
    )

    items = payload.get("items", [])

    matches = []

    for item in items:
        cdid = str(
            item.get(
                "cdid",
                "",
            )
        ).upper()

        dataset_id = str(
            item.get(
                "dataset_id",
                "",
            )
        ).upper()

        if cdid == series_id.upper() and dataset_id == ONS_CPI_DATASET_ID:
            matches.append(item)

    # Some ONS search responses may omit dataset_id even when the
    # returned time-series URI identifies the correct MM23 series.
    if not matches:
        for item in items:
            cdid = str(
                item.get(
                    "cdid",
                    "",
                )
            ).upper()

            uri = str(
                item.get(
                    "uri",
                    "",
                )
            ).lower()

            if cdid == series_id.upper() and "mm23" in uri:
                matches.append(item)

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one ONS MM23 search result "
            f"for series {series_id}, "
            f"but found {len(matches)}."
        )

    uri = matches[0].get("uri")

    if not uri:
        raise ValueError(
            f"ONS search result did not contain a URI for series {series_id}."
        )

    logger.info(
        "Resolved %s -> %s",
        series_id,
        uri,
    )

    return str(uri)


def fetch_series_data(
    canonical_uri: str,
) -> dict[str, Any]:
    """Fetch full time-series data through the ONS data endpoint."""

    data_url = f"{ONS_API_BASE_URL}/data"

    return get_json(
        data_url,
        params={
            "uri": canonical_uri,
        },
    )


def write_json(
    payload: dict[str, Any],
    destination: Path,
) -> None:
    """Write JSON deterministically to Bronze storage."""

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = destination.with_suffix(destination.suffix + ".part")

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as file_handle:
        json.dump(
            payload,
            file_handle,
            indent=2,
            ensure_ascii=False,
        )

    temporary_path.replace(destination)


def extract_inflation() -> tuple[
    Path,
    Path,
]:
    """
    Download the configured CPI time series into Bronze.

    Returns
    -------
    tuple[Path, Path]
        Bronze run directory and metadata path.
    """

    started_at = datetime.now(UTC)

    run_id = generate_run_id()

    ingestion_date = started_at.strftime("%Y-%m-%d")

    bronze_directory = (
        settings.bronze_path
        / "ons"
        / "inflation"
        / (f"ingestion_date={ingestion_date}")
        / run_id
    )

    bronze_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_path = bronze_directory / "metadata.json"

    logger.info("=" * 70)
    logger.info("ONS CPI inflation extraction started")
    logger.info(
        "Run ID: %s",
        run_id,
    )
    logger.info("=" * 70)

    downloaded_series: list[InflationSeriesMetadata] = []

    for (
        series_name,
        definition,
    ) in ONS_CPI_SERIES.items():
        series_id = str(definition["series_id"])

        metric_code = str(definition["metric_code"])

        logger.info(
            "Processing %s (%s)",
            metric_code,
            series_id,
        )

        canonical_uri = discover_series_uri(series_id)

        payload = fetch_series_data(canonical_uri)

        filename = f"{series_name}_{series_id.lower()}.json"

        destination = bronze_directory / filename

        write_json(
            payload,
            destination,
        )

        checksum = calculate_sha256(destination)

        downloaded_series.append(
            InflationSeriesMetadata(
                series_name=series_name,
                series_id=series_id,
                metric_code=metric_code,
                canonical_uri=canonical_uri,
                bronze_filename=filename,
                sha256=checksum,
            )
        )

        logger.info(
            "Bronze CPI series written: %s",
            destination,
        )

    completed_at = datetime.now(UTC)

    metadata = InflationExtractionMetadata(
        run_id=run_id,
        dataset_code=DATASET_CODE,
        dataset_id=ONS_CPI_DATASET_ID,
        dataset_name=ONS_CPI_DATASET_NAME,
        publisher=ONS_CPI_PUBLISHER,
        release_date=ONS_CPI_RELEASE_DATE,
        started_at=(started_at.isoformat()),
        completed_at=(completed_at.isoformat()),
        status="SUCCESS",
        series=downloaded_series,
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
        "Inflation metadata written: %s",
        metadata_path,
    )

    logger.info("ONS CPI inflation extraction completed successfully")

    return (
        bronze_directory,
        metadata_path,
    )
