"""Exercise search_code with a semantic query for deployment-readiness logic."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory import search_code  # noqa: E402


def main() -> bool:
    """Query the code index and accept either matches or a valid empty collection."""
    result = search_code("calculate deployment readiness from named checks", k=3)
    # Expected: search_code returns ok=True and a list, even when no index has been built yet.
    passed = bool(result.get("ok")) and isinstance(result.get("results"), list)
    if passed:
        print(f"PASS: search_code returned {len(result['results'])} matching code chunks")
    else:
        print(f"FAIL: search_code result={result}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
