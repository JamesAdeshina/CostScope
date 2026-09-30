"""
Discover the Nomis internal dataset ID and labour-market codes needed
for CostScope unemployment ingestion.

Nomis publishes a human-facing API reference such as APSNEW, but the
REST discovery endpoints use the internal dataset ID, typically NM_*.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from data_pipeline.config.nomis_sources import (
    NOMIS_API_BASE_URL,
)
from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


class NomisResponseError(RuntimeError):
    """Raised when Nomis returns an unexpected response."""


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
    """Request and validate JSON from Nomis."""

    logger.info(
        "Requesting Nomis API: %s",
        url,
    )

    response = requests.get(
        url,
        params=params,
        timeout=60,
        headers={
            "User-Agent": "CostScope/0.4",
            "Accept": "application/json",
        },
    )

    response.raise_for_status()

    try:
        payload = response.json()

    except requests.exceptions.JSONDecodeError as exc:
        raise NomisResponseError(
            "Nomis returned a non-JSON response. "
            f"URL={response.url} | "
            f"content-type={response.headers.get('content-type')} | "
            f"preview={response.text[:400]!r}"
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):
        raise NomisResponseError(
            f"Unexpected Nomis JSON type: {type(payload).__name__}"
        )

    return payload


def write_json(
    payload: dict[str, Any],
    destination: Path,
) -> None:
    """Write one discovery payload."""

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file_handle:
        json.dump(
            payload,
            file_handle,
            indent=2,
            ensure_ascii=False,
        )


def find_aps_dataset_id(
    payload: dict[str, Any],
) -> str:
    """
    Find the internal Nomis dataset ID for Annual Population Survey.
    """

    keyfamilies = (
        payload.get("structure", {}).get("keyfamilies", {}).get("keyfamily", [])
    )

    if isinstance(
        keyfamilies,
        dict,
    ):
        keyfamilies = [keyfamilies]

    matches = []

    for item in keyfamilies:
        if not isinstance(
            item,
            dict,
        ):
            continue

        dataset_id = str(
            item.get(
                "id",
                "",
            )
        )

        name = str(
            item.get(
                "name",
                "",
            )
        )

        description = str(
            item.get(
                "description",
                "",
            )
        )

        text = (f"{dataset_id} {name} {description}").lower()

        if "annual population survey" in text:
            matches.append(dataset_id)

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one Annual Population Survey "
            f"dataset match, found {matches}."
        )

    return matches[0]


def run_unemployment_discovery() -> Path:
    """Discover the Nomis APS dataset and its relevant dimensions."""

    output_directory = settings.bronze_path / "nomis" / "aps" / "discovery"

    dataset_search_url = f"{NOMIS_API_BASE_URL}/dataset/def.sdmx.json"

    dataset_search = get_json(
        dataset_search_url,
        params={
            "search": "*annual population survey*",
        },
    )

    write_json(
        dataset_search,
        output_directory / "dataset_search.json",
    )

    dataset_id = find_aps_dataset_id(dataset_search)

    logger.info(
        "Resolved Annual Population Survey -> %s",
        dataset_id,
    )

    overview = get_json(f"{NOMIS_API_BASE_URL}/dataset/{dataset_id}.overview.json")

    structure = get_json(f"{NOMIS_API_BASE_URL}/dataset/{dataset_id}/def.sdmx.json")

    variables = get_json(
        (f"{NOMIS_API_BASE_URL}/dataset/{dataset_id}/variable.def.sdmx.json"),
        params={
            "search": "*unemploy*",
        },
    )

    geographies = get_json(
        (f"{NOMIS_API_BASE_URL}/dataset/{dataset_id}/geography.def.sdmx.json"),
        params={
            "search": "*Derby*",
        },
    )

    write_json(
        overview,
        output_directory / "aps_overview.json",
    )

    write_json(
        structure,
        output_directory / "aps_structure.json",
    )

    write_json(
        variables,
        output_directory / "unemployment_variables.json",
    )

    write_json(
        geographies,
        output_directory / "derby_geographies.json",
    )

    with (output_directory / "resolved_dataset.json").open(
        "w",
        encoding="utf-8",
    ) as file_handle:
        json.dump(
            {
                "dataset_id": dataset_id,
            },
            file_handle,
            indent=2,
        )

    logger.info(
        "Nomis APS discovery written to %s",
        output_directory,
    )

    return output_directory
