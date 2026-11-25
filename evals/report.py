from __future__ import annotations


def to_markdown(report: dict, title: str = "Eval report") -> str:
    status = "✅ PASS" if report["gate_passed"] else "❌ FAIL"
    lines = [
        f"# {title}", "",
        f"**Gate:** {status} (pass rate {report['pass_rate']:.0%}, threshold {report['threshold']:.0%})",
        f"**Cases:** {report['passed']}/{report['total']} passed", "",
        "## By tag", "", "| Tag | Pass rate |", "|---|---|",
    ]
    lines += [f"| {t} | {r:.0%} |" for t, r in sorted(report["by_tag"].items())]
    failures = [r for r in report["results"] if not r["passed"]]
    if failures:
        lines += ["", "## Failures", ""]
        for r in failures:
            why = r["error"] or f"output: {r['output'][:120]!r}"
            lines.append(f"- `{r['id']}` ({r['grader']}): {why}")
    return "\n".join(lines) + "\n"
