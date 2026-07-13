from __future__ import annotations

from pathlib import Path
from typing import Any

from .util import PUBLIC_TASKS, load_json


REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "task_id",
    "group_id",
    "split",
    "family",
    "title",
    "horizon",
    "allowed_actions",
    "editable_paths",
    "budget",
    "verification_families",
}


def task_ids() -> list[str]:
    if not PUBLIC_TASKS.exists():
        return []
    return sorted(path.name for path in PUBLIC_TASKS.iterdir() if (path / "task.json").is_file())


def public_task_dir(task_id: str) -> Path:
    if task_id not in task_ids():
        raise KeyError(f"unknown task_id: {task_id}")
    return PUBLIC_TASKS / task_id


def load_task(task_id: str) -> dict[str, Any]:
    manifest = load_json(public_task_dir(task_id) / "task.json")
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        raise ValueError(f"task {task_id} missing manifest fields: {missing}")
    if manifest["schema_version"] != "1.0.0":
        raise ValueError(f"unsupported schema version for {task_id}")
    if manifest["task_id"] != task_id:
        raise ValueError(f"task_id mismatch in manifest for {task_id}")
    if not (public_task_dir(task_id) / "starter").is_dir():
        raise ValueError(f"starter repository missing for {task_id}")
    if not (public_task_dir(task_id) / "TASK.md").is_file():
        raise ValueError(f"TASK.md missing for {task_id}")
    return manifest


def catalog_summary() -> list[dict[str, Any]]:
    result = []
    for task_id in task_ids():
        task = load_task(task_id)
        result.append(
            {
                "task_id": task_id,
                "title": task["title"],
                "family": task["family"],
                "horizon": task["horizon"],
                "split": task["split"],
            }
        )
    return result
