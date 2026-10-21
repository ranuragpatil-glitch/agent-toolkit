# filesystem.py
from utils import safe_path


def read_file(path: str) -> dict:
    """File padho. Returns {ok, content/error}."""
    try:
        p = safe_path(path)
        if not p.exists():
            return {"ok": False, "error": f"File not found: {path}"}
        return {"ok": True, "content": p.read_text(encoding="utf-8")}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def write_file(path: str, content: str) -> dict:
    """File likho (parent dirs auto-create)."""
    try:
        p = safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True, "bytes": len(content), "path": path}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def edit_file(path: str, old: str, new: str) -> dict:
    """File mein ek occurrence replace karo."""
    try:
        p = safe_path(path)
        if not p.exists():
            return {"ok": False, "error": f"File not found: {path}"}
        txt = p.read_text(encoding="utf-8")
        if old not in txt:
            return {"ok": False, "error": "old string not found in file"}
        if txt.count(old) > 1:
            return {"ok": False, "error": f"old string appears {txt.count(old)} times — be more specific"}
        p.write_text(txt.replace(old, new, 1), encoding="utf-8")
        return {"ok": True, "path": path}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def list_files(dir_path: str = ".") -> dict:
    """Directory listing."""
    try:
        p = safe_path(dir_path)
        if not p.is_dir():
            return {"ok": False, "error": f"Not a directory: {dir_path}"}
        files = [str(f.relative_to(p)) for f in p.rglob("*") if f.is_file()]
        return {"ok": True, "files": files}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}