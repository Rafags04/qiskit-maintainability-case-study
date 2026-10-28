"""Unit tests for the Quantum Teleportation protocol."""

import unittest
import numpy as np
from algorithms.teleportation import (
    build_teleportation_circuit,
    run_teleportation,
)


class TestQuantumTeleportation(unittest.TestCase):
    """Test suite for the quantum teleportation protocol."""

    def test_circuit_qubits_and_registers(self):
        """Verifies that the circuit allocates 3 qubits and 3 classical bits."""
        qc = build_teleportation_circuit(theta=1.0, phi=0.5)
        self.assertEqual(qc.num_qubits, 3)
        self.assertEqual(qc.num_clbits, 3)

    def test_teleportation_fidelity_state_zero(self):
        """Verifies unity fidelity when teleporting state |0> (theta=0, phi=0)."""
        fidelity, counts, _ = run_teleportation(
            theta=0.0, phi=0.0, verify_with_inverse=True, shots=1024
        )
        self.assertEqual(fidelity, 1.0)

    def test_teleportation_fidelity_state_one(self):
        """Verifies unity fidelity when teleporting state |1> (theta=pi, phi=0)."""
        fidelity, counts, _ = run_teleportation(
            theta=np.pi, phi=0.0, verify_with_inverse=True, shots=1024
        )
        self.assertEqual(fidelity, 1.0)

    def test_teleportation_fidelity_superposition(self):
        """Verifies unity fidelity for an arbitrary superposition state."""
        theta = 1.35
        phi = 0.75
        fidelity, counts, _ = run_teleportation(
            theta=theta, phi=phi, verify_with_inverse=True, shots=2048
        )
        self.assertEqual(fidelity, 1.0)

    def test_direct_measurement_probabilities(self):
        """Verifies that direct measurement probability matches cos^2(theta/2)."""
        theta = np.pi / 3  # cos(pi/6)^2 = 3/4 = 0.75
        p0_obs, counts, _ = run_teleportation(
            theta=theta, phi=0.0, verify_with_inverse=False, shots=4000
        )
        expected_p0 = float(np.cos(theta / 2) ** 2)
        # Statistical tolerance for 4000 shots
        self.assertAlmostEqual(p0_obs, expected_p0, delta=0.03)


if __name__ == "__main__":
    unittest.main()
