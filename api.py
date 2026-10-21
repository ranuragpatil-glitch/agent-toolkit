"""Pookie's FastAPI companion layer."""

from __future__ import annotations

import os
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from nemotron import NemotronUnavailable, run_nemotron
from receptionist import ReceptionistError, classify_message

Mood = Literal[
    "happy",
    "thinking",
    "concerned",
    "proud",
    "processing",
    "angry",
    "sulking",
    "notification",
]
Status = Literal["chat", "task", "error"]
Source = Literal["qwen", "nemotron"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    reply: str
    mood: Mood
    status: Status
    source: Source


def _origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app = FastAPI(title="Pookie Ghost Companion API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _short_error(message: str) -> str:
    compact = " ".join(message.split())
    return compact[:220] + ("…" if len(compact) > 220 else "")


def _format_nemotron_success(result: dict) -> str:
    """Extract useful output from Nemotron agent result."""
    tool_results = result.get("tool_results") or []
    code = (result.get("code") or "").strip()
    tool_calls = result.get("tool_calls") or []

    if tool_results:
        summaries = []
        for entry in tool_results:
            tool_name = entry.get("tool") or "tool"
            tool_result = entry.get("result") or {}
            args = entry.get("args") or {}
            path = tool_result.get("path") or args.get("path") or args.get("filepath")

            if tool_name == "write_file" and tool_result.get("ok") and path:
                summaries.append(f"Wrote {path}")
            elif tool_name == "edit_file" and tool_result.get("ok") and path:
                summaries.append(f"Updated {path}")
            elif tool_name == "read_file" and tool_result.get("ok") and path:
                summaries.append(f"Read {path}")
            elif tool_name == "list_files" and tool_result.get("ok"):
                summaries.append(f"Listed {len(tool_result.get('files') or [])} files")
            elif tool_name in {"run_code", "safe_shell"}:
                if tool_result.get("ok"):
                    stdout = (tool_result.get("stdout") or "").strip()
                    if stdout:
                        tail = "\n".join(stdout.splitlines()[-6:])
                        summaries.append(f"{tool_name} output:\n{tail}")
                    else:
                        summaries.append(f"{tool_name} completed successfully")
                else:
                    error = tool_result.get("error") or tool_result.get("stderr")
                    if error:
                        summaries.append(f"{tool_name} error: {_short_error(str(error))}")
            elif tool_name == "web_search" and tool_result.get("ok"):
                summaries.append(f"Web search returned {len(tool_result.get('results') or [])} results")
            elif tool_name == "fetch_page" and tool_result.get("ok"):
                summaries.append(f"Fetched {args.get('url', 'the requested page')}")
            elif tool_name == "remember" and tool_result.get("ok"):
                summaries.append(f"Saved memory note {tool_result.get('id', '')}".rstrip())
            elif tool_name == "recall" and tool_result.get("ok"):
                summaries.append(f"Recalled {len(tool_result.get('results') or [])} notes")
            elif tool_name == "index_code_file" and tool_result.get("ok"):
                summaries.append(f"Indexed {tool_result.get('chunks_indexed', 0)} code chunks")
            elif tool_name == "search_code" and tool_result.get("ok"):
                summaries.append(f"Code search returned {len(tool_result.get('results') or [])} results")

        if summaries:
            reply = "Ho gaya! ✨\n\n" + "\n".join(f"• {summary}" for summary in summaries)
            return reply[:1200] + ("…" if len(reply) > 1200 else "")
        return "Ho gaya! ✨\n\nTool result mila, par koi compact output available nahi hai."

    if code:
        preview = code
        if len(preview) > 1200:
            preview = preview[:1200] + "\n\n... (truncated)"
        return f"Ho gaya! ✨\n\n```python\n{preview}\n```"

    if tool_calls:
        return f"Task complete ✨\n\nNemotron ne {len(tool_calls)} tools use kiye. Kaam ho gaya!"

    return "Task complete ✨ Pookie proud hai — Nemotron ne kaam handle kar diya."


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "boo-companion"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Route light conversation to Qwen and heavy tasks to Nemotron."""

    # ---------- 1. Receptionist (local Qwen) ----------
    try:
        decision = classify_message(req.message)
    except ReceptionistError:
        return ChatResponse(
            reply="Pookie ka local brain abhi connect nahi ho pa raha 😵 Ollama check kar lo.",
            mood="concerned",
            status="error",
            source="qwen",
        )

    # ---------- 2. CHAT path ----------
    if decision.intent == "CHAT":
        return ChatResponse(
            reply=decision.reply,
            mood=decision.mood,
            status="chat",
            source="qwen",
        )

    # ---------- 3. TASK path → Nemotron ----------
    task = decision.task_for_nemotron or req.message

    try:
        result = run_nemotron(task)
    except NemotronUnavailable as exc:
        return ChatResponse(
            reply=f"Task route ready tha, par Nemotron connect nahi hua: {_short_error(str(exc))}",
            mood="concerned",
            status="error",
            source="nemotron",
        )

    errors = result.get("errors") or []
    if errors:
        first_error = _short_error(str(errors[0]))
        return ChatResponse(
            reply=f"Thoda snag aaya 😟 {first_error}",
            mood="concerned",
            status="error",
            source="nemotron",
        )

    # Success
    return ChatResponse(
        reply=_format_nemotron_success(result),
        mood="proud",
        status="task",
        source="nemotron",
    )
