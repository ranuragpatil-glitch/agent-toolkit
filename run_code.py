# run_code.py
import subprocess
import sys
import tempfile
from pathlib import Path
from RestrictedPython import compile_restricted, safe_globals, safe_builtins
from config import SANDBOX_TIMEOUT, SHELL_ALLOWLIST, WORKSPACE


# ---------- Python Sandbox (RestrictedPython) ----------
def run_python_sandbox(code: str) -> dict:
    """RestrictedPython ke andar code run karo (safe)."""
    try:
        byte_code = compile_restricted(code, filename="<sandbox>", mode="exec")
        local_ns = {}
        exec(byte_code, {"__builtins__": safe_builtins}, local_ns)
        # __builtins__ ke bahar wale vars return karo
        result = {k: repr(v) for k, v in local_ns.items() if not k.startswith("__")}
        return {"ok": True, "locals": result}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# ---------- Subprocess Python (real execution with timeout) ----------
def run_python_subprocess(code: str, timeout: int = SANDBOX_TIMEOUT) -> dict:
    """Real Python process mein code chalao (isolated + timeout)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", dir=WORKSPACE, delete=False
    ) as f:
        f.write(code)
        tmp_path = Path(f.name)

    try:
        r = subprocess.run(
            [sys.executable, str(tmp_path)],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": r.returncode == 0,
            "stdout": r.stdout[-2000:],
            "stderr": r.stderr[-2000:],
            "returncode": r.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    finally:
        tmp_path.unlink(missing_ok=True)


# ---------- Safe Shell ----------
def safe_shell(cmd: str) -> dict:
    """Allowlisted shell command chalao."""
    binary = cmd.strip().split()[0] if cmd.strip() else ""
    if binary not in SHELL_ALLOWLIST:
        return {"ok": False, "error": f"Command '{binary}' not allowed"}
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=WORKSPACE,
            capture_output=True, text=True, timeout=SANDBOX_TIMEOUT,
        )
        return {
            "ok": r.returncode == 0,
            "stdout": r.stdout[-2000:],
            "stderr": r.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# ---------- Unified Entry ----------
def run_code(code: str, mode: str = "subprocess") -> dict:
    """
    mode='subprocess' → real execution (recommended for tests)
    mode='sandbox'    → RestrictedPython (fast but limited)
    """
    if mode == "sandbox":
        return run_python_sandbox(code)
    return run_python_subprocess(code)