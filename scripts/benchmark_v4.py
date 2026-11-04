#!/usr/bin/env python3
"""Reproduce selected local v3-to-v4 control differences in isolated processes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
EXPECTED_BASELINE_SHA256 = "048b48ce4e5379af0b1e1502b24b7469086b331aa8eb0c291fc0fe3c50b14deb"


CASES = {
    "query_dimension_fairness": {
        "question": "Synthetic evaluation question",
        "coverage": ["cost", "access", "safety"],
        "max_queries": 3,
    },
    "untraced_origin_lineage": {
        "required": ["effect"],
        "observations": [
            {"dimension": "effect", "source_id": "S1"},
            {"dimension": "effect", "source_id": "S2"},
        ],
    },
    "duplicate_evaluation_result_ids": {
        "cases": [{"id": "C1", "expected": "yes"}],
        "results": [{"id": "C1", "answer": "no"}, {"id": "C1", "answer": "yes"}],
    },
    "duplicate_json_keys": {"content": '{"status":"ok","status":"accepted"}'},
    "healthy_queries": {"question": "Synthetic", "coverage": ["cost", "access", "safety"], "max_queries": 9},
    "healthy_evaluation": {"cases": [{"id": "C1", "expected": "yes"}],
                           "results": [{"id": "C1", "answer": "yes"}]},
    "healthy_json": {"content": '{"status":"ok"}'},
    "healthy_provider": {"response": {"results": [{"id": "https://openalex.org/W1",
                                                   "title": "Synthetic fixture",
                                                   "publication_year": 2024}]}},
    "malformed_provider": {"response": {}},
}
CASE_SOURCE = {
    "query_dimension_fairness": "atlas/retrieval.py",
    "untraced_origin_lineage": "atlas/retrieval.py",
    "duplicate_evaluation_result_ids": "atlas/evaluation.py",
    "duplicate_json_keys": "atlas/ingest.py",
    "healthy_queries": "atlas/retrieval.py",
    "healthy_evaluation": "atlas/evaluation.py",
    "healthy_json": "atlas/ingest.py",
    "healthy_provider": "atlas/adapters.py",
    "malformed_provider": "atlas/adapters.py",
}


def _worker(tree, case_name, scratch):
    sys.path.insert(0, str(tree))
    case = CASES[case_name]
    try:
        if case_name in {"query_dimension_fairness", "healthy_queries"}:
            from atlas.retrieval import expand_queries
            rows = expand_queries(case["question"], case["coverage"], max_queries=case["max_queries"])
            result = {"accepted": True, "dimensions": list(dict.fromkeys(x["dimension"] for x in rows)),
                      "query_count": len(rows)}
        elif case_name == "untraced_origin_lineage":
            from atlas.retrieval import coverage_audit
            row = coverage_audit(case["required"], case["observations"])["dimensions"][0]
            result = {"accepted": True, "distinct_origin_count": row["distinct_origin_count"],
                      "status": row["status"], "untraced_source_ids": row.get("untraced_source_ids", [])}
        elif case_name in {"duplicate_evaluation_result_ids", "healthy_evaluation"}:
            from atlas.evaluation import evaluate_cases
            value = evaluate_cases(case["cases"], case["results"])
            result = {"accepted": True, "correct": value.get("accuracy_over_all") == 1,
                      "accuracy_over_all": value.get("accuracy_over_all")}
        elif case_name in {"healthy_provider", "malformed_provider"}:
            from unittest.mock import patch
            from atlas.adapters import search
            with patch("atlas.adapters.http_json", return_value=case["response"]):
                value = search("openalex", "Synthetic", limit=1)
            result = {"accepted": True, "total_returned": value["total_returned"],
                      "titles": [row["title"] for row in value["items"]]}
        else:
            from atlas.ingest import ingest
            path = Path(scratch) / "duplicate-keys.json"
            path.write_text(case["content"], encoding="utf-8")
            value = ingest(path)
            result = {"accepted": True, "parsed_status": json.loads(value["text"])["status"]}
    except Exception as error:
        result = {"accepted": False, "error_type": type(error).__name__, "error": str(error)}
    print(json.dumps(result, sort_keys=True))


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(tree):
    text = (Path(tree) / "atlas/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.M)
    if not match:
        raise RuntimeError("Cannot determine implementation version")
    return match.group(1)


def _run(tree, case, scratch):
    process = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker", str(tree), case, str(scratch)],
        cwd=tree, text=True, capture_output=True, timeout=30,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if process.returncode:
        raise RuntimeError(f"Benchmark worker failed ({case}): {process.stderr}")
    return json.loads(process.stdout)


def run(output=None):
    from atlas.archive import extract_checked
    from atlas.io import AtlasError, atomic_json, read_json

    baseline = ROOT / "reference/ATLAS_Copilot_v3_baseline.zip"
    audit = read_json(ROOT / "reports/FILE_AUDIT_V4.json")
    if audit.get("baseline_sha256") != EXPECTED_BASELINE_SHA256 or _sha(baseline) != EXPECTED_BASELINE_SHA256:
        raise AtlasError("Supplied v3 baseline hash does not match the audited archive")
    scratch = ROOT / (".benchmark-v4-" + uuid.uuid4().hex)
    scratch.mkdir()
    try:
        import zipfile
        with zipfile.ZipFile(baseline) as archive:
            extract_checked(archive, scratch / "baseline")
        baseline_root = scratch / "baseline/research_1-main"
        if not (baseline_root / "atlas/__init__.py").is_file():
            raise AtlasError("Supplied baseline has no expected repository root")
        baseline_version = _version(baseline_root)
        current_version = _version(ROOT)
        rows = []
        expected = {
            "query_dimension_fairness": lambda old, new: len(old["dimensions"]) == 1 and
                set(new["dimensions"]) == set(CASES["query_dimension_fairness"]["coverage"]),
            "untraced_origin_lineage": lambda old, new: old["distinct_origin_count"] == 2 and
                new["distinct_origin_count"] == 0 and new["status"] == "untraced",
            "duplicate_evaluation_result_ids": lambda old, new: old["accepted"] and
                not new["accepted"] and new.get("error_type") == "AtlasError",
            "duplicate_json_keys": lambda old, new: old["accepted"] and
                not new["accepted"] and new.get("error_type") == "AtlasError",
            "healthy_queries": lambda old, new: old == new == {
                "accepted": True, "dimensions": ["cost", "access", "safety"], "query_count": 9},
            "healthy_evaluation": lambda old, new: old == new == {
                "accepted": True, "correct": True, "accuracy_over_all": 1.0},
            "healthy_json": lambda old, new: old == new == {"accepted": True, "parsed_status": "ok"},
            "healthy_provider": lambda old, new: old == new == {
                "accepted": True, "total_returned": 1, "titles": ["Synthetic fixture"]},
            "malformed_provider": lambda old, new: old == {
                "accepted": True, "total_returned": 0, "titles": []} and
                not new["accepted"] and new.get("error_type") == "AtlasError",
        }
        for name in CASES:
            old = _run(baseline_root, name, scratch)
            new = _run(ROOT, name, scratch)
            rows.append({
                "case": name, "fixture": CASES[name],
                "baseline_v3": old, "current_v4": new,
                "expectation": {
                    "query_dimension_fairness": "v3 covers 1 dimension; v4 covers exactly cost/access/safety within 3 queries.",
                    "untraced_origin_lineage": "v3 counts 2 origins; v4 counts 0, status untraced.",
                    "duplicate_evaluation_result_ids": "v3 accepts duplicate results; v4 raises exactly AtlasError.",
                    "duplicate_json_keys": "v3 accepts duplicate JSON keys; v4 raises exactly AtlasError.",
                    "healthy_queries": "Both accept 9 queries covering exactly cost/access/safety.",
                    "healthy_evaluation": "Both accept unique correct answer with accuracy_over_all exactly 1.",
                    "healthy_json": "Both accept unique JSON key and preserve status exactly ok.",
                    "healthy_provider": "Both return exactly one metadata item titled Synthetic fixture.",
                    "malformed_provider": "v3 accepts {} as zero results; v4 raises exactly AtlasError.",
                }[name],
                "execution": {
                    "baseline_version": baseline_version, "current_version": current_version,
                    "interpreter": sys.executable, "python": sys.version,
                    "baseline_source_sha256": _sha(baseline_root / CASE_SOURCE[name]),
                    "current_source_sha256": _sha(ROOT / CASE_SOURCE[name]),
                },
                "expectation_met": bool(expected[name](old, new)),
            })
        report = {
            "schema_version": 1,
            "scope": "Nine selected deterministic local defect and healthy control cases, not a representative sample, accuracy estimate, or research-superiority claim.",
            "python": sys.version,
            "interpreter_executable": sys.executable,
            "baseline": {"version": baseline_version, "archive": "reference/ATLAS_Copilot_v3_baseline.zip",
                         "sha256": _sha(baseline)},
            "current": {"version": current_version,
                        "source_sha256": {p: _sha(ROOT / p) for p in
                                          ["atlas/retrieval.py", "atlas/evaluation.py", "atlas/ingest.py"]}},
            "results": rows,
            "all_expectations_met": all(row["expectation_met"] for row in rows),
        }
        destination = Path(output) if output else ROOT / "reports/v4_comparison.json"
        atomic_json(destination, report)
        return report
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", nargs=3, metavar=("TREE", "CASE", "SCRATCH"))
    args = parser.parse_args()
    if args.worker:
        _worker(*args.worker)
        return 0
    report = run(args.output)
    print(json.dumps({"cases": len(report["results"]),
                      "all_expectations_met": report["all_expectations_met"]}, indent=2))
    return 0 if report["all_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
