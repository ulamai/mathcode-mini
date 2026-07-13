from __future__ import annotations

import unittest

from mathcode_mini.baselines import apply_scripted_baseline
from mathcode_mini.env import MathCodeMiniEnv


class PublicDemoTests(unittest.TestCase):
    def test_scripted_baseline_gets_public_reward(self):
        env = MathCodeMiniEnv()
        try:
            env.reset()
            assert env.episode_dir is not None
            apply_scripted_baseline(env.episode_dir / "workspace")
            env.finish()
            self.assertEqual(env.reward, 1.0)
            self.assertEqual(env.report["metrics"]["checks_total"], 7)
        finally:
            env.close()

    def test_starter_is_not_successful(self):
        env = MathCodeMiniEnv()
        try:
            env.reset()
            env.finish()
            self.assertEqual(env.reward, 0.0)
        finally:
            env.close()


if __name__ == "__main__":
    unittest.main()
