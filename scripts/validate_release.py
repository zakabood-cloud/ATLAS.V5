#!/usr/bin/env python3
"""Reproducible local release gate. It makes no network or paid API calls."""
import hashlib
import io
import json
import os
import platform
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas import __version__
from atlas.archive import extract_checked
from atlas.io import AtlasError, atomic_json, file_hash, now, read_json
from atlas.quant import run_analysis
from atlas.structure import check
from scripts.release_common import input_inventory

EXPECTED_BASELINE_SHA256 = "048b48ce4e5379af0b1e1502b24b7469086b331aa8eb0c291fc0fe3c50b14deb"


class RecordedResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.started = time.perf_counter()

    def addSuccess(self, test):
        super().addSuccess(test)
        RECORDS.append({"test": test.id(), "status": "passed",
                        "seconds": time.perf_counter() - self.started})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        RECORDS.append({"test": test.id(), "status": "failed",
                        "detail": self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        RECORDS.append({"test": test.id(), "status": "error",
                        "detail": self._exc_info_to_string(err, test)})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        RECORDS.append({"test": test.id(), "status": "skipped", "reason": reason})


def _baseline_audit():
    audit = read_json(ROOT / "reports/FILE_AUDIT_V4.json")
    archive_path = ROOT / audit["baseline_archive"]
    if file_hash(archive_path) != EXPECTED_BASELINE_SHA256 or audit.get("baseline_sha256") != EXPECTED_BASELINE_SHA256:
        raise AtlasError("Supplied v3 baseline archive hash mismatch")
    by_path = {}
    with zipfile.ZipFile(archive_path) as archive:
        scratch = ROOT / (".release-audit-" + uuid.uuid4().hex)
        try:
            extract_checked(archive, scratch)
            for path in scratch.rglob("*"):
                if path.is_file():
                    by_path[path.relative_to(scratch).as_posix()] = (path.stat().st_size, file_hash(path))
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    original_path = ROOT / "reference/ORIGINAL_ATLAS_UNMODIFIED.zip"
    original_manifest = read_json(ROOT / "reference/original_manifest.json")
    if file_hash(original_path) != original_manifest["archive_sha256"]:
        raise AtlasError("Immutable embedded historical ZIP hash mismatch")
    # Reconcile original v4 release-file hashes against the immutable v4 ZIP,
    # never against intentionally modified v5 paths. Do not falsify historical
    # original-v4 audit receipts after making improvements.
    v4_archive = ROOT / "reference/ATLAS_v4.0.0_user_supplied_original.zip"
    v4_rows = {}
    with zipfile.ZipFile(v4_archive) as v4:
        for info in v4.infolist():
            if not info.is_dir():
                v4_rows[info.filename] = hashlib.sha256(v4.read(info)).hexdigest()
    with zipfile.ZipFile(original_path) as original:
        original_files = {info.filename: info for info in original.infolist() if not info.is_dir()}
    rows = audit.get("records")
    if not isinstance(rows, list) or len(rows) != 147:
        raise AtlasError("Expected complete 147-row ATLAS v4 audit inventory")
    checked_supplied = checked_embedded = 0
    seen = set()
    for row in rows:
        name, expected = row.get("path"), (row.get("bytes"), row.get("sha256"))
        if name in seen:
            raise AtlasError("Duplicate baseline audit row: " + name)
        seen.add(name)
        if row.get("scope") == "supplied_repository":
            member = "research_1-main/" + name
            data = by_path.get(member)
            checked_supplied += 1
            if row.get("release_sha256") is not None:
                if v4_rows.get("ATLAS/" + name) != row["release_sha256"]:
                    raise AtlasError("Supplied immutable v4 release hash mismatch: " + name)
        elif row.get("scope") == "embedded_historical_reference":
            try:
                member = name.split("!/", 1)[1]
            except (AttributeError, IndexError):
                raise AtlasError("Malformed embedded historical audit path")
            info = original_files.get(member)
            with zipfile.ZipFile(original_path) as original:
                data = (info.file_size, hashlib.sha256(original.read(info)).hexdigest()) if info else None
            checked_embedded += 1
        else:
            raise AtlasError("Unknown audit record scope")
        if data != expected:
            raise AtlasError("Baseline audit mismatch for " + str(name))
        if not row.get("implementation_status") or not row.get("release_action"):
            raise AtlasError("Audit row lacks final implementation_status/release_action: " + name)
    if checked_supplied != 107 or checked_embedded != 40:
        raise AtlasError("Baseline audit scope counts are incomplete")
    return {"files": len(rows), "supplied_repository_files": checked_supplied,
            "embedded_historical_files": checked_embedded, "all_hashes_match": True, "v4_release_hashes_validated_against_immutable_zip": True, "current_v5_files_compared_to_v4": False}


def _scratch():
    path = ROOT / (".release-validation-" + uuid.uuid4().hex)
    path.mkdir()
    return path


def run():
    RECORDS.clear()
    started_at = now()
    began = time.perf_counter()
    structure = check(ROOT)
    scratch = _scratch()
    previous_tempdir = tempfile.tempdir
    previous_tmpdir = os.environ.get("TMPDIR")
    os.environ["TMPDIR"] = str(scratch)
    tempfile.tempdir = str(scratch)
    test_stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=test_stream, verbosity=2,
                                    resultclass=RecordedResult).run(suite)
    (ROOT / "reports/unittest.log").write_text(test_stream.getvalue(), encoding="utf-8")

    try:
        demo_root = scratch / "demo"
        demo_root.mkdir()
        shutil.copytree(ROOT / "methods", demo_root / "methods")
        from atlas.demo import complete
        project = complete(demo_root)
        demo = project.validate()
        demo["final_state"] = project.status()["state"]

        examples = []
        example_files = sorted((ROOT / "examples").glob("*.json"))
        for path in example_files:
            output = run_analysis(read_json(path))
            examples.append({"input": path.name, "kind": output["kind"],
                             "input_sha256": output["input_sha256"], "status": "executed"})

        comparison_path = ROOT / "reports/v4_comparison.json"
        comparison = subprocess.run(
            [sys.executable, str(ROOT / "scripts/benchmark_v4.py"), "--output", str(comparison_path)],
            cwd=ROOT, text=True, capture_output=True, timeout=180,
        )
        comparison_data = read_json(comparison_path) if comparison.returncode == 0 else {"results": []}
        historical_path = ROOT / "reports/paired_controls.json"
        historical = subprocess.run(
            [sys.executable, str(ROOT / "scripts/benchmark_controls.py"), str(historical_path)],
            cwd=ROOT, text=True, capture_output=True, timeout=300,
        )
        historical_data = read_json(historical_path) if historical.returncode == 0 else {"results": []}
        audit = _baseline_audit()
        inputs = input_inventory(ROOT)
        passed = (
            structure["ok"] and result.wasSuccessful() and result.testsRun > 0 and not result.skipped
            and demo["final_state"] == "COMPLETE" and demo["evidence"]["ok"]
            and len(examples) == 10 and comparison.returncode == 0
            and comparison_data.get("all_expectations_met") is True
            and historical.returncode == 0 and historical_data.get("all_upgraded_expected") is True
            and audit["all_hashes_match"]
        )
        cases = RECORDS[:]
        report = {
            "schema_version": 1, "version": __version__, "started_at": started_at,
            "finished_at": now(), "seconds": time.perf_counter() - began,
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "sqlite": sqlite3.sqlite_version, "copilot_runtime_executed": False,
                            "network_calls": 0, "paid_api_calls": 0},
            "structure": structure,
            "tests": {"run": result.testsRun, "passed": sum(c["status"] == "passed" for c in cases),
                      "failures": len(result.failures), "errors": len(result.errors),
                      "skipped": len(result.skipped), "cases": cases},
            "synthetic_lifecycle": demo, "example_calculations": examples,
            "v3_v4_comparison": {
                "exit_code": comparison.returncode, "cases": len(comparison_data.get("results", [])),
                "all_expectations_met": comparison_data.get("all_expectations_met", False),
                "results": comparison_data.get("results", []),
                "stdout": comparison.stdout, "stderr": comparison.stderr,
            },
            "baseline_audit": audit,
            "historical_prototype_comparison": {
                "baseline": "Immutable historical Claude prototype, not supplied Copilot v3",
                "exit_code": historical.returncode,
                "cases": len(historical_data.get("results", [])),
                "all_expected": historical_data.get("all_upgraded_expected", False),
                "stdout": historical.stdout, "stderr": historical.stderr,
            },
            "validated_inputs": inputs,
            "local_release_gate_passed": bool(passed),
            "release_status": "QUALIFIED_LOCAL_RELEASE" if passed else "BLOCKED",
            "unresolved": [
                "Live Copilot compatibility and interaction behavior",
                "Authenticated provider/MCP runtime tests",
                "Independent post-implementation expert audit",
                "Blinded equal-resource research-quality evaluation",
                "Model-facing prompt-injection resistance",
                "Other operating systems and Python versions",
            ],
        }
        atomic_json(ROOT / "reports/test_results.json", report)
        text = f"""# Observed local release checks

ATLAS {__version__}. Run finished {report['finished_at']}. Tests: {report['tests']['passed']}/{report['tests']['run']} passed; {report['tests']['failures']} failed, {report['tests']['errors']} errors, {report['tests']['skipped']} skipped. Local status: **{report['release_status']}**.

The local gate executed the static structure check, the discovered test suite, the synthetic lifecycle, all {len(examples)} example calculations, the supplied-v3 paired controls, and a hash comparison of all {audit['files']} audited baseline files. This is not a research-quality or factual-accuracy score. No Copilot runtime, network request, model/provider, or paid API was used by the gate.

See [machine-readable results](test_results.json), [test log](unittest.log), and [upgrade comparison](v4_comparison.json). Packaging and independent ZIP extraction are separate steps. Unresolved: live Copilot behavior, authenticated integrations, independent post-implementation review, blinded research-quality evaluation, model-facing injection resistance, and other operating systems/Python versions.

Reproduce with `python3 scripts/validate_release.py`; run the local demo with `python3 scripts/demo.py`. These checks do not establish that sources support research claims or that real-world findings are correct.
"""
        (ROOT / "reports/TESTING.md").write_text(text, encoding="utf-8")
        print(json.dumps({"release_status": report["release_status"], "tests": result.testsRun,
                          "passed": report["tests"]["passed"], "comparison_cases": len(comparison_data.get("results", [])),
                          "audited_files": audit["files"], "examples": len(examples)}, indent=2))
        return 0 if passed else 1
    finally:
        tempfile.tempdir = previous_tempdir
        if previous_tmpdir is None:
            os.environ.pop("TMPDIR", None)
        else:
            os.environ["TMPDIR"] = previous_tmpdir
        shutil.rmtree(scratch, ignore_errors=True)


RECORDS = []


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except Exception as error:
        atomic_json(ROOT / "reports/test_results.json", {
            "version": __version__, "finished_at": now(),
            "local_release_gate_passed": False, "release_status": "BLOCKED",
            "error_type": type(error).__name__, "error": str(error),
            "tests": {"cases": RECORDS[:]},
        })
        raise
