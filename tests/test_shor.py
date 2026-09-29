"""Pruebas unitarias para el Algoritmo de Shor."""

import unittest
from algorithms.shor import (
    c_amod15,
    build_shor_circuit,
    run_shor,
)


class TestShor(unittest.TestCase):
    """Casos de prueba para el algoritmo de Shor."""

    def test_modular_multiplication_gate_creation(self):
        """Verifica la construccion de la compuerta C-U de multiplicacion modular."""
        gate = c_amod15(7, 1)
        self.assertEqual(gate.num_qubits, 5)  # 1 control + 4 trabajo

    def test_invalid_base_raises_error(self):
        """Verifica que una base no coprima o no admitida lance ValueError."""
        with self.assertRaises(ValueError):
            c_amod15(3, 1)  # 3 no es coprimo con 15

    def test_circuit_qubits(self):
        """Verifica que el circuito tenga n_count + 4 qubits de trabajo."""
        qc = build_shor_circuit(a=7, n_count=4)
        self.assertEqual(qc.num_qubits, 8)
        self.assertEqual(qc.num_clbits, 4)

    def test_factorization_N15_with_base7(self):
        """Verifica que la ejecucion completa del algoritmo factorice 15 en {3, 5} con base 7."""
        factors, periods, counts, _ = run_shor(a=7, N=15, n_count=4, shots=1024)
        self.assertIn(4, periods)  # El periodo teorico de 7 mod 15 es 4
        self.assertTrue({3, 5}.issubset(factors))

    def test_factorization_N15_with_base2(self):
        """Verifica la factorizacion con base 2."""
        factors, periods, counts, _ = run_shor(a=2, N=15, n_count=4, shots=1024)
        self.assertIn(4, periods)  # El periodo teorico de 2 mod 15 es 4
        self.assertTrue({3, 5}.issubset(factors))


if __name__ == "__main__":
    unittest.main()
