"""Pruebas unitarias para el Problema del Viajante de Comercio (TSP) con QAOA."""

import unittest
import numpy as np
from algorithms.tsp import (
    TSPQAOASolver,
    build_tsp_qaoa_circuit,
    run_tsp_qaoa,
)


class TestTSP(unittest.TestCase):
    """Casos de prueba para TSP resuelto con QAOA."""

    def setUp(self):
        # Matriz 3x3 donde la ruta 0 -> 1 -> 2 -> 0 tiene costo 37 y 0 -> 2 -> 1 -> 0 tiene costo 75
        self.distances = np.array([
            [0, 10, 30],
            [20, 0, 15],
            [12, 25, 0],
        ])
        self.solver = TSPQAOASolver(self.distances)

    def test_hamiltonian_dimensions(self):
        """Verifica las dimensiones de los coeficientes de Ising h y J."""
        self.assertEqual(len(self.solver.h), 4)
        self.assertEqual(self.solver.J.shape, (4, 4))

    def test_tour_cost_evaluation(self):
        """Verifica que el evaluador clasico distinga las rutas validas e invalidas."""
        # Ruta [0, 1, 2, 0]: x0=1, x3=1, x1=0, x2=0 -> bits = [1, 0, 0, 1]
        r1, cost1 = self.solver.evaluate_tour_cost([1, 0, 0, 1])
        self.assertEqual(r1, [0, 1, 2, 0])
        self.assertEqual(cost1, 37.0)

        # Ruta [0, 2, 1, 0]: x2=1, x1=1, x0=0, x3=0 -> bits = [0, 1, 1, 0]
        r2, cost2 = self.solver.evaluate_tour_cost([0, 1, 1, 0])
        self.assertEqual(r2, [0, 2, 1, 0])
        self.assertEqual(cost2, 75.0)

        # Estado invalido [0, 0, 0, 0]: no visita ciudades
        r_inv, cost_inv = self.solver.evaluate_tour_cost([0, 0, 0, 0])
        self.assertIsNone(r_inv)
        self.assertGreater(cost_inv, 100.0)

    def test_circuit_qubits(self):
        """Verifica que el circuito QAOA tenga 4 qubits y 4 bits clasicos."""
        qc = build_tsp_qaoa_circuit(self.distances, gamma=[0.5], beta=[0.5])
        self.assertEqual(qc.num_qubits, 4)
        self.assertEqual(qc.num_clbits, 4)

    def test_run_tsp_finds_optimal_or_suboptimal_valid_route(self):
        """Verifica que QAOA retorne una ruta valida."""
        best_route, best_distance, counts, _ = run_tsp_qaoa(self.distances, p=1, maxiter=25)
        self.assertIn(best_route, [[0, 1, 2, 0], [0, 2, 1, 0]])
        self.assertEqual(best_distance, 37.0)


if __name__ == "__main__":
    unittest.main()
