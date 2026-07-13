from __future__ import annotations

import json

import gradio as gr

from mathcode_mini.baselines import apply_scripted_baseline
from mathcode_mini.env import MathCodeMiniEnv


def run_demo() -> str:
    env = MathCodeMiniEnv()
    try:
        env.reset()
        assert env.episode_dir is not None
        apply_scripted_baseline(env.episode_dir / "workspace")
        env.finish()
        return json.dumps(env.report, indent=2, sort_keys=True)
    finally:
        env.close()


demo = gr.Interface(
    fn=run_demo,
    inputs=[],
    outputs=gr.Code(language="json", label="Public reward report"),
    title="MathCode Mini",
    description="A public expired coding-agent task with typed tools, real execution, and a replayable terminal reward.",
)

if __name__ == "__main__":
    demo.launch()
