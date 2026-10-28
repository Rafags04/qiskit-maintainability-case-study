"""Unit tests for Quantum Phase Estimation (QPE)."""

import unittest
from algorithms.phase_estimation import (
    build_qpe_circuit,
    run_qpe,
)


class TestQuantumPhaseEstimation(unittest.TestCase):
    """Test suite for Quantum Phase Estimation."""

    def test_exact_dyadic_phases(self):
        """Verifies exact phase recovery for dyadic rational fractions k / 2^m."""
        # theta = 0.5 (1/2), with m=3 -> expected 0.5
        est, err, bitstr, _, _ = run_qpe(0.5, num_counting_qubits=3, shots=512)
        self.assertAlmostEqual(est, 0.5, places=5)
        self.assertAlmostEqual(err, 0.0, places=5)
        self.assertEqual(bitstr, "100")

        # theta = 0.25 (1/4), with m=3 -> expected 0.25
        est, err, bitstr, _, _ = run_qpe(0.25, num_counting_qubits=3, shots=512)
        self.assertAlmostEqual(est, 0.25, places=5)
        self.assertAlmostEqual(err, 0.0, places=5)
        self.assertEqual(bitstr, "010")

        # theta = 0.125 (1/8), with m=3 -> expected 0.125
        est, err, bitstr, _, _ = run_qpe(0.125, num_counting_qubits=3, shots=512)
        self.assertAlmostEqual(est, 0.125, places=5)
        self.assertAlmostEqual(err, 0.0, places=5)
        self.assertEqual(bitstr, "001")

    def test_approximate_phase(self):
        """Verifies that non-dyadic phases are approximated within 2^-m resolution."""
        # theta = 1/3 ~ 0.3333, with m=4 (resolution 1/16 = 0.0625)
        theta_test = 1.0 / 3.0
        est, err, _, _, _ = run_qpe(theta_test, num_counting_qubits=4, shots=1024)
        # Error must not exceed the resolution interval
        self.assertLess(err, 1.0 / (2**4))

    def test_circuit_qubits(self):
        """Verifies that the circuit comprises m counting qubits + 1 target qubit."""
        m = 5
        qc = build_qpe_circuit(0.5, num_counting_qubits=m)
        self.assertEqual(qc.num_qubits, m + 1)
        self.assertEqual(qc.num_clbits, m)

    def test_invalid_counting_qubits_raises_error(self):
        """Verifies that non-positive counting qubit counts trigger ValueError."""
        with self.assertRaises(ValueError):
            build_qpe_circuit(0.5, num_counting_qubits=0)


if __name__ == "__main__":
    unittest.main()
