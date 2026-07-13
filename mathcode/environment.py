from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from .catalog import load_task, public_task_dir
from .util import (
    PACKAGE_ROOT,
    append_jsonl,
    atomic_write_json,
    hash_tree,
    iter_files,
    load_json,
    safe_path,
    sha256_text,
    truncate,
    utc_now,
)


class EnvironmentError(RuntimeError):
    def __init__(self, message: str, code: str = "ENVIRONMENT_ERROR"):
        super().__init__(message)
        self.code = code


def _episode_paths(episode_dir: Path) -> tuple[Path, Path, Path]:
    episode_dir = episode_dir.resolve()
    return episode_dir / "workspace", episode_dir / "state.json", episode_dir / "events.jsonl"


def _load_state(episode_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    workspace, state_path, events_path = _episode_paths(episode_dir)
    if not state_path.is_file() or not workspace.is_dir():
        raise EnvironmentError("invalid episode directory", "EPISODE_NOT_FOUND")
    return load_json(state_path), workspace, events_path


def reset(
    task_id: str,
    runs_dir: Path,
    *,
    seed: int = 0,
    episode_id: str | None = None,
) -> dict[str, Any]:
    task = load_task(task_id)
    runs_dir = runs_dir.resolve()
    runs_dir.mkdir(parents=True, exist_ok=True)
    episode_id = episode_id or f"{task_id}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,96}", episode_id):
        raise EnvironmentError("invalid episode_id", "EPISODE_ID_INVALID")
    episode_dir = runs_dir / episode_id
    workspace = episode_dir / "workspace"
    episode_dir.mkdir(parents=True, exist_ok=False)
    shutil.copytree(public_task_dir(task_id) / "starter", workspace)
    shutil.copy2(public_task_dir(task_id) / "TASK.md", workspace / "TASK.md")
    shutil.copy2(PACKAGE_ROOT / "AGENTS.md", workspace / "AGENTS.md")
    public_tests = public_task_dir(task_id) / "public_tests"
    if public_tests.is_dir():
        shutil.copytree(public_tests, workspace / "tests" / "public", dirs_exist_ok=True)

    state_hash = hash_tree(workspace)
    now = utc_now()
    state = {
        "schema_version": "1.0.0",
        "episode_id": episode_id,
        "task_id": task_id,
        "seed": int(seed),
        "workspace": str(workspace),
        "initial_state_hash": state_hash,
        "state_hash": state_hash,
        "status": "active",
        "usage": {"actions": 0, "test_runs": 0, "submissions": 0},
        "action_ids": [],
        "created_at": now,
        "created_unix": time.time(),
        "updated_at": now,
    }
    atomic_write_json(episode_dir / "state.json", state)
    (episode_dir / "events.jsonl").touch()
    return {
        "episode_id": episode_id,
        "episode_dir": str(episode_dir),
        "workspace": str(workspace),
        "task_id": task_id,
        "instruction": (workspace / "TASK.md").read_text(encoding="utf-8"),
        "allowed_actions": task["allowed_actions"],
        "budget": task["budget"],
        "initial_state_hash": state_hash,
    }


