"""Exercise fetch_page by extracting visible text from a small public documentation page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from search import fetch_page  # noqa: E402


def main() -> bool:
    """Fetch example.com and verify that browser-rendered body text is returned."""
    result = fetch_page("https://example.com")
    # Expected: Playwright returns body text containing the page's canonical heading.
    content = result.get("content", "")
    passed = bool(result.get("ok")) and "documentation examples" in content
    if passed:
        print(f"PASS: fetch_page extracted {len(content)} characters from example.com")
    else:
        print(f"FAIL: fetch_page result={result}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
