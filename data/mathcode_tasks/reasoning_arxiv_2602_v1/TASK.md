# Conditional index-4 theorem-scope audit

This is a public, expired MathCode reasoning task imported from the Ulam
Verified Research Reasoning Trajectories sample. It is an inspection example,
not a hidden holdout or a commercial training claim.

## Problem

Given the results of Archita-Becher on similitudes over fields with I^4=0, formulate a conditional extension of the index<=2 two-Clifford-component theorem to index-4 Clifford components, isolating the exact reduced-norm inputs needed and preserving open gaps.

## Assumptions

- char(K)!=2
- (A,sigma) has orthogonal involution of trivial discriminant
- (A,sigma) belongs to I^2 in the paper sense
- the source-paper external theorems are available
- for unconditional claims, RN^sgn_i and RN^2-ext_i need independent proof or citation

## Target

Produce a verified/conditional proof-unit decomposition showing what follows from RN^sgn_i and RN^2-ext_i, and what remains open.

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

- `PVU-001` (source_extraction), dependencies: none — Correctly extract the baseline theorems/propositions from the source paper that the extension uses.
- `PVU-002` (scope_reduction), dependencies: PVU-001 — Identify the missing index-4 target as the degree 0 mod 4 two-component Clifford case, not the degree 2 mod 4 parity already treated by Theorem 7.3.
- `PVU-003` (bottleneck_identification), dependencies: PVU-001, PVU-002 — Separate the sign-to-reduced-norm and reduced-norm-to-2-extension roles of Proposition 5.2.
- `PVU-004` (conditional_forward_inclusion), dependencies: PVU-001, PVU-003 — Under RN^sgn_i and local hyperbolicity, prove G(A,sigma)⊆Nrd^*_{C1}Nrd^*_{C2}.
- `PVU-005` (reverse_inclusion_to_Hyp), dependencies: PVU-001, PVU-002 — Under u(L)<=8 for splitting fields of C_i, prove Nrd^*_{C1}Nrd^*_{C2}⊆Hyp(A,sigma) and hence Hyp=Nrd product.
- `PVU-006` (equality_and_R_triviality), dependencies: PVU-004, PVU-005 — Combine inclusions to get G=Hyp=Nrd product and R-triviality under the conditional hypotheses.
- `PVU-007` (Hyp2_upgrade), dependencies: PVU-003, PVU-004, PVU-005, PVU-006 — State the additional RN^2-ext_i input needed to upgrade Hyp to Hyp2 for index-4 components.
- `PVU-008` (parity_and_boundary), dependencies: PVU-001, PVU-002 — Correctly situate the extension relative to Theorem 7.3 and the degree parity split.
- `PVU-009` (gap_classification), dependencies: PVU-003, PVU-007, PVU-008 — Label the degree-4 RN^sgn and RN^2-ext criteria as open algebraic inputs, not as proven results.
- `PVU-010` (RLVR_packaging), dependencies: PVU-009 — Package the episode as conditional proof assembly and proof-criticism data rather than as a fully machine-verifiable theorem.

## Adversarial prompts

- `ADV-001` targets `PVU-004`: The inclusion G(A,sigma)⊆Nrd^*_{C1}Nrd^*_{C2} holds for index-4 components without RN^sgn_i.
- `ADV-002` targets `PVU-007`: Once Nrd^*_{C_i}⊆Hyp(A,sigma), the same inclusion into Hyp2(A,sigma) follows automatically.
- `ADV-003` targets `PVU-008`: Theorem 7.3 already proves the two-component Clifford case for deg A≡0 mod4.
- `ADV-004` targets `PVU-005`: The reverse inclusion follows from u(K)<=8 alone, regardless of u(L) for splitting fields L.

Run the public structural checks before `finish`. The public bundle exposes
claims and dependencies but not canonical proofs or expected statuses.
