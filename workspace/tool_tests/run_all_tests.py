"""Run every isolated ai_cookbook tool test sequentially and summarize results."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = Path(__file__).resolve().parent
TEST_NAMES = [
    "test_read_file.py",
    "test_write_file.py",
    "test_edit_file.py",
    "test_list_files.py",
    "test_run_code.py",
    "test_safe_shell.py",
    "test_web_search.py",
    "test_fetch_page.py",
    "test_remember.py",
    "test_recall.py",
    "test_index_code_file.py",
    "test_search_code.py",
]
TEST_TIMEOUT_SECONDS = 120


def run_test(test_path: Path) -> tuple[bool, str]:
    """Run one test in a fresh process so state and imports stay isolated."""
    try:
        completed = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {TEST_TIMEOUT_SECONDS}s"

    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode == 0, output or "(no output)"


def main() -> int:
    """Execute all tests sequentially, print their output, and return a CI-friendly code."""
    outcomes: list[tuple[str, bool]] = []
    for name in TEST_NAMES:
        print(f"\n=== {name} ===")
        passed, output = run_test(TEST_DIR / name)
        print(output)
        outcomes.append((name, passed))

    print("\n=== SUMMARY ===")
    for name, passed in outcomes:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    passed_count = sum(passed for _, passed in outcomes)
    print(f"\nResult: {passed_count}/{len(outcomes)} passed")
    return 0 if passed_count == len(outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
