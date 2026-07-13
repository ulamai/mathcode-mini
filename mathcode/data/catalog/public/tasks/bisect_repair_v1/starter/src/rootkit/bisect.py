from __future__ import annotations

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


def bisect(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    x_tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> BisectionResult:
    """Return an approximate root and the final bracket.

    This starter implementation is intentionally incomplete.
    """
    fa = float(f(a))
    fb = float(f(b))
    if fa * fb >= 0:
        raise InvalidBracketError("endpoint values must have opposite signs")

    mid = (a + b) / 2.0
    fm = float(f(mid))
    for iteration in range(1, max_iterations + 1):
        mid = (a + b) / 2.0
        fm = float(f(mid))
        if abs(fm) <= x_tolerance:
            return BisectionResult(mid, fm, a, b, fa, fb, iteration, iteration + 2)
        if fm < 0:
            a, fa = mid, fm
        else:
            b, fb = mid, fm

    return BisectionResult(mid, fm, a, b, fa, fb, max_iterations, max_iterations + 2)
