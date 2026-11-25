# ai-evals-starter-kit

A small, dependency-light harness for **evaluating LLM features like software**: versioned datasets, deterministic graders first, an optional LLM judge, and a CI gate that fails the build when quality drops.

## Features
- JSONL datasets with tags, so you see pass rate **by category** (factual, format, hallucination, ...)
- Graders: `exact_match`, `contains`, `not_contains`, `regex`, `json_valid`, `llm_judge`
- Crashes count as failures (never silently skipped); an empty dataset never passes the gate
- Markdown report plus non-zero exit code for CI
- Bring any model: a model is just `function(prompt) -> str`

## Quick start
```bash
python -m evals.cli datasets/sample.jsonl --model mock          # offline demo
ANTHROPIC_API_KEY=... python -m evals.cli datasets/sample.jsonl --model anthropic --threshold 0.9
```

## Dataset format
```json
{"id": "geo-1", "input": "What is the capital of France?", "grader": "contains", "expected": ["Paris"], "tags": ["factual"]}
```

## Good practice built in
1. Prefer cheap deterministic checks; use `llm_judge` only for subjective criteria, with a written rubric.
2. Keep a **hallucination** slice (questions the model should decline).
3. Run in CI on every prompt/model change; compare against the last passing run.
4. Grow the dataset from real failures.

## Tests
```bash
pytest -q
```
