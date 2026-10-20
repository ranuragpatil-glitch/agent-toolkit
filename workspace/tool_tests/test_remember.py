"""Exercise remember by storing a tagged project-testing decision in ChromaDB."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory import remember  # noqa: E402


def main() -> bool:
    """Persist a useful testing note and report the generated memory identifier."""
    result = remember(
        "Tool tests: the deployment checklist requires FastAPI smoke tests before release.",
        tag="tool_tests",
    )
    # Expected: ChromaDB acknowledges the note with ok=True and a generated id.
    passed = bool(result.get("ok")) and bool(result.get("id"))
    if passed:
        print(f"PASS: remember stored a tagged note with id={result['id']}")
    else:
        print(f"FAIL: remember result={result}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
