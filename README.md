# Free Stack Coding Agent

Qwen2.5-Coder 14B based local coding agent.
Think first → write code → use tools only when needed.

## Setup

```bash
# 1. Ollama + model
ollama pull qwen2.5-coder:14b

# 2. Python deps
pip install -r requirements.txt
playwright install chromium

# 3. Run
python main.py "Fibonacci function likho with tests"
python main.py --list-tools
```

## Structure

- `agent.py`      — LangGraph flow (planner → coder → tools → reflect)
- `tools.py`      — Tool registry + dispatcher
- `filesystem.py` — Safe read/write/edit/list
- `run_code.py`   — Sandbox + subprocess + safe_shell
- `search.py`     — Web search (ddgs) + page fetch (Playwright)
- `memory.py`     — ChromaDB memory + code index
- `config.py`     — Settings
- `prompts.py`    — System prompts
- `utils.py`      — Helpers (safe_path, extract_code_block, ...)
- `main.py`       — CLI entry point

## Flow

User task → Planner (sochna) → Coder (code likhna) → Tool Router (zarurat pe tools) → Reflect (retry/done)
