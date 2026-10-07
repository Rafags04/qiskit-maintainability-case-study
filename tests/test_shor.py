"""Unit tests for Shor's algorithm."""

import unittest
from algorithms.shor import (
    c_amod15,
    build_shor_circuit,
    run_shor,
)


class TestShor(unittest.TestCase):
    """Test suite for Shor's algorithm."""

    def test_modular_multiplication_gate_creation(self):
        """Verifies construction of the controlled modular multiplication gate."""
        gate = c_amod15(7, 1)
        self.assertEqual(gate.num_qubits, 5)  # 1 control + 4 work qubits

    def test_invalid_base_raises_error(self):
        """Verifies that non-coprime or unsupported bases raise ValueError."""
        with self.assertRaises(ValueError):
            c_amod15(3, 1)  # 3 is not coprime to 15

    def test_circuit_qubits(self):
        """Verifies that the circuit allocates n_count + 4 work qubits."""
        qc = build_shor_circuit(a=7, n_count=4)
        self.assertEqual(qc.num_qubits, 8)
        self.assertEqual(qc.num_clbits, 4)

    def test_factorization_N15_with_base7(self):
        """Verifies full factorization of N=15 into {3, 5} with base 7."""
        factors, periods, counts, _ = run_shor(a=7, N=15, n_count=4, shots=1024)
        self.assertIn(4, periods)  # Theoretical period of 7 mod 15 is 4
        self.assertTrue({3, 5}.issubset(factors))

    def test_factorization_N15_with_base2(self):
        """Verifies full factorization of N=15 into {3, 5} with base 2."""
        factors, periods, counts, _ = run_shor(a=2, N=15, n_count=4, shots=1024)
        self.assertIn(4, periods)  # Theoretical period of 2 mod 15 is 4
        self.assertTrue({3, 5}.issubset(factors))

    def test_classical_gcd_shortcut(self):
        """Verifies that choosing a sharing factor directly triggers the classical gcd path."""
        factors, periods, counts, _ = run_shor(a=3, N=15)
        self.assertEqual(factors, {3, 5})
        self.assertEqual(periods, [1])

    def test_unsupported_N_raises_error(self):
        """Verifies that N != 15 raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            run_shor(a=7, N=21)


if __name__ == "__main__":
    unittest.main()
