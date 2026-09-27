"""
Progress utilities for CostScope pipeline operations.

Progress bars are intended for operations where visual feedback is useful,
such as processing batches of files, locations, API pages or records.

Progress bars complement structured logging rather than replacing it.
"""

from collections.abc import Iterable

from tqdm import tqdm


def track_progress[T](
    iterable: Iterable[T],
    *,
    description: str,
    unit: str = "item",
) -> Iterable[T]:
    """
    Wrap an iterable with a consistent CostScope progress bar.

    Parameters
    ----------
    iterable:
        Items to process.

    description:
        Human-readable description displayed beside the progress bar.

    unit:
        Name of the unit being processed, such as ``file``, ``row`` or
        ``location``.

    Returns
    -------
    Iterable[T]
        The input iterable wrapped with tqdm progress reporting.
    """

    return tqdm(
        iterable,
        desc=description,
        unit=unit,
        dynamic_ncols=True,
        leave=True,
    )
