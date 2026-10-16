# memory.py
import uuid

try:
    import chromadb  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    chromadb = None

try:
    import tree_sitter_languages  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    tree_sitter_languages = None

from config import MEMORY_DIR, CODE_INDEX_DIR, MEMORY_COLLECTION, CODE_COLLECTION, MAX_MEMORY_RESULTS


def _require_chromadb() -> None:
    if chromadb is None:
        raise RuntimeError("chromadb is not installed. Install it with: pip install chromadb")


# ---------- Decisions Memory ----------
if chromadb is not None:
    _mem_client = chromadb.PersistentClient(path=str(MEMORY_DIR))
    _mem_coll = _mem_client.get_or_create_collection(MEMORY_COLLECTION)
else:
    _mem_client = None
    _mem_coll = None


def remember(text: str, tag: str = "general") -> dict:
    """Ek decision/note yaad rakho."""
    try:
        _require_chromadb()
        if _mem_coll is None:
            raise RuntimeError("Memory collection is unavailable")
        doc_id = f"{tag}-{uuid.uuid4().hex[:8]}"
        _mem_coll.add(documents=[text], metadatas=[{"tag": tag}], ids=[doc_id])
        return {"ok": True, "id": doc_id}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def recall(query: str, k: int = MAX_MEMORY_RESULTS) -> dict:
    """Purane decisions recall karo."""
    try:
        _require_chromadb()
        if _mem_coll is None:
            raise RuntimeError("Memory collection is unavailable")
        if _mem_coll.count() == 0:
            return {"ok": True, "results": []}
        r = _mem_coll.query(query_texts=[query], n_results=min(k, _mem_coll.count()))
        docs = r["documents"][0] if r["documents"] else []
        return {"ok": True, "results": docs}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# ---------- Code Index (tree-sitter + Chroma) ----------
if chromadb is not None:
    _code_client = chromadb.PersistentClient(path=str(CODE_INDEX_DIR))
    _code_coll = _code_client.get_or_create_collection(CODE_COLLECTION)
else:
    _code_client = None
    _code_coll = None


def index_code_file(filepath: str, project_root: str = ".") -> dict:
    """File ke functions/classes extract karke embed karo."""
    try:
        import tree_sitter_languages
        from pathlib import Path

        parser = tree_sitter_languages.get_parser("python")
        src = Path(filepath).read_bytes()
        tree = parser.parse(src)

        chunks = []
        for node in tree.root_node.children:
            if node.type in ("function_definition", "class_definition"):
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode() if name_node else "anon"
                chunks.append({
                    "name": name,
                    "type": node.type,
                    "code": src[node.start_byte:node.end_byte].decode("utf-8", errors="ignore"),
                    "line": node.start_point[0],
                })

        for c in chunks:
            _code_coll.add(
                documents=[c["code"]],
                metadatas=[{"name": c["name"], "type": c["type"],
                            "file": filepath, "line": c["line"]}],
                ids=[f"{filepath}:{c['name']}:{c['line']}"],
            )
        return {"ok": True, "chunks_indexed": len(chunks)}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def search_code(query: str, k: int = 5) -> dict:
    """Similar code chunks dhoondho."""
    try:
        if _code_coll.count() == 0:
            return {"ok": True, "results": []}
        r = _code_coll.query(query_texts=[query], n_results=min(k, _code_coll.count()))
        return {"ok": True, "results": r["documents"][0] if r["documents"] else []}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}