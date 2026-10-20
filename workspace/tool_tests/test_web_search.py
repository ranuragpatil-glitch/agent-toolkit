"""Exercise web_search for current FastAPI testing guidance."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from search import web_search  # noqa: E402


def main() -> bool:
    """Search for authoritative FastAPI testing material and keep the result set bounded."""
    result = web_search("FastAPI testing TestClient official documentation", max_results=3)
    # Expected: network search succeeds and returns no more than three normalized results.
    results = result.get("results", [])
    passed = bool(result.get("ok")) and 0 < len(results) <= 3 and all(item.get("url") for item in results)
    if passed:
        titles = "; ".join(item.get("title", "untitled") for item in results)
        print(f"PASS: web_search returned {len(results)} results: {titles}")
    else:
        print(f"FAIL: web_search result={result}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
