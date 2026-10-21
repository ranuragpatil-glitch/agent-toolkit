"""Exercise read_file by loading and validating a realistic JSON configuration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from filesystem import read_file  # noqa: E402


def main() -> bool:
    """Read the fixture and verify the expected service configuration is present."""
    path = "tool_tests/sample_data/project_config.json"
    result = read_file(path)
    # Expected: the tool returns ok=True and valid JSON with the test environment.
    if not result.get("ok"):
        print(f"FAIL: read_file returned an error: {result.get('error')}")
        return False

    try:
        config = json.loads(result["content"])
    except (KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: configuration was not valid JSON: {exc}")
        return False

    passed = config.get("service") == "ghost-companion" and config.get("environment") == "test"
    if passed:
        print("PASS: read_file loaded and parsed project_config.json")
    else:
        print(f"FAIL: unexpected configuration payload: {config}")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
