from __future__ import annotations

from pathlib import Path


REFERENCE = Path(__file__).resolve().parent.parent / "examples" / "reference_solution.py"


def apply_scripted_baseline(workspace: Path) -> None:
    target = Path(workspace) / "src" / "rootkit" / "bisect.py"
    target.write_text(REFERENCE.read_text(encoding="utf-8"), encoding="utf-8")
