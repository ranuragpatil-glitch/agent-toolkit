"""Mood classification for the screen companion."""

import requests


VALID_MOODS = {"happy", "thinking", "concerned", "fixing", "proud"}
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3:4b-instruct-2507-q4_K_M"

SYSTEM_PROMPT = """Tum ek mood classifier ho. Coding agent ke ek run ka context diya jayega.
In 5 moods mein se SIRF EK shabd return karo, kuch aur mat likho:
happy - task clean complete hua, koi error nahi
proud - task complete hua par errors/retries ke baad (struggle karke)
concerned - abhi errors hain, task done nahi
fixing - agent retry loop mein hai
thinking - agent abhi process kar raha hai"""


def _fallback_mood(status: str, retries: int) -> str:
    if status == "done":
        return "proud" if retries > 0 else "happy"
    return "concerned"


def classify_mood(context: dict) -> str:
    """Classify an agent run as one of the five supported companion moods."""
    status = context.get("status", "")
    errors = context.get("errors", []) or []
    retries = context.get("retries", 0)
    reply = context.get("reply", "")

    # Fast-path transient failures without making an LLM request.
    if retries > 0 and status != "done":
        return "fixing"
    if errors and status != "done":
        return "concerned"

    user_message = (
        f"Status: {status}\n"
        f"Retries: {retries}\n"
        f"Errors: {errors}\n"
        f"Reply: {str(reply)[:300]}"
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "think": False,
        "options": {"temperature": 0},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        mood = response.json().get("message", {}).get("content", "")
        mood = mood.strip().lower()
        if mood in VALID_MOODS:
            return mood
    except Exception:
        pass

    return _fallback_mood(status, retries)
