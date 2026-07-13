from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from mathcode.environment import execute_action, reset as reset_episode

from .grader import grade


class MathCodeMiniEnv:
    """Stateful public environment for local agents and TRL GRPO."""

    def __init__(self) -> None:
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.episode_dir: Path | None = None
        self.reward = 0.0
        self.report: dict[str, Any] = {}
        self.done = False
        self._counter = 0

    def reset(self, **kwargs: Any) -> str:
        """Reset one public episode and return the task instruction."""

        self.close()
        self._temp = tempfile.TemporaryDirectory(prefix="mathcode-mini-")
        created = reset_episode(
            str(kwargs.get("task_id", "bisect_repair_v1")),
            Path(self._temp.name) / "runs",
            seed=int(kwargs.get("seed", 0)),
        )
        self.episode_dir = Path(created["episode_dir"])
        self.reward = 0.0
        self.report = {}
        self.done = False
        self._counter = 0
        return str(created["instruction"])

    def repo_tree(self) -> str:
        """List the files currently visible in the workspace."""

        return self._tool("repo_tree")

    def read_file(self, path: str) -> str:
        """Read a UTF-8 file from the workspace.

        Args:
            path: Workspace-relative file path.
        """

        return self._tool("read_file", {"path": path})

    def search_repo(self, query: str) -> str:
        """Search text in workspace files.

        Args:
            query: Non-empty text to search for.
        """

        return self._tool("search_repo", {"query": query})

    def replace_text(self, path: str, old: str, new: str, expected_replacements: int = 1) -> str:
        """Replace exact text in an editable workspace file.

        Args:
            path: Workspace-relative file path.
            old: Existing text to replace.
            new: Replacement text.
            expected_replacements: Number of exact matches required.
        """

        return self._tool(
            "replace_text",
            {"path": path, "old": old, "new": new, "expected_replacements": expected_replacements},
        )

    def write_file(self, path: str, content: str) -> str:
        """Write UTF-8 content to an editable workspace file.

        Args:
            path: Workspace-relative file path.
            content: Complete replacement file content.
        """

        return self._tool("write_file", {"path": path, "content": content})

    def run_public_tests(self, timeout_seconds: int = 60) -> str:
        """Run the protected public tests for this expired task.

        Args:
            timeout_seconds: Maximum test process duration.
        """

        return self._tool("run_public_tests", {"timeout_seconds": timeout_seconds})

    def python_run(self, code: str, timeout_seconds: int = 10) -> str:
        """Run a short Python diagnostic inside the workspace.

        Args:
            code: Python source to execute.
            timeout_seconds: Maximum process duration.
        """

        return self._tool("python_run", {"code": code, "timeout_seconds": timeout_seconds})

    def inspect_diff(self) -> str:
        """Return a unified diff from the starter workspace."""

        return self._tool("inspect_diff")

    def finish(self) -> str:
        """Finish the episode and return the public reward report."""

        if self.episode_dir is None:
            raise RuntimeError("reset must be called before finish")
        if not self.done:
            self._tool("finish")
            self.report = grade(self.episode_dir)
            self.reward = float(self.report["reward_scalar"])
            self.done = True
        return json.dumps(self.report, sort_keys=True)

    def close(self) -> None:
        if self._temp is not None:
            self._temp.cleanup()
            self._temp = None
        self.episode_dir = None

    def _tool(self, action_type: str, args: dict[str, Any] | None = None) -> str:
        if self.episode_dir is None:
            raise RuntimeError("reset must be called before using tools")
        self._counter += 1
        observation = execute_action(
            self.episode_dir,
            {"action_id": f"mini-{self._counter:04d}", "type": action_type, "args": args or {}},
        )
        return json.dumps(observation, sort_keys=True)
