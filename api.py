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
    code = (result.get("code") or "").strip()
    tool_calls = result.get("tool_calls") or []

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
