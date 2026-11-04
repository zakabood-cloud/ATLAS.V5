"""Explicit release payload selection and validated-input inventory checks."""
from pathlib import Path
import hashlib

from atlas.archive import manifest_index, safe_name
from atlas.io import AtlasError

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIRS = (".claude", ".github", "atlas", "benchmarks", "config", "docs", "examples", "methods", "reference", "reports", "research", "scripts", "tests")
PAYLOAD_ROOT_FILES = (".gitignore", "AGENTS.md", "CLAUDE.md", "README.md", "pyproject.toml", "memory/README.md", "projects/.gitkeep")
GENERATED_REPORTS = {
    "reports/test_results.json",
    "reports/unittest.log",
    "reports/TESTING.md",
    "reports/paired_controls.json",
    "reports/v4_comparison.json",
    "reports/package_validation.json",
}
PRIVATE_OR_EPHEMERAL_PARTS = {
    ".git", ".atlas", ".venv", "__pycache__", "build", "dist", "history",
}
PRIVATE_NAMES = {
    ".mcp.json", ".netrc", ".npmrc", "settings.local.json",
    "credentials", "credentials.json", "secrets.json", "token", "token.json", "auth.json",
}
PRIVATE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def release_files(root=ROOT, include_generated=True):
    """Return only explicit payload roots/files; reject links even when excluded."""
    root = Path(root)
    selected = []
    roots = [root / name for name in PAYLOAD_DIRS]
    for path in [root / name for name in PAYLOAD_ROOT_FILES] + roots:
        if path.is_symlink():
            raise AtlasError("Release symlink forbidden: " + path.relative_to(root).as_posix())
    for rel in PAYLOAD_ROOT_FILES:
        path = root / rel
        if path.is_file():
            selected.append(path)
    for directory in roots:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise AtlasError("Release symlink forbidden: " + relative)
            parts = set(path.relative_to(root).parts)
            if parts & PRIVATE_OR_EPHEMERAL_PARTS or path.name in PRIVATE_NAMES:
                continue
            if (path.name.startswith(".env") or path.suffix in {".pyc", ".pyo"}
                    or path.suffix.lower() in PRIVATE_SUFFIXES):
                continue
            if not include_generated and relative in GENERATED_REPORTS:
                continue
            if relative.startswith("projects/") or relative.startswith("memory/"):
                continue
            elif path.is_file():
                selected.append(path)
    return sorted(set(selected), key=lambda path: path.relative_to(root).as_posix())


def input_inventory(root=ROOT):
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in release_files(root, include_generated=False)
    }


def verify_input_inventory(expected, root=ROOT):
    """Require exact path-set and digest equality against current package inputs."""
    if not isinstance(expected, dict) or not expected:
        raise AtlasError("Validation lacks a nonempty release input inventory")
    for name in expected:
        safe_name(name)
    actual = input_inventory(root)
    if set(expected) != set(actual):
        added = sorted(set(actual) - set(expected))
        removed = sorted(set(expected) - set(actual))
        raise AtlasError(f"Release input path set changed; added={added}, removed={removed}")
    if any(not isinstance(value, dict) for value in expected.values()):
        raise AtlasError("Invalid validated release input row")
    normalized = manifest_index(
        [{"path": name, "bytes": value.get("bytes"), "sha256": value.get("sha256")}
         for name, value in expected.items()],
        size_key="bytes",
    )
    for name, row in normalized.items():
        if row["bytes"] != actual[name]["bytes"] or row["sha256"] != actual[name]["sha256"]:
            raise AtlasError("Release input changed after validation: " + name)
    return actual
