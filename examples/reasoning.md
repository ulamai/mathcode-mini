# Reasoning task projections

This repository includes three small, public MathCode-formatted reasoning
bundles under [`data/mathcode_tasks`](../data/mathcode_tasks). They are the
same public projection published in the [sanitized Dataset](https://huggingface.co/datasets/ulamai/mathcode-mini-traces/tree/main/data/mathcode_tasks):

- `reasoning_ep258_v1` — known-status public sample;
- `reasoning_ep1201_v1` — partial, draft-reviewed public sample;
- `reasoning_arxiv_2602_v1` — conditional, reviewed public sample.

The bundles are intended for inspection, parser/environment integration, and
research experiments. They include normalized problems, proof-unit claims,
dependencies, public verifier predicates, and adversarial prompts. They do not
include canonical proofs, expected statuses, expected adversarial verdicts,
reward gates, or private evaluator code.

The runnable public reward example in this mini repository remains the
expired `bisect_repair_v1` task. Use `MathCodeMiniEnv` for that bisection
demo; the reasoning bundles are public task projections and are not scored by
the bisection grader. Ulam's full MathCode release provides the host-only
operator scorer and canonical episode/replay path.

Other public surfaces:

- [Interactive MathCode Mini Space](https://huggingface.co/spaces/ulamai/mathcode-mini)
- [Sanitized MathCode Dataset](https://huggingface.co/datasets/ulamai/mathcode-mini-traces)
