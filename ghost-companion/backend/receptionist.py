"""Local Qwen receptionist for Pookie.

The receptionist does one small, reliable job: classify a message as CHAT or
TASK and return a compact JSON decision. Heavy work is intentionally kept out
of this module and is delegated to the existing Nemotron agent by api.py.
"""

from __future__ import annotations

import json
import os
import re
from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError

Intent = Literal["CHAT", "TASK"]
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


RECEPTIONIST_SYSTEM_PROMPT = """Tum Pookie ho — ek cute purple ghost AI companion.

Tumhara kaam:
1. User ka message padho.
2. Decide karo: yeh CHAT hai ya TASK.
3. Mood decide karo.
4. Agar CHAT hai to short cute Hinglish reply do.
5. Agar TASK hai to task_for_nemotron mein clean English task likho.

Intent rules:
- CHAT is the default for text-only answers: greeting, emotional baat, "kaisa hai", bored, motivate, simple personal talk, or showing/writing/explaining a short code snippet. Code shown only as text is still CHAT; do not run it, inspect the user's files, or change anything on the machine.
- TASK only when Pookie must do something on the user's machine: run or execute code, read/inspect actual files, screen, or repository state, create/edit/delete real files, fix a real project bug, refactor the repository, or perform a multi-step/tool-using action.
- If the request can be answered completely in text and no machine action is requested, choose CHAT. When uncertain, choose CHAT.

Mood rules:
- happy: normal chat ya success.
- thinking: complex question ya sochne wali baat.
- concerned: error ya bug detect hua.
- processing: task ko kaam ke liye bhejna hai.
- proud: task successfully complete hua.
- angry: repeated errors ya user frustrated hai.
- sulking: user disappointed ya low feel kar raha hai.
- notification: short announcement ya update.

Response format (ONLY valid JSON, no markdown, no extra text):
{
  "intent": "CHAT" or "TASK",
  "mood": "happy|thinking|concerned|proud|processing|angry|sulking|notification",
  "reply": "CHAT ke liye max 2-3 short Hinglish lines; TASK ke liye short cute acknowledgement",
  "task_for_nemotron": "TASK ke liye clean English task, warna null"
}

Important:
- Reply hamesha short, cute aur supportive rakho.
- Text-only code requests (for example, "python hello world program de sakte ho kya?" or "write a short function") are CHAT and should be answered directly with a concise snippet or explanation.
- TASK hone pe reply mein sirf short acknowledgement do jaise:
  "Theek hai, Pookie dekh raha hai... 🛠️"
  "Samajh gaya, ab Nemotron ko de raha hoon 👻"
  "On it! ✨"
- Kabhi markdown ya extra text mat likho. Sirf pure JSON.
"""


class ReceptionistDecision(BaseModel):
    intent: Intent
    mood: Mood = "happy"
    reply: str = Field(default="Haan, Pookie yahin hoon 👻", max_length=600)
    task_for_nemotron: str | None = Field(default=None, max_length=4000)


class ReceptionistError(RuntimeError):
    """Raised when local Ollama cannot produce a usable decision."""


def _extract_json(raw: str) -> str:
    """Remove Qwen thinking/code-fence noise and isolate the JSON object."""
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ReceptionistError("Qwen returned no JSON object")
    return cleaned[start : end + 1]


def _normalise_decision(payload: dict, original_message: str) -> ReceptionistDecision:
    """Validate model output while keeping the routing contract strict."""
    intent = str(payload.get("intent", "CHAT")).upper()
    if intent not in {"CHAT", "TASK"}:
        raise ReceptionistError(f"Invalid receptionist intent: {intent}")

    allowed_moods = {
        "happy", "thinking", "concerned", "proud",
        "processing", "angry", "sulking", "notification",
    }
    mood = str(payload.get("mood", "processing" if intent == "TASK" else "happy")).lower()
    if mood not in allowed_moods:
        mood = "processing" if intent == "TASK" else "happy"

    reply = str(payload.get("reply") or "Pookie samajh gaya 👻").strip()
    task = payload.get("task_for_nemotron")
    task = str(task).strip() if task else None

    if intent == "TASK" and not task:
        task = original_message.strip()

    # TASK hone pe mood force processing (better UX)
    if intent == "TASK" and mood not in {"processing", "concerned"}:
        mood = "processing"

    try:
        return ReceptionistDecision(
            intent=intent,
            mood=mood,
            reply=reply[:600],
            task_for_nemotron=task[:4000] if task else None,
        )
    except ValidationError as exc:
        raise ReceptionistError(f"Invalid receptionist JSON: {exc}") from exc


def classify_message(message: str) -> ReceptionistDecision:
    """Ask the local Ollama Qwen model to classify one user message."""
    message = message.strip()
    if not message:
        raise ReceptionistError("Message cannot be empty")

    ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
    timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": 0.15, "num_predict": 350},
        "messages": [
            {"role": "system", "content": RECEPTIONIST_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(f"{ollama_url}/api/chat", json=payload)
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ReceptionistError(f"Ollama receptionist unavailable: {exc}") from exc

    content = body.get("message", {}).get("content", "")
    try:
        decoded = json.loads(_extract_json(content))
    except (json.JSONDecodeError, ReceptionistError) as exc:
        raise ReceptionistError(f"Ollama receptionist returned invalid JSON: {exc}") from exc

    if not isinstance(decoded, dict):
        raise ReceptionistError("Ollama receptionist JSON must be an object")

    return _normalise_decision(decoded, message)
