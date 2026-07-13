"""Tiny TRL GRPO example for the public expired task.

Run with: python train_grpo.py --model Qwen/Qwen2.5-0.5B-Instruct --max-steps 10
"""

from __future__ import annotations

import argparse

from datasets import Dataset
from trl import GRPOConfig, GRPOTrainer

from mathcode_mini.env import MathCodeMiniEnv


def reward_func(environments, **kwargs):
    return [float(environment.reward) for environment in environments]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", default="outputs/mathcode-mini")
    parser.add_argument("--max-steps", type=int, default=10)
    args = parser.parse_args()
    prompts = [
        [
            {
                "role": "user",
                "content": (
                    "Repair the bisection repository using the MathCode tools. "
                    "Run public tests, inspect your diff, then call finish."
                ),
            }
        ]
        * 32
    ]
    dataset = Dataset.from_dict({"prompt": prompts, "task_id": ["bisect_repair_v1"] * len(prompts)})
    trainer = GRPOTrainer(
        model=args.model,
        reward_funcs=reward_func,
        train_dataset=dataset,
        environment_factory=MathCodeMiniEnv,
        args=GRPOConfig(
            output_dir=args.output_dir,
            max_steps=args.max_steps,
            num_generations=4,
            max_completion_length=2048,
            logging_steps=1,
            report_to=[],
        ),
    )
    trainer.train()


if __name__ == "__main__":
    main()
