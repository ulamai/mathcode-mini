# Tinker

The public environment is intentionally written as a normal Python
`environment_factory`, so the same stateful loop can be adapted to Tinker's
`AgentToolMessageEnv` or the Verifiers RL recipe.

The easiest first experiment is the included TRL script:

```bash
uv sync --extra rl
python train_grpo.py --model Qwen/Qwen2.5-0.5B-Instruct --max-steps 10
```

For a Verifiers Hub publication, install the public environment package and
pass its environment ID to Tinker's Verifiers recipe. The public task uses a
demo grader; Ulam's active scorer is never part of this repository.
