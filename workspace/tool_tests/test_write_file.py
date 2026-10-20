"""Exercise write_file by producing an isolated deployment report artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from filesystem import write_file  # noqa: E402


def main() -> bool:
    """Write structured report data and verify that the artifact is readable."""
    relative_path = "tool_tests/runtime/write_file/deployment_report.json"
    report = {
        "commit": "demo-2026-10-19",
        "checks": {"api": True, "frontend": True, "agent": True},
        "status": "ready",
    }
    result = write_file(relative_path, json.dumps(report, indent=2) + "\n")
    # Expected: parent directories are created and the file contains the report.
    if not result.get("ok"):
        print(f"FAIL: write_file returned an error: {result.get('error')}")
        return False

    output_path = ROOT / "workspace" / relative_path
    try:
        written = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: written report could not be verified: {exc}")
        return False

    passed = written == report and result.get("bytes", 0) > 0
    print("PASS: write_file created and verified deployment_report.json" if passed else "FAIL: report content mismatch")
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
