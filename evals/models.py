"""Model adapters. Add your own: any function str -> str works."""
from __future__ import annotations

import os

_CANNED = {
    "capital of france": "The capital of France is Paris.",
    "2+2": "4",
    "json": '{"name": "Ada", "age": 36}',
}


def mock_model(prompt: str) -> str:
    """Deterministic offline model so the kit runs with no API key."""
    p = prompt.lower()
    for key, answer in _CANNED.items():
        if key in p:
            return answer
    return "I'm not sure."


def anthropic_model(model: str | None = None, system: str | None = None):
    import anthropic

    client = anthropic.Anthropic()
    model = model or os.getenv("EVAL_MODEL", "claude-sonnet-5-5")

    def call(prompt: str) -> str:
        kwargs = {"system": system} if system else {}
        resp = client.messages.create(
            model=model, max_tokens=1000,
            messages=[{"role": "user", "content": prompt}], **kwargs)
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    return call
