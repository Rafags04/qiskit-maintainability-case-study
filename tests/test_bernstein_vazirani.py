"""Unit tests for the Bernstein-Vazirani algorithm."""

import unittest
from algorithms.bernstein_vazirani import (
    build_bernstein_vazirani_circuit,
    run_bernstein_vazirani,
)


class TestBernsteinVazirani(unittest.TestCase):
    """Test suite for the Bernstein-Vazirani algorithm."""

    def test_circuit_structure(self):
        """Verifies that the number of qubits and classical bits matches specifications."""
        secret = "1011"
        qc = build_bernstein_vazirani_circuit(secret)
        # n input qubits + 1 ancilla qubit
        self.assertEqual(qc.num_qubits, len(secret) + 1)
        self.assertEqual(qc.num_clbits, len(secret))

    def test_reconstruction_various_secrets(self):
        """Verifies exact reconstruction for diverse secret bitstrings."""
        test_secrets = ["0", "1", "10", "01", "1101", "101010"]
        for secret in test_secrets:
            detected, counts, _ = run_bernstein_vazirani(secret, shots=512)
            self.assertEqual(
                detected,
                secret,
                f"Failed to recover secret '{secret}', received '{detected}'.",
            )
            # In an ideal noiseless simulation, 100% of shots yield the exact secret
            self.assertEqual(len(counts), 1)

    def test_invalid_input_raises_error(self):
        """Verifies that empty strings or non-binary characters trigger ValueError."""
        with self.assertRaises(ValueError):
            build_bernstein_vazirani_circuit("")
        with self.assertRaises(ValueError):
            build_bernstein_vazirani_circuit("1021")


if __name__ == "__main__":
    unittest.main()
