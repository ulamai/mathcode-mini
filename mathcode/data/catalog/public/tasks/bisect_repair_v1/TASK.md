# Repair the certified bisection solver

The `rootkit` package exposes a bisection routine that returns a certificate,
not merely an approximate float. The current implementation works on a basic
example but violates the API contract on endpoint roots, sign orientation,
non-finite observations, and exhausted iteration budgets.

## Required API

Keep these public names:

- `BisectionResult`;
- `InvalidBracketError`;
- `ConvergenceError`;
- `bisect(f, a, b, *, x_tolerance=1e-12, max_iterations=100)`.

`BisectionResult` contains `x`, `fx`, `lower`, `upper`, `f_lower`,
`f_upper`, `iterations`, and `evaluations`.

## Contract

1. `a` and `b` are finite and satisfy `a < b`.
2. `x_tolerance` is finite and positive. `max_iterations` is a positive
   integer.
3. Callback results must be real and finite. Callback exceptions otherwise
   propagate.
4. An exact root at either endpoint succeeds with zero iterations.
5. Otherwise, endpoint values must have opposite signs. Compare signs
   directly; multiplying values can overflow or underflow.
6. Each interior callback evaluation consumes one iteration.
7. Success means either `fx == 0`, or the returned interval remains a
   sign-changing bracket and the maximum distance from `x` to either endpoint
   is at most `x_tolerance`.
8. Stored function values must correspond to the returned points.
9. If the iteration budget cannot certify the requested accuracy, raise
   `ConvergenceError`. Do not return an unchecked last midpoint.
10. Midpoint arithmetic must remain finite for finite, widely separated
    endpoints.

Continuity on the supplied interval is a caller precondition.

Add useful regression tests under `tests/added/`. Do not edit protected public
tests. Inspect the final diff before submitting.
