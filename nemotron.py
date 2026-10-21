"""Lazy bridge to the user's existing ai_cookbook agent.

`ai_cookbook` is deliberately not copied or edited by this companion layer.
The existing project is discovered as a sibling folder by default, or can be
set explicitly with AI_COOKBOOK_PATH.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any


class NemotronUnavailable(RuntimeError):
    """Raised when the existing Nemotron agent cannot be loaded or run."""


def _candidate_directories() -> list[Path]:
    explicit = os.getenv("AI_COOKBOOK_PATH")
    companion_root = Path(__file__).resolve().parents[1]

    if explicit:
        explicit_path = Path(explicit).expanduser()
        if not explicit_path.is_absolute():
            explicit_path = (Path(__file__).resolve().parent / explicit_path).resolve()
        candidates = [explicit_path]
    else:
        candidates = []

    candidates.extend(
        [
            companion_root.parent / "ai_cookbook",
            companion_root / "ai_cookbook",
        ]
    )
    return candidates


def _load_run_agent():
    for directory in _candidate_directories():
        if not directory.is_dir() or not (directory / "agent.py").is_file():
            continue

        directory_string = str(directory.resolve())
        if directory_string not in sys.path:
            sys.path.insert(0, directory_string)

        try:
            module = importlib.import_module("agent")
            run_agent = module.run_agent
            return run_agent
        except (ImportError, AttributeError) as exc:
            raise NemotronUnavailable(
                f"Could not import run_agent from {directory}: {exc}"
            ) from exc

    searched = ", ".join(str(path) for path in _candidate_directories())
    raise NemotronUnavailable(
        "ai_cookbook/agent.py not found. Set AI_COOKBOOK_PATH to the existing folder. "
        f"Searched: {searched}"
    )


def run_nemotron(task: str) -> dict[str, Any]:
    """Run the existing agent without changing its source or configuration."""
    try:
        return _load_run_agent()(task)
    except NemotronUnavailable:
        raise
    except Exception as exc:
        raise NemotronUnavailable(f"Nemotron task failed: {exc}") from exc