# agent-toolkit tool tests

These independent demos exercise the 12 tools registered in `tools.py` using realistic file, code, web, and memory tasks. They only create runtime artifacts below `workspace/tool_tests/`.

## Tools covered

| Test | Tool | What it demonstrates |
| --- | --- | --- |
| `test_read_file.py` | `read_file` | Loads and validates a JSON service configuration. |
| `test_write_file.py` | `write_file` | Creates a structured deployment report. |
| `test_edit_file.py` | `edit_file` | Updates one Python-version policy in a TOML fragment. |
| `test_list_files.py` | `list_files` | Recursively inventories sample fixtures. |
| `test_run_code.py` | `run_code` | Calculates a release-health score in a subprocess. |
| `test_safe_shell.py` | `safe_shell` | Runs an allowlisted, read-only Python inventory command. |
| `test_web_search.py` | `web_search` | Searches for current FastAPI testing guidance. |
| `test_fetch_page.py` | `fetch_page` | Extracts visible text from `example.com` using Playwright. |
| `test_remember.py` | `remember` | Stores a tagged testing decision in ChromaDB. |
| `test_recall.py` | `recall` | Queries project decision memory. |
| `test_index_code_file.py` | `index_code_file` | Indexes functions/classes from a Python fixture. |
| `test_search_code.py` | `search_code` | Searches the semantic code index. |

## Run everything

From the project root:

```bash
python workspace/tool_tests/run_all_tests.py
```

Run one test directly when debugging:

```bash
python workspace/tool_tests/test_read_file.py
```

## Expected output

Each test prints either `PASS: ...` or `FAIL: ...`. The master runner prints one section per test and a final count. File and subprocess tests should pass on a configured checkout. Web tests require network access; `fetch_page` also requires a Playwright Chromium installation. Memory and code-index tests require the project's ChromaDB/tree-sitter dependencies and their embedding model to be available.
