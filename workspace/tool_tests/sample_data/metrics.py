"""Small fixture used by the tool tests to model release-health metrics."""

from collections.abc import Iterable


def success_rate(results: Iterable[bool]) -> float:
    """Return the percentage of successful checks as a number from 0 to 100."""
    values = list(results)
    return round((sum(values) / len(values)) * 100, 2) if values else 0.0


def release_label(rate: float, threshold: float = 90.0) -> str:
    """Classify a release as ready or blocked using a configurable threshold."""
    return "ready" if rate >= threshold else "blocked"
