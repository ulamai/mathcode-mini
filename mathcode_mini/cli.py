from __future__ import annotations

import argparse
import json

from .baselines import apply_scripted_baseline
from .env import MathCodeMiniEnv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public MathCode Mini demo")
    parser.add_argument("command", choices=("demo", "starter", "tests"), nargs="?", default="demo")
    args = parser.parse_args(argv)
    env = MathCodeMiniEnv()
    try:
        instruction = env.reset()
        if args.command == "starter":
            print(json.dumps({"instruction": instruction, "reward": env.reward}, indent=2))
        elif args.command == "tests":
            print(env.run_public_tests())
        else:
            assert env.episode_dir is not None
            apply_scripted_baseline(env.episode_dir / "workspace")
            print(env.finish())
    finally:
        env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
