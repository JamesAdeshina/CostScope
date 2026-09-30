"""
Tests for Nomis unemployment discovery.
"""

from data_pipeline.extract.nomis.unemployment_discovery import (
    find_aps_dataset_id,
)
from data_pipeline.quality.nomis.inspect_unemployment import (
    object_contains,
    walk_matches,
)


def test_object_contains_finds_nested_term() -> None:
    """Nested Nomis metadata should be searchable."""

    value = {
        "children": [
            {
                "label": "Unemployment rate",
            }
        ]
    }

    assert object_contains(
        value,
        "unemployment",
    )


def test_walk_matches_finds_derby() -> None:
    """Recursive discovery should find Derby metadata."""

    value = {
        "items": [
            {
                "name": "Derby",
                "code": "example",
            }
        ]
    }

    matches = walk_matches(
        value,
        "derby",
    )

    assert matches


def test_find_aps_dataset_id() -> None:
    """Internal Nomis dataset ID should be extracted from SDMX."""

    payload = {
        "structure": {
            "keyfamilies": {
                "keyfamily": [
                    {
                        "id": "NM_TEST",
                        "name": ("annual population survey"),
                        "description": ("Residence based labour market survey"),
                    }
                ]
            }
        }
    }

    assert find_aps_dataset_id(payload) == "NM_TEST"
