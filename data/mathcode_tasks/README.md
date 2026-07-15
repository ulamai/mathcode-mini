# MathCode-formatted reasoning tasks

These bundles are the public projection produced by
`scripts/import_verified_reasoning.py` in MathCode. The same bundles are
published in the [sanitized MathCode Dataset](https://huggingface.co/datasets/ulamai/mathcode-mini-traces/tree/main/data/mathcode_tasks).

Each task contains:

- `task.json`: MathCode task manifest and budgets;
- `TASK.md`: policy instruction;
- `starter/`: the policy-visible workspace;
- `problem.json`: normalized problem and assumptions;
- `proof_units.json`: claims, dependencies, and public verifier predicates;
- `adversarial_tests.json`: mutation prompts without expected verdicts;
- `source_record.json`: provenance and contamination status.

Canonical proofs, expected statuses, reward gates, reference assessments, and
private evaluator code are deliberately absent from this public projection.
