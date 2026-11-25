"""python -m evals.cli datasets/sample.jsonl --model mock|anthropic [--threshold 0.8]"""
from __future__ import annotations

import argparse
import json
import sys

from .models import anthropic_model, mock_model
from .report import to_markdown
from .runner import load_dataset, run_eval


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run an eval dataset against a model")
    ap.add_argument("dataset")
    ap.add_argument("--model", choices=["mock", "anthropic"], default="mock")
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--json-out", help="write the full JSON report here")
    args = ap.parse_args(argv)

    model_fn = mock_model if args.model == "mock" else anthropic_model()
    report = run_eval(load_dataset(args.dataset), model_fn, args.threshold)
    print(to_markdown(report))
    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(report, f, indent=2)
    return 0 if report["gate_passed"] else 1   # non-zero exit fails CI


if __name__ == "__main__":
    sys.exit(main())
