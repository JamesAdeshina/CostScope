"""
Discover the live Nomis Annual Population Survey structure.

Usage
-----

    python -m scripts.discover_unemployment
"""

from __future__ import annotations

import json

from data_pipeline.extract.nomis.unemployment_discovery import (
    run_unemployment_discovery,
)
from data_pipeline.quality.nomis.inspect_unemployment import (
    load_json,
    walk_matches,
)


def print_matches(
    title: str,
    payload,
    term: str,
    limit: int = 30,
) -> None:
    """Print unique nested objects containing a search term."""

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)

    matches = walk_matches(
        payload,
        term,
    )

    if not matches:
        print(f"No matches found for: {term}")
        return

    seen: set[str] = set()

    shown = 0

    for (
        path,
        value,
    ) in matches:
        rendered = json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

        if rendered in seen:
            continue

        seen.add(rendered)

        print()
        print(f"PATH: {path}")

        print(rendered)

        shown += 1

        if shown >= limit:
            print(f"... limited to {limit} unique matches ...")
            break


def main() -> None:
    """Run APS discovery and print relevant codes."""

    output_directory = run_unemployment_discovery()

    resolved = load_json(output_directory / "resolved_dataset.json")

    variables = load_json(output_directory / "unemployment_variables.json")

    geographies = load_json(output_directory / "derby_geographies.json")

    structure = load_json(output_directory / "aps_structure.json")

    print()
    print("=" * 100)
    print("RESOLVED NOMIS DATASET")
    print("=" * 100)
    print(resolved)

    print_matches(
        "APS STRUCTURE - VARIABLE",
        structure,
        "variable",
    )

    print_matches(
        "APS STRUCTURE - MEASURE",
        structure,
        "measure",
    )

    print_matches(
        "UNEMPLOYMENT VARIABLE MATCHES",
        variables,
        "unemploy",
    )

    print_matches(
        "DERBY GEOGRAPHY MATCHES",
        geographies,
        "derby",
    )

    print()
    print("=" * 100)
    print("DISCOVERY DIRECTORY")
    print("=" * 100)
    print(output_directory)


if __name__ == "__main__":
    main()
