"""Unit tests for Grover's search algorithm."""

import unittest
from algorithms.grover import (
    build_grover_circuit,
    build_grover_oracle,
    build_grover_diffuser,
    optimal_iterations,
    run_grover,
)


class TestGrover(unittest.TestCase):
    """Test suite for Grover's search algorithm."""

    def test_optimal_iterations_calculation(self):
        """Verifies the theoretical optimal iteration formula."""
        # N = 4 (n=2), 1 target -> round(pi/4 * 2) = 1
        self.assertEqual(optimal_iterations(2, 1), 1)
        # N = 8 (n=3), 1 target -> round(pi/4 * sqrt(8)) = 2
        self.assertEqual(optimal_iterations(3, 1), 2)
        # Edge cases
        self.assertEqual(optimal_iterations(0, 1), 0)
        self.assertEqual(optimal_iterations(3, 0), 0)

    def test_grover_single_target_n3(self):
        """Verifies that Grover locates a marked state with high probability in n=3."""
        target = "110"
        best_str, prob, counts, _ = run_grover(target, n=3, shots=2048)
        self.assertEqual(best_str, target)
        self.assertGreater(prob, 0.90)

    def test_grover_single_target_n2(self):
        """Verifies that Grover finds a target in n=2 with 100% deterministic probability."""
        target = "01"
        best_str, prob, counts, _ = run_grover(target, n=2, shots=1024)
        self.assertEqual(best_str, target)
        # For n=2 with 1 iteration, the theoretical success rate is exactly 1.0 (100%)
        self.assertAlmostEqual(prob, 1.0, places=2)

    def test_grover_multi_target(self):
        """Verifies that multi-target search amplifies all marked items."""
        targets = ["001", "110"]
        best_str, prob, counts, _ = run_grover(targets, n=3, shots=2048)
        self.assertIn(best_str, targets)
        self.assertGreater(prob, 0.90)

    def test_invalid_target_length(self):
        """Verifies that incompatible target lengths raise ValueError."""
        with self.assertRaises(ValueError):
            build_grover_circuit("1010", n=3)
        with self.assertRaises(ValueError):
            build_grover_oracle([], n=3)
        with self.assertRaises(ValueError):
            build_grover_diffuser(0)


if __name__ == "__main__":
    unittest.main()
