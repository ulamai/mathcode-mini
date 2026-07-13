import math
import unittest

from rootkit import InvalidBracketError, bisect


class PublicBisectionTests(unittest.TestCase):
    def test_square_root_two(self):
        result = bisect(lambda x: x * x - 2.0, 0.0, 2.0, x_tolerance=1e-9)
        self.assertAlmostEqual(result.x, math.sqrt(2.0), places=7)

    def test_invalid_bracket(self):
        with self.assertRaises(InvalidBracketError):
            bisect(lambda x: x * x + 1.0, -1.0, 1.0)

    def test_endpoint_root_is_valid(self):
        result = bisect(lambda x: x - 2.0, 2.0, 5.0)
        self.assertEqual(result.x, 2.0)
        self.assertEqual(result.iterations, 0)


if __name__ == "__main__":
    unittest.main()
