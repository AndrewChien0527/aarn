"""
Light wrapper for OpenAI (or other provider).
This module is optional — if OPENAI_API_KEY is not set, the extractors should fallback to heuristic rules.
"""
import os
import requests
from ..config import OPENAI_API_KEY, OPENAI_MODEL




def call_openai_chat(prompt: str, max_tokens: int = 256) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
"model": OPENAI_MODEL,
"messages": [{"role": "user", "content": prompt}],
"max_tokens": max_tokens,
"temperature": 0,
}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"].strip()