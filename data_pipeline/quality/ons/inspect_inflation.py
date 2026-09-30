"""
Inspection helpers for ONS CPI API payloads.

The goal is to inspect the actual API structure before CostScope commits
to a Silver transformation contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(
    path: Path,
) -> dict[str, Any]:
    """Load one Bronze JSON payload."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file_handle:
        payload = json.load(file_handle)

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(f"Expected JSON object in {path}")

    return payload


def describe_payload(
    payload: dict[str, Any],
) -> dict[str, object]:
    """
    Describe top-level CPI payload structure without assuming schema.
    """

    description: dict[str, object] = {
        "top_level_keys": sorted(payload.keys()),
    }

    for (
        key,
        value,
    ) in payload.items():
        if isinstance(
            value,
            list,
        ):
            description[f"{key}_length"] = len(value)

            if value:
                first = value[0]

                description[f"{key}_first_type"] = type(first).__name__

                if isinstance(
                    first,
                    dict,
                ):
                    description[f"{key}_first_keys"] = sorted(first.keys())

        elif isinstance(
            value,
            dict,
        ):
            description[f"{key}_keys"] = sorted(value.keys())

    return description
