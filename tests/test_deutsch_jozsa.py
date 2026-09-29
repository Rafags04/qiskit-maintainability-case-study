"""Pruebas unitarias para el Algoritmo de Deutsch-Jozsa."""

import unittest
from algorithms.deutsch_jozsa import (
    build_deutsch_jozsa_oracle,
    build_deutsch_jozsa_circuit,
    run_deutsch_jozsa,
)


class TestDeutschJozsa(unittest.TestCase):
    """Casos de prueba para el algoritmo de Deutsch-Jozsa."""

    def test_constant_zero(self):
        """Verifica que una funcion constante f(x)=0 se identifique correctamente."""
        n = 3
        classification, counts, _ = run_deutsch_jozsa(n, oracle_type="constant_0", shots=512)
        self.assertEqual(classification, "constant")
        self.assertIn("000", counts)
        self.assertEqual(counts["000"], 512)

    def test_constant_one(self):
        """Verifica que una funcion constante f(x)=1 se identifique correctamente."""
        n = 3
        classification, counts, _ = run_deutsch_jozsa(n, oracle_type="constant_1", shots=512)
        self.assertEqual(classification, "constant")
        self.assertIn("000", counts)
        self.assertEqual(counts["000"], 512)

    def test_balanced_functions(self):
        """Verifica que funciones balanceadas con distintas mascaras no den '0'*n."""
        n = 4
        for mask in [1, 2, 7, 15]:
            classification, counts, _ = run_deutsch_jozsa(n, oracle_type="balanced", mask=mask, shots=512)
            self.assertEqual(classification, "balanced")
            self.assertNotIn("0000", counts)

    def test_invalid_oracle_type(self):
        """Verifica que un tipo de oraculo desconocido lance ValueError."""
        with self.assertRaises(ValueError):
            build_deutsch_jozsa_oracle(3, "invalid_type")  # type: ignore


if __name__ == "__main__":
    unittest.main()
