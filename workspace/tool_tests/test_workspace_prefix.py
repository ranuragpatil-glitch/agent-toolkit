"""Verify workspace-prefixed paths do not create a nested workspace directory."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from filesystem import write_file  # noqa: E402


def main() -> bool:
    """Write through the public tool API and verify the normalized location."""
    expected_path = ROOT / "workspace" / "_prefix_check.txt"
    nested_path = ROOT / "workspace" / "workspace" / "_prefix_check.txt"
    original_expected = expected_path.read_bytes() if expected_path.exists() else None
    original_nested = nested_path.read_bytes() if nested_path.exists() else None

    result = write_file("workspace/_prefix_check.txt", "workspace prefix normalized\n")
    try:
        passed = (
            result.get("ok") is True
            and expected_path.is_file()
            and not nested_path.exists()
        )
        print("PASS: workspace/ prefix resolved to the existing workspace" if passed else "FAIL: workspace/ prefix created an unexpected path")
        return passed
    finally:
        if original_expected is None and expected_path.exists():
            expected_path.unlink()
        elif original_expected is not None:
            expected_path.write_bytes(original_expected)
        if original_nested is None and nested_path.exists():
            nested_path.unlink()
        elif original_nested is not None:
            nested_path.write_bytes(original_nested)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
