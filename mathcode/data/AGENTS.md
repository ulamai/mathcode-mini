# AGENTS.md — MathCode Policy Runtime

Applies to every policy, reasoner, tool worker, critic, and coordinator acting
inside a MathCode task workspace.

## Objective

Complete the public engineering task by changing only the permitted workspace.
Use actual observations, preserve the mathematical contract, and submit a
working artifact with concise evidence.

## Absolute rules

1. Treat `TASK.md` as the public source of requirements.
2. Never inspect or attempt to infer private evaluator files, fixtures, seeds,
   reference solutions, or reward internals.
3. Never fabricate command output, test results, files, or subagent reports.
4. Do not delete or weaken tests to claim success.
5. Do not write outside the episode workspace.
6. Do not use the network.
7. Preserve public APIs unless the task explicitly changes them.
8. Distinguish observed evidence from hypotheses.
9. Check the resulting diff before submission.
10. A task may require no delegation. Do not create agents merely to increase
    activity.

## Recommended loop

1. Read `TASK.md` and identify the mathematical and engineering obligations.
2. Inspect repository structure and public tests.
3. Reproduce at least one relevant failure.
4. State a short plan containing checkable milestones.
5. Make the smallest coherent change that advances the task.
6. Inspect every real tool observation before acting again.
7. Add useful regression tests without relying on them as acceptance evidence.
8. Run the protected public suite.
9. Inspect the final diff and cite observation IDs in the submission report.

## Evidence report

The terminal report contains:

```json
{
  "requirements_completed": ["R1"],
  "evidence": {"R1": ["observation:a7"]},
  "known_limitations": []
}
```

The report is checked for grounding but is not proof of correctness. Private
verification determines terminal acceptance.

## Delegation

Only a coordinator profile with a positive child-agent budget may delegate.
Specialists should normally return read-only evidence reports. The coordinator
owns edits, reconciles conflicting advice, and remains accountable for the
final repository. Delegation itself receives no reward.
