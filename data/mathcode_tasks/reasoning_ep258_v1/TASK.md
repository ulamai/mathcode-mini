# Erdős #258 proof-unit repair

This is a public, expired MathCode reasoning task imported from the Ulam
Verified Research Reasoning Trajectories sample. It is an inspection example,
not a hidden holdout or a commercial training claim.

## Problem

For every positive integer sequence (a_n) with a_n -> infinity, define Q_n=a_1...a_n and S=sum_{n>=1} tau(n)/Q_n. Prove S is irrational.

## Assumptions

- a_n are positive integers
- a_n -> infinity
- tau(n) is the number of positive divisors
- External theorem: infinitely many N with Omega(N+k)<=Ck for all k>=1

## Target

Prove S is irrational by assuming S=A/B, choosing a Tao--Teravainen good N past the denominator threshold, and forcing the cleared positive integer tail I_N to satisfy 0<I_N<1.

## Your job

Use the repository tools to complete `draft/assessment.json`, write a concise
proof-unit-grounded account in `draft/proof.md`, and classify every adversarial
prompt in `draft/adversarial.json`. Preserve the source theorem status:
`known`. Do not upgrade a partial or conditional result
into an unconditional theorem.

The assessment JSON must have this shape:

```json
{
  "schema_version": "mathcode-reasoning-assessment-v1",
  "final_status": "verified|partial|conditional|needs_review",
  "claims": [
    {"pvu_id": "PVU-001", "status": "verified|conditional|partial|needs_review", "dependencies": [], "justification": "..."}
  ],
  "open_gaps": ["GAP-..."],
  "adversarial_verdicts": [
    {"test_id": "ADV-001", "verdict": "true|false|false_or_unjustified", "reason": "..."}
  ]
}
```

## Proof units

- `PVU-001` (setup_convergence), dependencies: none — Define Q_n and justify convergence of S.
- `PVU-002` (external_theorem_statement), dependencies: none — State the Tao--Teravainen theorem with all-shift bounded Omega.
- `PVU-003` (divisor_bound), dependencies: PVU-002 — Derive tau(N+k)<=2^{Ck} from Omega(N+k)<=Ck.
- `PVU-004` (rationality_setup), dependencies: PVU-001 — Assume S=A/B and define I_N=BQ_N times the tail.
- `PVU-005` (integrality), dependencies: PVU-004 — Prove I_N is a positive integer.
- `PVU-006` (eventual_threshold), dependencies: PVU-002, PVU-004 — Use a_n -> infinity to force a_m > 3*2^C*B eventually.
- `PVU-007` (good_shift_selection), dependencies: PVU-002, PVU-006 — Select a TT-good N beyond N_0.
- `PVU-008` (geometric_tail_bound), dependencies: PVU-003, PVU-005, PVU-007 — Bound the cleared tail by a geometric series less than 1.
- `PVU-009` (final_contradiction), dependencies: PVU-005, PVU-008 — Conclude irrationality from positive integer less than 1.

## Adversarial prompts

- `ADV-001` targets `PVU-006`: Since a_n -> infinity, the sequence is eventually monotone, so Erdős--Straus applies.
- `ADV-002` targets `PVU-002`: It is enough that Omega(N+k)<=Ck for k=1,...,100.
- `ADV-003` targets `PVU-008`: Choose a_m>3*2^C; then I_N<1.
- `ADV-004` targets `PVU-003`: Since Omega(n)<=Ck, tau(n)<=Ck.
- `ADV-005` targets `PVU-009`: The same proof proves irrationality of sum sigma_k(n)/n! for all k.

Run the public structural checks before `finish`. The public bundle exposes
claims and dependencies but not canonical proofs or expected statuses.
