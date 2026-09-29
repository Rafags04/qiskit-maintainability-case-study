"""Pruebas unitarias para Estimacion Cuantica de Fase (QPE)."""

import unittest
from algorithms.quantum_phase_estimation import (
    build_qpe_circuit,
    run_qpe,
)


class TestQuantumPhaseEstimation(unittest.TestCase):
    """Casos de prueba para QPE."""

    def test_exact_dyadic_phases(self):
        """Verifica fases que se representan exactamente como enteros / 2^m."""
        # theta = 0.5 (1/2), con m=3 -> esperado 0.5
        est, err, bitstr, _, _ = run_qpe(0.5, num_counting_qubits=3, shots=512)
        self.assertAlmostEqual(est, 0.5, places=5)
        self.assertAlmostEqual(err, 0.0, places=5)
        self.assertEqual(bitstr, "100")

        # theta = 0.25 (1/4), con m=3 -> esperado 0.25
        est, err, bitstr, _, _ = run_qpe(0.25, num_counting_qubits=3, shots=512)
        self.assertAlmostEqual(est, 0.25, places=5)
        self.assertAlmostEqual(err, 0.0, places=5)
        self.assertEqual(bitstr, "010")

        # theta = 0.125 (1/8), con m=3 -> esperado 0.125
        est, err, bitstr, _, _ = run_qpe(0.125, num_counting_qubits=3, shots=512)
        self.assertAlmostEqual(est, 0.125, places=5)
        self.assertAlmostEqual(err, 0.0, places=5)
        self.assertEqual(bitstr, "001")

    def test_approximate_phase(self):
        """Verifica que fases no diadicas se aproximen dentro de la resolucion 2^-m."""
        # theta = 1/3 ~ 0.3333, con m=4 (resolucion 1/16 = 0.0625)
        theta_test = 1.0 / 3.0
        est, err, _, _, _ = run_qpe(theta_test, num_counting_qubits=4, shots=1024)
        # El error no debe superar medio intervalo de resolucion
        self.assertLess(err, 1.0 / (2**4))

    def test_circuit_qubits(self):
        """Verifica que el circuito tenga m qubits de conteo + 1 qubit objetivo."""
        m = 5
        qc = build_qpe_circuit(0.5, num_counting_qubits=m)
        self.assertEqual(qc.num_qubits, m + 1)
        self.assertEqual(qc.num_clbits, m)


if __name__ == "__main__":
    unittest.main()
