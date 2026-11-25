from evals.graders import grade
from evals.models import mock_model
from evals.report import to_markdown
from evals.runner import load_dataset, run_eval


def test_graders():
    assert grade("Paris is it", {"grader": "contains", "expected": ["paris"]})
    assert not grade("Berlin", {"grader": "contains", "expected": ["paris"]})
    assert grade(" 4 ", {"grader": "exact_match", "expected": "4"})
    assert grade('{"a": 1}', {"grader": "json_valid", "expected": ["a"]})
    assert not grade("not json", {"grader": "json_valid", "expected": []})
    assert not grade('{"a": 1}', {"grader": "json_valid", "expected": ["b"]})
    assert grade("I don't know", {"grader": "regex", "expected": "don't know"})


def test_unknown_grader_raises():
    try:
        grade("x", {"grader": "nope", "expected": ""})
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_sample_dataset_with_mock_passes_gate():
    report = run_eval(load_dataset("datasets/sample.jsonl"), mock_model, 0.8)
    assert report["total"] == 5 and report["gate_passed"]
    assert report["by_tag"]["factual"] == 1.0


def test_crashing_case_counts_as_failure():
    def boom(_): raise RuntimeError("api down")
    report = run_eval([{"id": "x", "input": "hi", "expected": ["a"]}], boom)
    assert report["passed"] == 0 and "api down" in report["results"][0]["error"]
    assert not report["gate_passed"]


def test_report_markdown_lists_failures():
    report = run_eval([{"id": "bad", "input": "2+2", "expected": ["zzz"]}], mock_model)
    md = to_markdown(report)
    assert "❌ FAIL" in md and "`bad`" in md


def test_empty_dataset_does_not_pass_gate():
    assert run_eval([], mock_model)["gate_passed"] is False
