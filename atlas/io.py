"""Strict, bounded local IO. No networking, shell execution, or pickle."""
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone


class AtlasError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def confined(root, rel, must_exist=False):
    root = Path(root).resolve()
    rel = Path(rel)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise AtlasError("Expected a nonempty relative path without parent traversal")
    p = root
    for part in rel.parts:
        p = p / part
        if p.is_symlink():
            raise AtlasError("Symlinks are not allowed in controlled artifacts")
    p = p.resolve()
    if not p.is_relative_to(root):
        raise AtlasError("Path escapes project")
    if must_exist and not p.is_file():
        raise AtlasError("Missing artifact: " + str(rel))
    return p


def parse_json(text):
    """Parse the same strict JSON contract for files and external responses."""
    if not isinstance(text, str) or len(text.encode("utf-8")) > 20_000_000:
        raise AtlasError("JSON must be text within the 20 MB safety limit")
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise AtlasError("Duplicate JSON key: " + k)
            d[k] = v
        return d
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise AtlasError("Nonfinite JSON number")
        return number
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_float=finite_float,
                          parse_constant=lambda x: (_ for _ in ()).throw(AtlasError("Nonfinite JSON number")))
    except (json.JSONDecodeError, RecursionError) as e:
        raise AtlasError("Invalid or excessively nested JSON") from e


def read_json(path):
    p = Path(path)
    if p.stat().st_size > 20_000_000:
        raise AtlasError("JSON exceeds 20 MB safety limit")
    try:
        return parse_json(p.read_text(encoding="utf-8"))
    except UnicodeError as e:
        raise AtlasError("Invalid JSON encoding: " + p.name) from e


def atomic_json(path, value):
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def atomic_text(path, body):
    if not isinstance(body, str):
        raise AtlasError("Text output must be a string")
    path = Path(path)
    if path.is_symlink():
        raise AtlasError("Refusing symlink output")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".atlas-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(body); f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def text_required(obj, key):
    if not isinstance(obj, dict) or not isinstance(obj.get(key), str) or not obj[key].strip():
        raise AtlasError("Required nonempty text: " + key)
    return obj[key]


def date(value):
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)
    except (ValueError, AttributeError, TypeError) as e:
        raise AtlasError("Invalid ISO date") from e
