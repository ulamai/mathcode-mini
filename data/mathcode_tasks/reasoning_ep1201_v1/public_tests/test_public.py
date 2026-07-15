from __future__ import annotations

import json
import unittest
from pathlib import Path


class PublicReasoningContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1] / "starter"

    def test_public_problem_and_units_are_present_without_gold_answers(self):
        problem = json.loads((self.root / "problem.json").read_text(encoding="utf-8"))
        units = json.loads((self.root / "proof_units.json").read_text(encoding="utf-8"))
        self.assertTrue(problem["normalized_statement"])
        self.assertGreaterEqual(len(units), 1)
        for unit in units:
            self.assertIn("pvu_id", unit)
            self.assertIn("claim", unit)
            self.assertNotIn("canonical_proof", unit)
            self.assertNotIn("expected_status", unit)

    def test_assessment_and_adversarial_artifacts_have_public_shapes(self):
        assessment = json.loads((self.root / "draft" / "assessment.json").read_text(encoding="utf-8"))
        adversarial = json.loads((self.root / "draft" / "adversarial.json").read_text(encoding="utf-8"))
        self.assertEqual(assessment["schema_version"], "mathcode-reasoning-assessment-v1")
        self.assertIsInstance(assessment["claims"], list)
        self.assertIsInstance(assessment["open_gaps"], list)
        self.assertIsInstance(adversarial, list)


if __name__ == "__main__":
    unittest.main()
