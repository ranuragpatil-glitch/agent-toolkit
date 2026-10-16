# utils.py
"""Helper functions used across the agent."""
from pathlib import Path
from config import WORKSPACE


def safe_path(path: str) -> Path:
    """
    Resolve path inside WORKSPACE only.
    Path escape attempts are blocked.
    """
    full = (WORKSPACE / path).resolve()
    if not str(full).startswith(str(WORKSPACE.resolve())):
        raise PermissionError(f"Path escape blocked: {path}")
    return full


def extract_code_block(text: str) -> str:
    """
    Extract first ```python ... ``` block.
    Agar block na mile to pura text return karo.
    """
    if not text:
        return ""
    marker = "```python"
    if marker in text:
        start = text.find(marker) + len(marker)
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    # fallback: generic ``` block
    if "```" in text:
        start = text.find("```") + 3
        # skip optional language tag on same line
        newline = text.find("\n", start)
        if newline != -1:
            start = newline + 1
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    return text.strip()


def format_errors(errors: list) -> str:
    """Error list ko readable string banao."""
    if not errors:
        return "(no errors)"
    return "\n".join(f"- {e}" for e in errors)


def truncate(text: str, max_len: int = 1500) -> str:
    """Long text ko truncate karo (prompt size control)."""
    if not text or len(text) <= max_len:
        return text or ""
    return text[:max_len] + f"\n... [truncated {len(text) - max_len} chars]"
