# Hugging Face publication

MathCode Mini has two useful public Hub surfaces:

1. `ulamai/mathcode-mini` as a free static Space for the interactive demo and
   public contract overview.
2. `ulamai/mathcode-mini-traces` as a Dataset repository for sanitized public
   trajectory summaries and failure-atlas records.

GitHub is the source of truth. Publish a tagged or reviewed commit to the
Space, and keep the Dataset release versioned against the same source commit.

## Space

The source repository contains the runnable Gradio app and `requirements.txt`
for local use or a separately funded Gradio Space. The organization-hosted
Space is a static derivative so it does not require paid compute. It shows the
expired `bisect_repair_v1` task, action contract, and a visible public baseline
report without executing arbitrary Python.

```bash
git clone https://github.com/ulamai/mathcode-mini.git
cd mathcode-mini
git remote add hf https://huggingface.co/spaces/ulamai/mathcode-mini
git push hf main:main
```

Use a Hugging Face credential through the normal Git credential helper. Never
put a token in a remote URL, README, Space secret, task file, or trace.

## Dataset

The companion Dataset should contain only public task IDs, typed action
summaries, state/observation hashes, public reward reports, and sanitized
failure-family counts. It must not contain active task bundles, hidden tests,
reference implementations for active tasks, operator credentials, or private
reports.

The initial release is intentionally small: it contains one clearly labelled
public reference-baseline summary and an empty preflight failure atlas. It is
research scaffolding, not a model leaderboard or a claim about model quality.

## Updating either surface

Before each release:

```bash
python -m unittest discover -s tests -v
python -m mathcode_mini.cli demo
```

Then inspect the public-only audit:

```bash
rg -n -i \
  'operator_mathcode|MATHCODE_OPERATOR_TOKEN|catalog/private|mutations\\.json|private_task_dir|evaluator\\.py' \
  . --glob '!*.md'
```

An empty result is required before publication. The Space and Dataset are
distribution views; Ulam-hosted scoring remains the source of commercial
reward truth.
