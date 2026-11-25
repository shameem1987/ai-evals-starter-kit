"""Deterministic graders first; LLM-as-judge only where rules can't decide."""
from __future__ import annotations

import json
import os
import re
from typing import Callable


def exact_match(output: str, case: dict) -> bool:
    return output.strip().lower() == str(case["expected"]).strip().lower()


def contains(output: str, case: dict) -> bool:
    return all(s.lower() in output.lower() for s in case["expected"])


def not_contains(output: str, case: dict) -> bool:
    return all(s.lower() not in output.lower() for s in case["expected"])


def regex(output: str, case: dict) -> bool:
    return re.search(case["expected"], output, re.IGNORECASE | re.DOTALL) is not None


def json_valid(output: str, case: dict) -> bool:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return False
    required = case.get("expected") or []
    return all(k in data for k in required)


def llm_judge(output: str, case: dict) -> bool:
    """Rubric-based judge. Needs ANTHROPIC_API_KEY; raises if unavailable
    so a missing key can never silently pass a case."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("llm_judge requires ANTHROPIC_API_KEY")
    import anthropic

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=os.getenv("EVAL_JUDGE_MODEL", "claude-sonnet-5-5"),
        max_tokens=200,
        messages=[{"role": "user", "content": (
            "You are a strict grader. Rubric:\n"
            f"{case['expected']}\n\nAnswer under test:\n{output}\n\n"
            'Reply JSON only: {"pass": true|false, "reason": "..."}')}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    return bool(json.loads(text[text.index("{"): text.rindex("}") + 1])["pass"])


GRADERS: dict[str, Callable[[str, dict], bool]] = {
    "exact_match": exact_match, "contains": contains, "not_contains": not_contains,
    "regex": regex, "json_valid": json_valid, "llm_judge": llm_judge,
}


def grade(output: str, case: dict) -> bool:
    name = case.get("grader", "contains")
    if name not in GRADERS:
        raise ValueError(f"Unknown grader '{name}'. Options: {sorted(GRADERS)}")
    return GRADERS[name](output, case)
