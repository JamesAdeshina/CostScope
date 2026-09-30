"""
Inspect the latest CostScope ONS CPI Bronze API payloads.

Run with:

    python -m scripts.inspect_inflation
"""

from __future__ import annotations

import json

from data_pipeline.quality.ons.inspect_inflation import (
    describe_payload,
    load_json,
)
from data_pipeline.utils.inflation import (
    find_latest_inflation_run,
)


def main() -> None:
    """Inspect all CPI series downloaded in the latest Bronze run."""

    run_directory = find_latest_inflation_run()

    print()
    print("=" * 100)
    print("LATEST CPI BRONZE RUN")
    print("=" * 100)
    print(run_directory)

    files = sorted(
        path for path in run_directory.glob("*.json") if path.name != "metadata.json"
    )

    for path in files:
        payload = load_json(path)

        description = describe_payload(payload)

        print()
        print("=" * 100)
        print(path.name)
        print("=" * 100)

        print(
            json.dumps(
                description,
                indent=2,
                default=str,
            )
        )

        print()
        print("SELECTED TOP-LEVEL VALUES")
        print("-" * 100)

        for key in (
            "title",
            "description",
            "cdid",
            "datasetId",
            "dataset_id",
            "unit",
            "releaseDate",
            "release_date",
            "nextRelease",
            "next_release",
        ):
            if key in payload:
                print(f"{key}: {payload[key]}")

        # Print the last few entries of list-valued structures so we can
        # identify where ONS stores recent monthly observations.
        print()
        print("RECENT LIST SAMPLES")
        print("-" * 100)

        for (
            key,
            value,
        ) in payload.items():
            if (
                isinstance(
                    value,
                    list,
                )
                and value
            ):
                print()
                print(f"{key}: {len(value)} entries")

                sample = value[-5:]

                print(
                    json.dumps(
                        sample,
                        indent=2,
                        default=str,
                    )
                )


if __name__ == "__main__":
    main()
