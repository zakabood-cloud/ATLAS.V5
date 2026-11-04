#!/usr/bin/env python3
"""Build a deterministic, allowlisted v4 ZIP and test two fresh extractions."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.archive import checked_members, extract_checked, manifest_index, safe_name
from atlas import __version__
from atlas.io import AtlasError, atomic_json, file_hash, now, read_json
from scripts.release_common import release_files, sha256, verify_input_inventory


def _file_rows(root):
    rows = [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
             "sha256": sha256(path)}
            for path in release_files(root)
            if path.relative_to(root).as_posix() != "release_manifest.json"]
    manifest_index(rows, size_key="bytes")
    return rows


def write_manifest(root):
    rows = _file_rows(root)
    atomic_json(root / "release_manifest.json", {
        "schema_version": 1, "hash_algorithm": "SHA-256",
        "scope": "All allowlisted package files except this self-referential manifest",
        "files": rows,
    })
    return rows


def make_zip(root, destination):
    destination = Path(destination)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        paths = release_files(root)
        if (Path(root) / "release_manifest.json").is_file():
            paths.append(Path(root) / "release_manifest.json")
        for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
            name = "ATLAS/" + path.relative_to(root).as_posix()
            safe_name(name)
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            archive.writestr(info, path.read_bytes())


def verify_zip(archive_path, destination):
    destination = Path(destination)
    if destination.exists():
        raise AtlasError("Verification extraction path must be fresh")
    with zipfile.ZipFile(archive_path) as archive:
        infos = checked_members(archive)
        actual_names = {info.filename for info in infos}
        if any(not name.startswith("ATLAS/") for name in actual_names):
            raise AtlasError("Unexpected archive root")
        extract_checked(archive, destination)
    root = destination / "ATLAS"
    manifest = read_json(root / "release_manifest.json")
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1
            or manifest.get("hash_algorithm") != "SHA-256"):
        raise AtlasError("Invalid release manifest header")
    expected = manifest_index(manifest.get("files"), size_key="bytes")
    expected_names = {"ATLAS/" + name for name in expected} | {"ATLAS/release_manifest.json"}
    if actual_names != expected_names:
        raise AtlasError("Raw ZIP member set does not exactly match the release manifest")
    actual = {
        path.relative_to(root).as_posix(): (path.stat().st_size, sha256(path))
        for path in root.rglob("*") if path.is_file()
        and path.relative_to(root).as_posix() != "release_manifest.json"
    }
    if set(expected) != set(actual):
        raise AtlasError("Release manifest path set mismatch")
    for name, row in expected.items():
        if actual[name] != (row["bytes"], row["sha256"]):
            raise AtlasError("Release manifest digest mismatch: " + name)

    original = read_json(root / "reference/original_manifest.json")
    if file_hash(root / "reference/ORIGINAL_ATLAS_UNMODIFIED.zip") != original["archive_sha256"]:
        raise AtlasError("Immutable original archive was not preserved")
    commands = []
    local_temp = destination / ".local-test-tmp"
    local_temp.mkdir(parents=True, exist_ok=True)
    test_env = {**os.environ, "TMPDIR": str(local_temp)}
    for command in (
        [sys.executable, "-m", "atlas", "check"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        [sys.executable, "scripts/demo.py"],
    ):
        result = subprocess.run(command, cwd=root, text=True, capture_output=True,
                                timeout=180, env=test_env)
        commands.append({"command": command[1:], "exit_code": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise AtlasError("Extracted release check failed: " + repr(commands[-1]))
    shutil.rmtree(local_temp, ignore_errors=True)
    return {"files": len(expected) + 1, "manifest_matches": True,
            "original_archive_preserved": True, "commands": commands}


def _copy_payload(source, destination):
    for path in release_files(source):
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def package(output, overwrite=False):
    report = read_json(ROOT / "reports/test_results.json")
    metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    versions = re.findall(r'^version\s*=\s*"([^"]+)"\s*$', metadata, re.M)
    if len(versions) != 1:
        raise AtlasError("Cannot determine unique package version")
    package_version = versions[0]
    if report.get("version") != package_version:
        raise AtlasError("Validation report version does not match package metadata")
    if not report.get("local_release_gate_passed"):
        raise AtlasError("Run and pass scripts/validate_release.py first")
    validated = report.get("validated_inputs")
    verify_input_inventory(validated, ROOT)

    output = Path(output).expanduser()
    if output.is_symlink():
        raise AtlasError("Refusing to replace a symlink destination")
    output = output.resolve()
    if output.exists() and not overwrite:
        raise AtlasError("Destination exists; pass --overwrite to replace it explicitly")
    try:
        relative_output = output.relative_to(ROOT).as_posix()
    except ValueError:
        relative_output = ""
    if relative_output and (relative_output.split("/", 1)[0] in {
        ".github", "atlas", "benchmarks", "config", "docs", "examples", "methods",
        "reference", "reports", "research", "scripts", "tests", "memory", "projects",
    }):
        raise AtlasError("Archive destination must be outside release payload inputs")
    output.parent.mkdir(parents=True, exist_ok=True)
    scratch = ROOT / (".release-package-" + uuid.uuid4().hex)
    scratch.mkdir()
    staged_output = output.parent / ("." + output.name + ".staged-" + uuid.uuid4().hex)
    try:
        stage = scratch / "stage"
        stage.mkdir()
        _copy_payload(ROOT, stage)
        write_manifest(stage)
        candidate = scratch / "candidate.zip"
        make_zip(stage, candidate)
        candidate_result = verify_zip(candidate, scratch / "candidate-extract")

        receipt = {
            "validated_at": now(),
            "candidate_validation": candidate_result,
            "final_archive_independently_extracted": True,
            "limitations": ["No live Copilot or optional API execution",
                            "Integrity hashes are not digital signatures"],
        }
        atomic_json(stage / "reports/package_validation.json", receipt)
        write_manifest(stage)
        make_zip(stage, staged_output)
        final_result = verify_zip(staged_output, scratch / "final-extract")
        verify_input_inventory(validated, ROOT)

        if overwrite:
            os.replace(staged_output, output)
        else:
            try:
                os.link(staged_output, output)
            except FileExistsError as error:
                raise AtlasError("Destination appeared during packaging; refusing overwrite") from error
            staged_output.unlink()
        final_receipt = {
            "at": now(), "archive": str(output), "sha256": file_hash(output),
            "bytes": output.stat().st_size, "final_extraction": final_result,
        }
        atomic_json(ROOT.parent / "final_package_receipt.json", final_receipt)
        atomic_json(ROOT / "reports/package_validation.json", receipt)
        shutil.copyfile(stage / "release_manifest.json", ROOT / "release_manifest.json")
        return {"archive": str(output), "sha256": final_receipt["sha256"],
                "bytes": final_receipt["bytes"], "files": final_result["files"],
                "independent_extractions": 2, "checks_passed": True}
    finally:
        if staged_output.exists():
            staged_output.unlink()
        shutil.rmtree(scratch, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / f"releases/ATLAS_Research_OS_v{__version__}_Copilot.zip")
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace an existing destination after all checks pass")
    args = parser.parse_args()
    print(json.dumps(package(args.output, args.overwrite), indent=2))


if __name__ == "__main__":
    main()
