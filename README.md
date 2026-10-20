# ai_cookbook

`ai_cookbook` is a Python coding agent powered by LangGraph, NVIDIA Nemotron, local ChromaDB memory, and a 12-tool execution layer. The optional `ghost-companion/` application adds a local Pookie desktop companion with a FastAPI backend and Electron frontend.

## Setup

```bash
conda activate agent
pip install -r requirements.txt
playwright install chromium
```

Provide `NVIDIA_API_KEY` in the local environment. Keep `.env` untracked.

## Tools

The agent registers these tools in `tools.py`:

`read_file`, `write_file`, `edit_file`, `list_files`, `run_code`, `safe_shell`, `web_search`, `fetch_page`, `remember`, `recall`, `index_code_file`, and `search_code`.

## Run

```bash
python main.py --list-tools
python main.py "Fibonacci function likho with tests"
```

The companion backend can be started with `uvicorn api:app --reload` from `ghost-companion/backend/`. The Electron frontend is in `ghost-companion/frontend/`.

## Tests

```bash
python workspace/tool_tests/run_all_tests.py
```

Expected result: **12/12 passed**. `fetch_page` needs network access and a Chromium installation. Memory and code-index tests need ChromaDB and its embedding model.

## Test results

![12/12 tool tests passing](docs/images/test-results.png)


## Example task

![Pookie running FizzBuzz](docs/images/task-fizzbuzz.png)