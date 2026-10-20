"""Exercise index_code_file by indexing functions and a class from a Python fixture."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory import index_code_file  # noqa: E402


def main() -> bool:
    """Extract and persist semantic chunks from the deployment-readiness fixture."""
    result = index_code_file("tool_tests/sample_data/index_target.py", project_root=".")
    # Expected: at least the DeploymentReport class and readiness function are indexed.
    passed = bool(result.get("ok")) and result.get("chunks_indexed", 0) >= 2
    if passed:
        print(f"PASS: index_code_file indexed {result['chunks_indexed']} code chunks")
    else:
        print(f"FAIL: index_code_file result={result}")
    return bool(passed)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
