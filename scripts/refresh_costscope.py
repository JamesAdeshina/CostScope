"""
Run the complete CostScope data refresh pipeline.

This script is the single orchestration entry point for refreshing
CostScope from source extraction through PostgreSQL validation.

Current pipeline
----------------
Private rent:
    extract -> Silver -> Gold

Earnings:
    extract -> Silver -> Gold

Inflation:
    extract -> Silver -> Gold

Unemployment:
    extract -> Silver -> Gold

Finally:
    Gold -> PostgreSQL
    PostgreSQL validation

Usage
-----
Run everything:

    python -m scripts.refresh_costscope

Run without loading PostgreSQL:

    python -m scripts.refresh_costscope --skip-database

Run one domain only:

    python -m scripts.refresh_costscope --only inflation

Available domains:
    private_rent
    earnings
    inflation
    unemployment
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class PipelineStep:
    """One executable CostScope pipeline step."""

    name: str
    module: str


@dataclass(frozen=True)
class DomainPipeline:
    """Pipeline stages belonging to one CostScope domain."""

    name: str
    steps: tuple[PipelineStep, ...]


PIPELINES = {
    "private_rent": DomainPipeline(
        name="Private rent",
        steps=(
            PipelineStep(
                name="Extract private rent",
                module="scripts.extract_private_rent",
            ),
            PipelineStep(
                name="Build private rent Silver",
                module="scripts.build_private_rent_silver",
            ),
            PipelineStep(
                name="Build private rent Gold",
                module="scripts.build_private_rent_gold",
            ),
        ),
    ),
    "earnings": DomainPipeline(
        name="Earnings",
        steps=(
            PipelineStep(
                name="Extract earnings",
                module="scripts.extract_earnings",
            ),
            PipelineStep(
                name="Build earnings Silver",
                module="scripts.build_earnings_silver",
            ),
            PipelineStep(
                name="Build earnings Gold",
                module="scripts.build_earnings_gold",
            ),
        ),
    ),
    "inflation": DomainPipeline(
        name="Inflation",
        steps=(
            PipelineStep(
                name="Extract inflation",
                module="scripts.extract_inflation",
            ),
            PipelineStep(
                name="Build inflation Silver",
                module="scripts.build_inflation_silver",
            ),
            PipelineStep(
                name="Build inflation Gold",
                module="scripts.build_inflation_gold",
            ),
        ),
    ),
    "unemployment": DomainPipeline(
        name="Unemployment",
        steps=(
            PipelineStep(
                name="Extract unemployment",
                module="scripts.extract_unemployment",
            ),
            PipelineStep(
                name="Build unemployment Silver",
                module="scripts.build_unemployment_silver",
            ),
            PipelineStep(
                name="Build unemployment Gold",
                module="scripts.build_unemployment_gold",
            ),
        ),
    ),
}


DATABASE_STEPS = (
    PipelineStep(
        name="Load Gold warehouse into PostgreSQL",
        module="scripts.load_gold_to_postgres",
    ),
    PipelineStep(
        name="Validate PostgreSQL warehouse",
        module="scripts.check_postgres",
    ),
)


def print_banner(
    title: str,
) -> None:
    """Print a clearly separated terminal section."""

    width = 72

    print()
    print("=" * width)
    print(title)
    print("=" * width)


def run_step(
    step: PipelineStep,
) -> float:
    """
    Execute one pipeline module.

    Returns
    -------
    float
        Execution duration in seconds.

    Raises
    ------
    subprocess.CalledProcessError
        When the pipeline step exits unsuccessfully.
    """

    print()
    print(f"→ {step.name}")
    print(f"  python -m {step.module}")

    started = time.perf_counter()

    subprocess.run(
        [
            sys.executable,
            "-m",
            step.module,
        ],
        check=True,
    )

    duration = time.perf_counter() - started

    print(f"✓ {step.name} ({duration:.2f}s)")

    return duration


def run_domain(
    pipeline: DomainPipeline,
) -> float:
    """Run every stage belonging to one domain."""

    print_banner(pipeline.name)

    total_duration = 0.0

    for step in pipeline.steps:
        total_duration += run_step(step)

    print()
    print(f"✓ {pipeline.name} pipeline complete ({total_duration:.2f}s)")

    return total_duration


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=("Refresh the complete CostScope data platform.")
    )

    parser.add_argument(
        "--only",
        choices=tuple(PIPELINES.keys()),
        help=(
            "Run one source domain only. "
            "Database loading still runs unless "
            "--skip-database is supplied."
        ),
    )

    parser.add_argument(
        "--skip-database",
        action="store_true",
        help=("Do not reload or validate PostgreSQL."),
    )

    return parser.parse_args()


def main() -> None:
    """Run CostScope refresh orchestration."""

    args = parse_arguments()

    started_at = datetime.now(UTC)

    overall_started = time.perf_counter()

    print_banner("CostScope data refresh")

    print(
        "Started:",
        started_at.isoformat(),
    )

    if args.only:
        selected = {args.only: PIPELINES[args.only]}
    else:
        selected = PIPELINES

    print(
        "Domains:",
        ", ".join(selected.keys()),
    )

    print(
        "PostgreSQL refresh:",
        ("disabled" if args.skip_database else "enabled"),
    )

    try:
        for pipeline in selected.values():
            run_domain(pipeline)

        if not args.skip_database:
            print_banner("PostgreSQL serving warehouse")

            for step in DATABASE_STEPS:
                run_step(step)

    except subprocess.CalledProcessError as exc:
        duration = time.perf_counter() - overall_started

        print_banner("CostScope refresh FAILED")

        print(
            "Failed command:",
            " ".join(str(part) for part in exc.cmd),
        )

        print(
            "Exit code:",
            exc.returncode,
        )

        print(f"Elapsed: {duration:.2f}s")

        raise SystemExit(exc.returncode) from exc

    completed_at = datetime.now(UTC)

    total_duration = time.perf_counter() - overall_started

    print_banner("CostScope refresh complete")

    print(
        "Completed:",
        completed_at.isoformat(),
    )

    print(f"Duration: {total_duration:.2f}s")

    print()
    print("✓ Source extraction")
    print("✓ Silver transformations")
    print("✓ Gold modelling")

    if not args.skip_database:
        print("✓ PostgreSQL refresh")
        print("✓ PostgreSQL validation")


if __name__ == "__main__":
    main()
