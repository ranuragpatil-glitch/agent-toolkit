"""Exercise safe_shell with an allowlisted, read-only Python inventory command."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run_code import safe_shell  # noqa: E402


def main() -> bool:
    """Count Python fixtures using the project's allowlisted `python` shell binary."""
    command = (
        "python -c \"from pathlib import Path; files = sorted(Path('tool_tests/sample_data').glob('*.py')); "
        "print('sample_python_files=' + str(len(files)))\""
    )
    result = safe_shell(command)
    # Expected: the allowlist permits python and the command reports at least two fixtures.
    output = result.get("stdout", "")
    passed = result.get("ok") and "sample_python_files=2" in output
    if passed:
        print(f"PASS: safe_shell completed an allowlisted inventory: {output.strip()}")
    else:
        print(f"FAIL: safe_shell result={result}")
    return bool(passed)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
