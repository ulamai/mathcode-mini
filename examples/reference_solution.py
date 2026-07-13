from __future__ import annotations

import math
import numbers
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class BisectionResult:
    x: float
    fx: float
    lower: float
    upper: float
    f_lower: float
    f_upper: float
    iterations: int
    evaluations: int


class InvalidBracketError(ValueError):
    pass


class ConvergenceError(RuntimeError):
    pass


def _finite_real(value, label: str) -> float:
    if not isinstance(value, numbers.Real):
        raise ValueError(f"{label} must be real")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _same_sign(left: float, right: float) -> bool:
    return (left < 0 and right < 0) or (left > 0 and right > 0)


def bisect(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    x_tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> BisectionResult:
    a = _finite_real(a, "a")
    b = _finite_real(b, "b")
    tolerance = _finite_real(x_tolerance, "x_tolerance")
    if not a < b:
        raise ValueError("a must be smaller than b")
    if tolerance <= 0:
        raise ValueError("x_tolerance must be positive")
    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")
    fa = _finite_real(f(a), "f(a)")
    fb = _finite_real(f(b), "f(b)")
    evaluations = 2
    if fa == 0.0:
        return BisectionResult(a, fa, a, a, fa, fa, 0, evaluations)
    if fb == 0.0:
        return BisectionResult(b, fb, b, b, fb, fb, 0, evaluations)
    if _same_sign(fa, fb):
        raise InvalidBracketError("endpoint values must have opposite signs")
    for iteration in range(1, max_iterations + 1):
        midpoint = a / 2.0 + b / 2.0
        fm = _finite_real(f(midpoint), "f(midpoint)")
        evaluations += 1
        if fm == 0.0:
            return BisectionResult(midpoint, fm, midpoint, midpoint, fm, fm, iteration, evaluations)
        if _same_sign(fa, fm):
            a, fa = midpoint, fm
        else:
            b, fb = midpoint, fm
        if b - a <= tolerance:
            x, fx = (a, fa) if abs(fa) <= abs(fb) else (b, fb)
            return BisectionResult(x, fx, a, b, fa, fb, iteration, evaluations)
    raise ConvergenceError("iteration budget exhausted before certification")
