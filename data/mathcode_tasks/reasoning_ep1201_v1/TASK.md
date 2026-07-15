# Erdős #1201 partial-proof audit

This is a public, expired MathCode reasoning task imported from the Ulam
Verified Research Reasoning Trajectories sample. It is an inspection example,
not a hidden holdout or a commercial training claim.

## Problem

For every epsilon, eta > 0, find k such that the set G_k(epsilon) = {n: P(prod_{j=0}^k (n+j)) > n^{1-epsilon}} has density at least 1-eta. The RLVR proof record proves lower asymptotic density at least 1-eta via upper density control of the exceptional set.

## Assumptions

- epsilon > 0 and eta > 0 are fixed before k/H is chosen
- P(1) may be set to 1; only large n matter
- External theorem inputs: Matomaki-Radziwill short interval theorem; Dickman-de Bruijn smooth-number asymptotic

## Target

Prove upper density of the exceptional set B_H(epsilon) tends to 0 as H tends to infinity, then set k=H-1.

## Your job

Use the repository tools to complete `draft/assessment.json`, write a concise
proof-unit-grounded account in `draft/proof.md`, and classify every adversarial
prompt in `draft/adversarial.json`. Preserve the source theorem status:
`partial_solution`. Do not upgrade a partial or conditional result
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

- `PVU-001` (reduction), dependencies: none — The exceptional-set formulation is equivalent to the desired lower-density statement after taking k=H-1.
- `PVU-002` (parameter_choice), dependencies: PVU-001 — For 0<epsilon<1, alpha=1-epsilon/2 gives rho(1/alpha)<1 and a positive delta; H can be chosen so C0 loglogH/logH<=delta.
- `PVU-003` (multiplicativity_check), dependencies: PVU-002 — The indicator f_X(m)=1_{P(m)<=y} is bounded and multiplicative for fixed X and y.
- `PVU-004` (external_theorem_application), dependencies: PVU-002, PVU-003 — The long average A_X of f_X over [X,2X] tends to r=rho(1/alpha), hence is <=r+delta for large X.
- `PVU-005` (external_theorem_application), dependencies: PVU-002, PVU-003, PVU-004 — MR gives local averages of f_X close to A_X outside a controlled exceptional set, and these local averages are <1.
- `PVU-006` (smoothness_implication), dependencies: PVU-002, PVU-003 — Every bad start n in [X,2X] has f_X(n+j)=1 for all 0<=j<H.
- `PVU-007` (containment), dependencies: PVU-005, PVU-006 — B_H(epsilon) cap [X,2X] is contained in the MR exceptional set E_{X,H}.
- `PVU-008` (asymptotic_bound), dependencies: PVU-007 — After dividing by X and taking limsup_X, the dyadic bad-set density is O_epsilon((log H)^{1/3}/H^{delta/25}).
- `PVU-009` (density_conversion), dependencies: PVU-008 — Dyadic limsup control implies global upper-density control up to a factor 2.
- `PVU-010` (final_assembly_and_gap_label), dependencies: PVU-001, PVU-009 — Choosing H gives k=H-1 and lower density at least 1-eta; the proof does not establish natural-density existence.

## Adversarial prompts

- `EP1201_ADV_001` targets `PVU-010`: The proof establishes that the natural density exists and is at least 1-eta.
- `EP1201_ADV_002` targets `PVU-005`: Matomaki-Radziwill implies the short interval average is close to A_X for every starting point n.
- `EP1201_ADV_003` targets `PVU-004`: The long average A_X tends to rho(alpha).
- `EP1201_ADV_004` targets `PVU-002`: For each n one may choose H=H(n) large enough, and then set k=H(n)-1.
- `EP1201_ADV_005` targets `PVU-003`: The smoothness indicator remains multiplicative even if the threshold y is allowed to vary with the input m.
- `EP1201_ADV_006` targets `PVU-007`: The MR exceptional set is contained in the bad-start set B_H(epsilon).
- `EP1201_ADV_007` targets `PVU-009`: Dyadic limsup at most theta automatically implies global upper density at most theta with no loss.
- `EP1201_ADV_008` targets `PVU-006`: If the product is y-smooth then the desired condition holds, regardless of the relation between y and n^{1-epsilon}.

Run the public structural checks before `finish`. The public bundle exposes
claims and dependencies but not canonical proofs or expected statuses.
