# tools.py
from filesystem import read_file, write_file, edit_file, list_files
from run_code import run_code, safe_shell
from search import web_search, fetch_page
from memory import remember, recall, index_code_file, search_code


# ---------- Tool Registry ----------
TOOL_REGISTRY = {
    # Filesystem
    "read_file":       read_file,
    "write_file":      write_file,
    "edit_file":       edit_file,
    "list_files":      list_files,
    # Execution
    "run_code":        run_code,
    "safe_shell":      safe_shell,
    # Web
    "web_search":      web_search,
    "fetch_page":      fetch_page,
    # Memory
    "remember":        remember,
    "recall":          recall,
    "index_code_file": index_code_file,
    "search_code":     search_code,
}


# ---------- Dispatcher ----------
def execute_tool(name: str, args: dict) -> dict:
    """Tool name + args le kar safely execute karo."""
    if name not in TOOL_REGISTRY:
        return {"ok": False, "error": f"Unknown tool: {name}"}

    fn = TOOL_REGISTRY[name]
    try:
        result = fn(**args)
        # Standardize: har tool {ok: bool, ...} return karta hai
        return result if isinstance(result, dict) else {"ok": True, "result": result}
    except TypeError as e:
        return {"ok": False, "error": f"Bad args for {name}: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def list_tools() -> list[str]:
    """Available tools ki list."""
    return list(TOOL_REGISTRY.keys())