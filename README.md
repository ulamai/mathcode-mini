---
title: MathCode Mini
emoji: 🧮
colorFrom: indigo
colorTo: blue
sdk: gradio
app_file: app.py
python_version: "3.11"
suggested_hardware: "cpu-basic"
license: other
tags:
- reinforcement-learning
- coding-agents
- tool-use
- code-repair
---

# MathCode Mini

MathCode Mini is a small, public, expired coding-agent environment for RL and
tool-use research. It is deliberately runnable on a laptop and deliberately
separate from Ulam's private benchmark scorer.

The task is to repair a certified bisection solver. The agent must inspect and
edit a real repository, run public tests, and call `finish`. The terminal
reward is produced by a public contract grader. Episodes include real file
changes, tool observations, state hashes, and a replayable event log.

This is a compatibility example, not an active benchmark. It contains one
expired task and a public reference solution. Ulam's active tasks, private
evaluators, operator tokens, and commercial scorer are not included.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python -m mathcode_mini.cli starter
python -m mathcode_mini.cli tests
python -m mathcode_mini.cli demo
```

If you use `uv`, the equivalent commands are `uv sync` and
`uv run python -m mathcode_mini.cli demo`.

The demo runs the public scripted baseline and prints its terminal reward. To
build an agent, use the stateful environment directly:

```python
from mathcode_mini import MathCodeMiniEnv

env = MathCodeMiniEnv()
print(env.reset())
print(env.repo_tree())
print(env.read_file("TASK.md"))
# Model tool calls go here.
print(env.finish())
print(env.reward)
env.close()
```

## Train with TRL

Install the optional RL dependencies and run a tiny GRPO experiment:

```bash
python -m pip install -e '.[rl]'
python train_grpo.py \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --max-steps 10
```

The environment exposes individual typed tools rather than a generic
`step(action)` method. TRL's `environment_factory` creates one stateful
environment per rollout, and the reward function reads the terminal reward
after `finish`.

## Public surfaces

- `app.py`: a browser demo suitable for a Hugging Face Space.
- `requirements.txt`: Space runtime dependencies.
- `train_grpo.py`: minimal TRL multi-turn GRPO example.
- `examples/prime.md`: Prime hosted-evaluation smoke test.
- `examples/tinker.md`: Tinker integration direction.
- `examples/huggingface.md`: Space and sanitized Dataset publication guide.
- `mathcode_mini/grader.py`: public expired-task grader.

`examples/reference_solution.py` is an intentionally public upper-bound
baseline for this expired task; it is not a template for active MathCode
tasks.

## Safety and research boundaries

The public grader is intentionally visible because this task is expired. Do
not treat its score as Ulam's commercial reward truth. Do not add active Ulam
tasks, private fixtures, scorer credentials, reference implementations for
active tasks, or customer traces to this repository.

The local environment executes candidate Python in the current process's OS
context. Use a container or hosted sandbox when running untrusted policies.

## Hugging Face publication

The recommended public deployment is a CPU Gradio Space built from this
repository. GitHub remains the canonical source; the Space is a discoverable
interactive view of the same expired task. A separate sanitized Dataset
repository can hold public trajectory summaries and failure-atlas records.
See [examples/huggingface.md](examples/huggingface.md) for the release
procedure and the public-data boundary.

## License

See [LICENSE](LICENSE). This public research repository does not grant access
to Ulam's private benchmark or commercial scoring service.
