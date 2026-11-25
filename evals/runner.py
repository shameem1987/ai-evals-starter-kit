"""Run a dataset through any `model_fn(prompt) -> str` and grade the results."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .graders import grade


def load_dataset(path: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def run_eval(dataset: list[dict], model_fn: Callable[[str], str], pass_threshold: float = 0.8) -> dict:
    results = []
    for case in dataset:
        t0 = time.perf_counter()
        try:
            output = model_fn(case["input"])
            passed, error = grade(output, case), None
        except Exception as e:  # a crashing case is a failing case, never a skipped one
            output, passed, error = "", False, f"{type(e).__name__}: {e}"
        results.append({
            "id": case["id"], "tags": case.get("tags", []), "grader": case.get("grader", "contains"),
            "passed": passed, "output": output, "error": error,
            "latency_s": round(time.perf_counter() - t0, 3),
        })
    total = len(results)
    passed = sum(r["passed"] for r in results)
    by_tag: dict[str, list[bool]] = {}
    for r in results:
        for t in r["tags"] or ["untagged"]:
            by_tag.setdefault(t, []).append(r["passed"])
    return {
        "total": total, "passed": passed,
        "pass_rate": round(passed / total, 3) if total else 0.0,
        "gate_passed": total > 0 and passed / total >= pass_threshold,
        "threshold": pass_threshold,
        "by_tag": {t: round(sum(v) / len(v), 3) for t, v in by_tag.items()},
        "results": results,
    }
