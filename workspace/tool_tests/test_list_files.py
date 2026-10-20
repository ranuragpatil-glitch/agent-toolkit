"""Exercise list_files by inventorying a nested release-health fixture directory."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from filesystem import list_files  # noqa: E402


def main() -> bool:
    """List fixtures recursively and confirm the expected source types are present."""
    result = list_files("tool_tests/sample_data")
    # Expected: recursive listing returns relative paths for JSON, Python, and Markdown fixtures.
    required = {"project_config.json", "metrics.py", "index_target.py", "notes.md"}
    files = set(result.get("files", [])) if result.get("ok") else set()
    passed = bool(result.get("ok")) and required.issubset(files)
    if passed:
        print(f"PASS: list_files found {len(files)} sample-data files")
    else:
        print(f"FAIL: list_files result={result}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
