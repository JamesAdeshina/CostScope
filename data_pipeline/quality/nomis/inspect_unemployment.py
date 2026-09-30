"""
Inspect Nomis APS discovery documents.

The recursive walker prints objects containing terms relevant to
unemployment or Derby without assuming the exact Nomis JSON layout.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(
    path: Path,
) -> dict[str, Any]:
    """Load a JSON object."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file_handle:
        return json.load(file_handle)


def object_contains(
    value: Any,
    term: str,
) -> bool:
    """Return True when a nested object contains the search term."""

    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
        ).lower()

    except TypeError:
        text = str(value).lower()

    return term.lower() in text


def walk_matches(
    value: Any,
    term: str,
    path: str = "root",
) -> list[tuple[str, Any]]:
    """Recursively collect dictionaries matching a term."""

    matches: list[tuple[str, Any]] = []

    if isinstance(
        value,
        dict,
    ):
        if object_contains(
            value,
            term,
        ):
            # Only show reasonably small objects directly.
            if (
                len(
                    json.dumps(
                        value,
                        default=str,
                    )
                )
                < 2500
            ):
                matches.append(
                    (
                        path,
                        value,
                    )
                )

        for (
            key,
            child,
        ) in value.items():
            matches.extend(
                walk_matches(
                    child,
                    term,
                    f"{path}.{key}",
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for (
            index,
            child,
        ) in enumerate(value):
            matches.extend(
                walk_matches(
                    child,
                    term,
                    f"{path}[{index}]",
                )
            )

    return matches
