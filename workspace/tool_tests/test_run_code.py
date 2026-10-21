"""Exercise run_code with a small release-health calculation in a subprocess."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run_code import run_code  # noqa: E402


def main() -> bool:
    """Run a realistic check aggregation and validate its printed status."""
    code = """
from statistics import mean

checks = {"api": True, "routing": True, "frontend": True, "docs": False}
pass_rate = round(mean(checks.values()) * 100, 1)
status = "ready" if pass_rate >= 75 else "blocked"
print(f"status={status}; pass_rate={pass_rate}; checks={len(checks)}")
"""
    result = run_code(code, mode="subprocess")
    # Expected: isolated execution succeeds and reports a 75% readiness score.
    output = result.get("stdout", "")
    passed = result.get("ok") and "status=ready" in output and "pass_rate=75.0" in output
    if passed:
        print(f"PASS: run_code produced {output.strip()}")
    else:
        print(f"FAIL: run_code result={result}")
    return bool(passed)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