def _budget_remaining(task: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {
        "actions": max(0, task["budget"]["actions"] - state["usage"]["actions"]),
        "test_runs": max(0, task["budget"]["test_runs"] - state["usage"]["test_runs"]),
        "submissions": max(0, task["budget"]["submissions"] - state["usage"]["submissions"]),
        "wall_time_seconds": max(
            0,
            int(task["budget"]["wall_time_seconds"] - (time.time() - state["created_unix"])),
        ),
    }


def _ensure_active(task: dict[str, Any], state: dict[str, Any]) -> None:
    if state["status"] != "active":
        raise EnvironmentError(f"episode status is {state['status']}", "EPISODE_NOT_ACTIVE")
    remaining = _budget_remaining(task, state)
    if remaining["actions"] <= 0:
        raise EnvironmentError("action budget exhausted", "BUDGET_ACTIONS_EXHAUSTED")
    if remaining["wall_time_seconds"] <= 0:
        raise EnvironmentError("wall-time budget exhausted", "BUDGET_TIME_EXHAUSTED")


def _is_editable(task: dict[str, Any], relative: str) -> bool:
    normalized = Path(relative).as_posix().lstrip("./")
    for prefix in task["editable_paths"]:
        clean_prefix = prefix.rstrip("/")
        if normalized == clean_prefix or normalized.startswith(clean_prefix + "/"):
            return True
    return False


def _repo_tree(workspace: Path) -> str:
    return "\n".join(path.relative_to(workspace).as_posix() for path in iter_files(workspace))


def _read_file(workspace: Path, args: dict[str, Any]) -> str:
    path = safe_path(workspace, args.get("path", ""), must_exist=True)
    if not path.is_file():
        raise EnvironmentError("read_file requires a regular file", "TOOL_INVALID_PATH")
    data = path.read_bytes()
    if len(data) > 200_000:
        raise EnvironmentError("file exceeds 200 KB read limit", "TOOL_OUTPUT_LIMIT")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EnvironmentError("binary files are not supported", "TOOL_BINARY_FILE") from exc


def _search_repo(workspace: Path, args: dict[str, Any]) -> str:
    query = args.get("query", "")
    if not isinstance(query, str) or not query:
        raise EnvironmentError("query must be a non-empty string", "TOOL_INVALID_ARGUMENT")
    if len(query) > 500:
        raise EnvironmentError("query is too long", "TOOL_INVALID_ARGUMENT")
    matches: list[str] = []
    for path in iter_files(workspace):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(lines, 1):
            if query in line:
                matches.append(f"{path.relative_to(workspace).as_posix()}:{line_number}:{line}")
                if len(matches) >= 200:
                    return "\n".join(matches) + "\n... [match limit reached]"
    return "\n".join(matches)


def _replace_text(workspace: Path, task: dict[str, Any], args: dict[str, Any]) -> str:
    relative = args.get("path", "")
    if not _is_editable(task, relative):
        raise EnvironmentError("path is not editable", "TOOL_PATH_NOT_EDITABLE")
    path = safe_path(workspace, relative, must_exist=True)
    old = args.get("old")
    new = args.get("new")
    expected = int(args.get("expected_replacements", 1))
    if not isinstance(old, str) or not isinstance(new, str) or not old:
        raise EnvironmentError("old and new must be strings and old must be non-empty", "TOOL_INVALID_ARGUMENT")
    text = path.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != expected:
        raise EnvironmentError(
            f"expected {expected} replacements but found {actual}",
            "TOOL_REPLACEMENT_COUNT_MISMATCH",
        )
    path.write_text(text.replace(old, new), encoding="utf-8")
    return f"replaced {actual} occurrence(s) in {relative}"


def _write_file(workspace: Path, task: dict[str, Any], args: dict[str, Any]) -> str:
    relative = args.get("path", "")
    content = args.get("content")
    if not _is_editable(task, relative):
        raise EnvironmentError("path is not editable", "TOOL_PATH_NOT_EDITABLE")
    if not isinstance(content, str):
        raise EnvironmentError("content must be a string", "TOOL_INVALID_ARGUMENT")
    if len(content.encode("utf-8")) > 500_000:
        raise EnvironmentError("content exceeds 500 KB", "TOOL_OUTPUT_LIMIT")
    path = safe_path(workspace, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote {len(content.encode('utf-8'))} bytes to {relative}"


def _run_process(command: list[str], workspace: Path, timeout: int) -> tuple[int, str, str]:
    env = os.environ.copy()
    src = str(workspace / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            command,
            cwd=workspace,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        raise EnvironmentError(stdout + "\n" + stderr, "TOOL_TIMED_OUT") from exc
    stdout = result.stdout.replace(str(workspace), "<WORKSPACE>")
    stderr = result.stderr.replace(str(workspace), "<WORKSPACE>")
    return result.returncode, stdout, stderr


def _run_public_tests(task_id: str, workspace: Path, args: dict[str, Any]) -> tuple[int, str, str]:
    timeout = min(120, max(1, int(args.get("timeout_seconds", 60))))
    test_dir = public_task_dir(task_id) / "public_tests"
    command = [sys.executable, "-m", "unittest", "discover", "-s", str(test_dir), "-p", "test_*.py", "-v"]
    return _run_process(command, workspace, timeout)


def _python_run(workspace: Path, args: dict[str, Any]) -> tuple[int, str, str]:
    code = args.get("code")
    if not isinstance(code, str) or not code:
        raise EnvironmentError("code must be a non-empty string", "TOOL_INVALID_ARGUMENT")
    if len(code) > 50_000:
        raise EnvironmentError("code exceeds 50 KB", "TOOL_OUTPUT_LIMIT")
    timeout = min(30, max(1, int(args.get("timeout_seconds", 10))))
    return _run_process([sys.executable, "-c", code], workspace, timeout)


def _inspect_diff(task_id: str, workspace: Path) -> str:
    starter = public_task_dir(task_id) / "starter"
    paths = set()
    for path in iter_files(starter):
        paths.add(path.relative_to(starter).as_posix())
    for path in iter_files(workspace):
        relative = path.relative_to(workspace).as_posix()
        if relative in {"TASK.md", "AGENTS.md"} or relative.startswith("tests/public/"):
            continue
        paths.add(relative)
    output: list[str] = []
    for relative in sorted(paths):
        before_path = starter / relative
        after_path = workspace / relative
        before = before_path.read_text(encoding="utf-8").splitlines(keepends=True) if before_path.is_file() else []
        after = after_path.read_text(encoding="utf-8").splitlines(keepends=True) if after_path.is_file() else []
        if before == after:
            continue
        output.extend(
            difflib.unified_diff(before, after, fromfile=f"a/{relative}", tofile=f"b/{relative}")
        )
    return "".join(output)


def execute_action(episode_dir: Path, action: dict[str, Any]) -> dict[str, Any]:
    state, workspace, events_path = _load_state(episode_dir)
    task = load_task(state["task_id"])
    _ensure_active(task, state)

    action_id = action.get("action_id")
    action_type = action.get("type")
    args = action.get("args", {})
    if not isinstance(action_id, str) or not action_id:
        raise EnvironmentError("action_id is required", "ACTION_SCHEMA_INVALID")
    if action_id in state["action_ids"]:
        raise EnvironmentError("action_id must be unique", "ACTION_ID_DUPLICATE")
    if action_type not in task["allowed_actions"]:
        raise EnvironmentError(f"action not allowed: {action_type}", "ACTION_NOT_ALLOWED")
    if not isinstance(args, dict):
        raise EnvironmentError("args must be an object", "ACTION_SCHEMA_INVALID")

    current_hash = hash_tree(workspace)
    expected_hash = action.get("expected_state_hash")
    if expected_hash is not None and expected_hash != current_hash:
        raise EnvironmentError("expected_state_hash does not match", "STATE_HASH_MISMATCH")

    started = time.monotonic()
    status = "completed"
    exit_code: int | None = None
    stdout = ""
    stderr = ""
    failure_code: str | None = None
    try:
        if action_type == "repo_tree":
            stdout = _repo_tree(workspace)
        elif action_type == "read_file":
            stdout = _read_file(workspace, args)
        elif action_type == "search_repo":
            stdout = _search_repo(workspace, args)
        elif action_type == "replace_text":
            stdout = _replace_text(workspace, task, args)
        elif action_type == "write_file":
            stdout = _write_file(workspace, task, args)
        elif action_type == "run_public_tests":
            if state["usage"]["test_runs"] >= task["budget"]["test_runs"]:
                raise EnvironmentError("public-test budget exhausted", "BUDGET_TESTS_EXHAUSTED")
            state["usage"]["test_runs"] += 1
            exit_code, stdout, stderr = _run_public_tests(state["task_id"], workspace, args)
        elif action_type == "python_run":
            exit_code, stdout, stderr = _python_run(workspace, args)
        elif action_type == "inspect_diff":
            stdout = _inspect_diff(state["task_id"], workspace)
        elif action_type == "finish":
            # Finish is a policy-visible handoff point.  It records the final
            # artifact state without invoking the private evaluator; an
            # external partner wrapper performs the authenticated score call.
            stdout = "finish requested; host scorer may evaluate the artifact"
        else:
            raise EnvironmentError(f"unsupported action: {action_type}", "ACTION_NOT_IMPLEMENTED")
    except EnvironmentError as exc:
        status = "timed_out" if exc.code == "TOOL_TIMED_OUT" else "rejected"
        stderr = str(exc)
        failure_code = exc.code
    except ValueError as exc:
        status = "rejected"
        stderr = str(exc)
        failure_code = "TOOL_INVALID_PATH"
    except Exception as exc:  # fail closed at the tool boundary
        status = "failed"
        stderr = f"{type(exc).__name__}: {exc}"
        failure_code = "TOOL_INTERNAL_ERROR"

    stdout, stdout_truncated = truncate(stdout)
    stderr, stderr_truncated = truncate(stderr)
    state_after = hash_tree(workspace)
    state["usage"]["actions"] += 1
    state["action_ids"].append(action_id)
    state["state_hash"] = state_after
    state["updated_at"] = utc_now()
    observation = {
        "observation_id": f"observation:{action_id}",
        "action_id": action_id,
        "status": status,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_hash": sha256_text(stdout),
        "stderr_hash": sha256_text(stderr),
        "truncated": stdout_truncated or stderr_truncated,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "state_before": current_hash,
        "state_after": state_after,
        "budget_remaining": _budget_remaining(task, state),
    }
    if failure_code:
        observation["failure_code"] = failure_code
    event = {
        "schema_version": "1.0.0",
        "sequence": state["usage"]["actions"],
        "event_type": "action_observation",
        "action": action,
        "observation": observation,
    }
    append_jsonl(events_path, event)
    atomic_write_json(Path(episode_dir) / "state.json", state)
    return observation


def _evidence_score(events_path: Path, evidence: dict[str, Any]) -> float:
    known = set()
    if events_path.is_file():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            event = json.loads(line)
            observation = event.get("observation", {})
            if observation.get("observation_id"):
                known.add(observation["observation_id"])
    requirements = evidence.get("requirements_completed", []) if isinstance(evidence, dict) else []
    mapping = evidence.get("evidence", {}) if isinstance(evidence, dict) else {}
    references = [ref for refs in mapping.values() if isinstance(refs, list) for ref in refs]
    if requirements and not references:
        return 0.0
    if not references:
        return 1.0
    return sum(ref in known for ref in references) / len(references)


def submit(episode_dir: Path, evidence: dict[str, Any]) -> dict[str, Any]:
    state, workspace, events_path = _load_state(episode_dir)
    task = load_task(state["task_id"])
    _ensure_active(task, state)
    if state["usage"]["submissions"] >= task["budget"]["submissions"]:
        raise EnvironmentError("submission budget exhausted", "BUDGET_SUBMISSIONS_EXHAUSTED")
    score = _evidence_score(events_path, evidence)
    from mathcode_mini.grader import grade

    report = grade(Path(episode_dir))
    state["usage"]["submissions"] += 1
    state["status"] = "submitted"
    state["state_hash"] = hash_tree(workspace)
    state["updated_at"] = utc_now()
    atomic_write_json(Path(episode_dir) / "submission.json", evidence)
    atomic_write_json(Path(episode_dir) / "reward.json", report)
    event = {
        "schema_version": "1.0.0",
        "sequence": state["usage"]["actions"] + 1,
        "event_type": "submission",
        "action": {"action_id": "submit", "type": "submit", "args": {"evidence": evidence}},
        "observation": {
            "observation_id": "observation:submit",
            "action_id": "submit",
            "status": "completed",
            "terminal_success": report["terminal_success"],
            "reward_scalar": report["reward_scalar"],
            "reward_vector": report["reward_vector"],
            "failure_codes": report["failure_codes"],
            "state_before": state["state_hash"],
            "state_after": state["state_hash"],
            "budget_remaining": _budget_remaining(task, state),
        },
    }
    append_jsonl(events_path, event)
    atomic_write_json(Path(episode_dir) / "state.json", state)
    return report


def replay(episode_dir: Path) -> dict[str, Any]:
    original_state, _, original_events_path = _load_state(episode_dir)
    events = [json.loads(line) for line in original_events_path.read_text(encoding="utf-8").splitlines() if line]
    with tempfile.TemporaryDirectory(prefix="mathcode-replay-") as tmp:
        reset_result = reset(original_state["task_id"], Path(tmp), seed=original_state.get("seed", 0))
        replay_dir = Path(reset_result["episode_dir"])
        differences: list[dict[str, Any]] = []
        replayed = 0
        for event in events:
            if event["event_type"] == "submission":
                report = submit(replay_dir, event["action"]["args"].get("evidence", {}))
                original_obs = event["observation"]
                if report["terminal_success"] != original_obs["terminal_success"] or report["reward_scalar"] != original_obs["reward_scalar"]:
                    differences.append({"sequence": event["sequence"], "field": "terminal_reward"})
                replayed += 1
                continue
            action = dict(event["action"])
            action.pop("expected_state_hash", None)
            observed = execute_action(replay_dir, action)
            expected = event["observation"]
            for field in ("status", "exit_code", "stdout_hash", "stderr_hash", "state_after", "failure_code"):
                if observed.get(field) != expected.get(field):
                    differences.append(
                        {
                            "sequence": event["sequence"],
                            "field": field,
                            "expected": expected.get(field),
                            "observed": observed.get(field),
                        }
                    )
            replayed += 1
        result = {
            "episode_id": original_state["episode_id"],
            "replayed_events": replayed,
            "replay_agreed": not differences,
            "differences": differences,
        }
        atomic_write_json(Path(episode_dir) / "replay.json", result)
        return result
