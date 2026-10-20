"""Exercise edit_file by applying a single safe dependency-policy update."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from filesystem import edit_file  # noqa: E402


def main() -> bool:
    """Seed an isolated TOML fragment, then replace exactly one configuration value."""
    relative_path = "tool_tests/runtime/edit_file/pyproject.toml"
    output_path = ROOT / "workspace" / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        '[project]\nname = "demo-service"\nrequires-python = ">=3.11"\n',
        encoding="utf-8",
    )

    result = edit_file(
        relative_path,
        'requires-python = ">=3.11"',
        'requires-python = ">=3.12"',
    )
    # Expected: one occurrence is replaced and unrelated project metadata stays intact.
    updated = output_path.read_text(encoding="utf-8")
    passed = result.get("ok") and 'requires-python = ">=3.12"' in updated and 'name = "demo-service"' in updated
    if passed:
        print("PASS: edit_file updated the Python version policy once")
    else:
        print(f"FAIL: edit_file result={result}; file={updated!r}")
    return bool(passed)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
