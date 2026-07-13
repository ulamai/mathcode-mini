from __future__ import annotations

import importlib.util
import math
import numbers
import sys
from pathlib import Path
from typing import Any


def _load_candidate(workspace: Path) -> Any:
    path = workspace / "src" / "rootkit" / "bisect.py"
    spec = importlib.util.spec_from_file_location("mathcode_mini_candidate", path)
    if spec is None or spec.loader is None:
        raise ImportError("candidate module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    source = str(workspace / "src")
    sys.path.insert(0, source)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(source)
    return module


def _check(checks: list[dict[str, Any]], name: str, family: str, passed: bool) -> None:
    checks.append({"name": name, "family": family, "passed": bool(passed)})


def grade(episode_dir: Path) -> dict[str, Any]:
    """Grade the expired public task using only public contract checks."""

    workspace = Path(episode_dir) / "workspace"
    checks: list[dict[str, Any]] = []
    try:
        module = _load_candidate(workspace)
        required = ["BisectionResult", "InvalidBracketError", "ConvergenceError", "bisect"]
        api_ok = all(hasattr(module, name) for name in required)
    except Exception:
        _check(checks, "import-and-api", "semantic", False)
        return _report(checks)
    _check(checks, "import-and-api", "semantic", api_ok)
    if not api_ok:
        return _report(checks)

    try:
        result = module.bisect(lambda x: x * x - 2.0, 0.0, 2.0, x_tolerance=1e-10)
        certificate_ok = (
            result.lower <= result.x <= result.upper
            and abs((result.x * result.x - 2.0) - result.fx) <= 1e-15
            and (
                result.fx == 0.0
                or (
                    result.f_lower * result.f_upper <= 0
                    and max(result.x - result.lower, result.upper - result.x) <= 1.0001e-10
                )
            )
            and abs(result.x - math.sqrt(2.0)) <= 2e-10
        )
    except Exception:
        certificate_ok = False
    _check(checks, "certificate-relation", "semantic", certificate_ok)

    try:
        left = module.bisect(lambda x: x - 2.0, 2.0, 5.0)
        right = module.bisect(lambda x: x - 5.0, 2.0, 5.0)
        endpoint_ok = left.x == 2.0 and right.x == 5.0 and left.iterations == right.iterations == 0
    except Exception:
        endpoint_ok = False
    _check(checks, "endpoint-roots", "semantic", endpoint_ok)

    try:
        positive = module.bisect(lambda x: x - 0.25, -1.0, 1.0, x_tolerance=1e-9)
        negative = module.bisect(lambda x: 0.25 - x, -1.0, 1.0, x_tolerance=1e-9)
        orientation_ok = abs(positive.x - 0.25) <= 2e-9 and abs(negative.x - 0.25) <= 2e-9
    except Exception:
        orientation_ok = False
    _check(checks, "sign-orientation", "semantic", orientation_ok)

    try:
        module.bisect(lambda x: 1e-300 * (x * x + 1.0), -1.0, 1.0)
        underflow_ok = False
    except module.InvalidBracketError:
        underflow_ok = True
    except Exception:
        underflow_ok = False
    _check(checks, "underflow-sign-check", "robustness", underflow_ok)

    try:
        module.bisect(lambda x: x - 0.123456789, -1.0, 1.0, x_tolerance=1e-15, max_iterations=2)
        budget_ok = False
    except module.ConvergenceError:
        budget_ok = True
    except Exception:
        budget_ok = False
    _check(checks, "budget-exhaustion", "protocol", budget_ok)

    nonfinite_ok = True
    for callback in (lambda x: float("nan"), lambda x: float("inf"), lambda x: "bad"):
        try:
            module.bisect(callback, -1.0, 1.0)
            nonfinite_ok = False
        except ValueError:
            pass
        except Exception:
            nonfinite_ok = False
    _check(checks, "nonfinite-observations", "robustness", nonfinite_ok)
    return _report(checks)


def _report(checks: list[dict[str, Any]]) -> dict[str, Any]:
    passed = [check for check in checks if check["passed"]]
    failures = [check for check in checks if not check["passed"]]
    families = {check["family"] for check in failures}
    if "robustness" in families:
        failure_family = "robustness_failure"
    elif "protocol" in families:
        failure_family = "budget_failure"
    elif failures:
        failure_family = "semantic_failure"
    else:
        failure_family = None
    semantic = [check for check in checks if check["family"] == "semantic"]
    robustness = [check for check in checks if check["family"] == "robustness"]
    return {
        "terminal_status": "completed",
        "terminal_success": not failures,
        "reward_scalar": 1.0 if not failures else 0.0,
        "metrics": {
            "semantic_correctness": _fraction(semantic),
            "robustness": _fraction(robustness),
            "integrity": 1.0,
            "checks_passed": len(passed),
            "checks_total": len(checks),
        },
        "reward_vector": {
            "semantic_correctness": _fraction(semantic),
            "robustness": _fraction(robustness),
            "integrity": 1.0,
        },
        "failure_codes": [failure_family] if failure_family else [],
        "failure_family": failure_family,
        "checks": checks,
    }


def _fraction(checks: list[dict[str, Any]]) -> float:
    return round(sum(1 for check in checks if check["passed"]) / len(checks), 6) if checks else 1.0
