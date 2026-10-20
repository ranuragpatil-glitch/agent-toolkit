"""Exercise recall by querying the project's decision memory for testing context."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory import recall  # noqa: E402


def main() -> bool:
    """Run a semantic memory query and report how many relevant notes were found."""
    result = recall("deployment checklist and FastAPI smoke tests", k=3)
    # Expected: the tool returns ok=True; zero results is valid when memory is empty.
    passed = bool(result.get("ok")) and isinstance(result.get("results"), list)
    if passed:
        print(f"PASS: recall returned {len(result['results'])} matching memory notes")
    else:
        print(f"FAIL: recall result={result}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
