from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


_PACKAGE_DIR = Path(__file__).resolve().parent
_SOURCE_ROOT = next(
    (
        ancestor
        for ancestor in _PACKAGE_DIR.parents
        if (ancestor / "catalog" / "private").is_dir()
    ),
    _PACKAGE_DIR.parent,
)
_BUNDLED_ROOT = Path(__file__).resolve().parent / "data"
# Editable/source installs use the operator checkout when it is present. A
# wheel install has only the public package data under mathcode/data.
PACKAGE_ROOT = (
    _SOURCE_ROOT
    if (_SOURCE_ROOT / "catalog" / "private").is_dir()
    else (_BUNDLED_ROOT if _BUNDLED_ROOT.is_dir() else _SOURCE_ROOT)
)
PUBLIC_TASKS = PACKAGE_ROOT / "catalog" / "public" / "tasks"

IGNORED_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".DS_Store"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if not path.is_file():
            continue
        if any(part in IGNORED_NAMES for part in path.parts):
            continue
        if path.suffix in IGNORED_SUFFIXES:
            continue
        yield path


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in iter_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return "sha256:" + digest.hexdigest()


def safe_path(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("path must be a non-empty string")
    candidate_input = Path(relative)
    if candidate_input.is_absolute() or ".." in candidate_input.parts:
        raise ValueError("absolute paths and '..' are forbidden")
    root_resolved = root.resolve()
    candidate = (root / candidate_input).resolve(strict=False)
    if not candidate.is_relative_to(root_resolved):
        raise ValueError("path escapes the workspace")
    if must_exist and not candidate.exists():
        raise ValueError(f"path does not exist: {relative}")
    return candidate


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(value) + "\n")


def truncate(text: str, limit: int = 20000) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    marker = f"\n... [truncated {len(text) - limit} characters]"
    return text[: max(0, limit - len(marker))] + marker, True
