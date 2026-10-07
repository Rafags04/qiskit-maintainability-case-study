"""Unit tests for the Deutsch-Jozsa algorithm."""

import unittest
from algorithms.deutsch_jozsa import (
    build_deutsch_jozsa_oracle,
    build_deutsch_jozsa_circuit,
    run_deutsch_jozsa,
)


class TestDeutschJozsa(unittest.TestCase):
    """Test suite for the Deutsch-Jozsa algorithm."""

    def test_constant_zero(self):
        """Verifies that a constant f(x)=0 function is classified correctly."""
        n = 3
        classification, counts, _ = run_deutsch_jozsa(n, oracle_type="constant_0", shots=512)
        self.assertEqual(classification, "constant")
        self.assertIn("000", counts)
        self.assertEqual(counts["000"], 512)

    def test_constant_one(self):
        """Verifies that a constant f(x)=1 function is classified correctly."""
        n = 3
        classification, counts, _ = run_deutsch_jozsa(n, oracle_type="constant_1", shots=512)
        self.assertEqual(classification, "constant")
        self.assertIn("000", counts)
        self.assertEqual(counts["000"], 512)

    def test_balanced_functions(self):
        """Verifies that balanced functions with diverse masks do not output '0'*n."""
        n = 4
        for mask in [1, 2, 7, 15]:
            classification, counts, _ = run_deutsch_jozsa(
                n, oracle_type="balanced", mask=mask, shots=512
            )
            self.assertEqual(classification, "balanced")
            self.assertNotIn("0000", counts)

    def test_invalid_oracle_type(self):
        """Verifies that an unknown oracle type raises ValueError."""
        with self.assertRaises(ValueError):
            build_deutsch_jozsa_oracle(3, "invalid_type")  # type: ignore

    def test_invalid_num_qubits(self):
        """Verifies that non-positive qubit counts raise ValueError."""
        with self.assertRaises(ValueError):
            build_deutsch_jozsa_oracle(0, "constant_0")
        with self.assertRaises(ValueError):
            build_deutsch_jozsa_circuit(0, None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
