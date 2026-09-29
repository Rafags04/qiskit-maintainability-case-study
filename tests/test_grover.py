"""Pruebas unitarias para el Algoritmo de Grover."""

import unittest
from algorithms.grover import (
    build_grover_circuit,
    optimal_iterations,
    run_grover,
)


class TestGrover(unittest.TestCase):
    """Casos de prueba para el algoritmo de Grover."""

    def test_optimal_iterations_calculation(self):
        """Verifica la formula teorica de iteraciones optimas."""
        # N = 4 (n=2), 1 target -> round(pi/4 * 2) = 1
        self.assertEqual(optimal_iterations(2, 1), 1)
        # N = 8 (n=3), 1 target -> round(pi/4 * sqrt(8)) = 2
        self.assertEqual(optimal_iterations(3, 1), 2)

    def test_grover_single_target_n3(self):
        """Verifica que Grover encuentre con alta probabilidad un objetivo en n=3."""
        target = "110"
        best_str, prob, counts, _ = run_grover(target, n=3, shots=2048)
        self.assertEqual(best_str, target)
        self.assertGreater(prob, 0.90)

    def test_grover_single_target_n2(self):
        """Verifica que Grover encuentre un objetivo en n=2 con 100% de probabilidad."""
        target = "01"
        best_str, prob, counts, _ = run_grover(target, n=2, shots=1024)
        self.assertEqual(best_str, target)
        # Para n=2 con 1 iteracion, la probabilidad teorica es exactamente 100%
        self.assertAlmostEqual(prob, 1.0, places=2)

    def test_invalid_target_length(self):
        """Verifica que una longitud de objetivo incompatible lance ValueError."""
        with self.assertRaises(ValueError):
            build_grover_circuit("1010", n=3)


if __name__ == "__main__":
    unittest.main()
