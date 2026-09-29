"""Pruebas unitarias para el Algoritmo de Bernstein-Vazirani."""

import unittest
from algorithms.bernstein_vazirani import (
    build_bernstein_vazirani_circuit,
    run_bernstein_vazirani,
)


class TestBernsteinVazirani(unittest.TestCase):
    """Casos de prueba para el algoritmo de Bernstein-Vazirani."""

    def test_circuit_structure(self):
        """Verifica que el numero de qubits y compuertas del circuito coincida."""
        secret = "1011"
        qc = build_bernstein_vazirani_circuit(secret)
        # n qubits de entrada + 1 ancilla
        self.assertEqual(qc.num_qubits, len(secret) + 1)
        self.assertEqual(qc.num_clbits, len(secret))

    def test_reconstruction_various_secrets(self):
        """Verifica la deduccion exacta de multiples cadenas secretas."""
        test_secrets = ["0", "1", "10", "01", "1101", "101010"]
        for secret in test_secrets:
            detected, counts, _ = run_bernstein_vazirani(secret, shots=512)
            self.assertEqual(
                detected,
                secret,
                f"Fallo al recuperar '{secret}', se obtuvo '{detected}'.",
            )
            # En simulacion ideal sin ruido, el 100% de las tomas deben dar la cadena exacta
            self.assertEqual(len(counts), 1)

    def test_invalid_input_raises_error(self):
        """Verifica que entradas no binarias o vacias lancen ValueError."""
        with self.assertRaises(ValueError):
            build_bernstein_vazirani_circuit("")
        with self.assertRaises(ValueError):
            build_bernstein_vazirani_circuit("1021")


if __name__ == "__main__":
    unittest.main()
