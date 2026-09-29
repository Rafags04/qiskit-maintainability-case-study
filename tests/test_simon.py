"""Pruebas unitarias para el Algoritmo de Simon."""

import unittest
from algorithms.simon import (
    build_simon_circuit,
    run_simon,
    solve_simon_linear_system,
)


class TestSimon(unittest.TestCase):
    """Casos de prueba para el algoritmo de Simon."""

    def test_circuit_qubits(self):
        """Verifica que el circuito tenga 2*n qubits."""
        secret = "110"
        qc = build_simon_circuit(secret)
        self.assertEqual(qc.num_qubits, 2 * len(secret))
        self.assertEqual(qc.num_clbits, len(secret))

    def test_simon_recovery_n3(self):
        """Verifica la deduccion correcta de s='110'."""
        secret = "110"
        recovered_s, counts, _ = run_simon(secret, shots=1024)
        self.assertEqual(recovered_s, secret)

    def test_simon_recovery_n2(self):
        """Verifica la deduccion de s='11'."""
        secret = "11"
        recovered_s, counts, _ = run_simon(secret, shots=1024)
        self.assertEqual(recovered_s, secret)

    def test_samples_orthogonality(self):
        """Verifica que todas las mediciones satisfagan y · s = 0 (mod 2)."""
        secret = "101"
        s_bits = [int(b) for b in secret]
        n = len(secret)
        recovered_s, counts, _ = run_simon(secret, shots=1024)
        for sample in counts:
            y_bits = [int(sample[n - 1 - i]) for i in range(n)]
            dot = sum(a * b for a, b in zip(s_bits, y_bits)) % 2
            self.assertEqual(
                dot,
                0,
                f"Muestra {sample} viola la condicion y · s = 0 (mod 2) para s={secret}",
            )


if __name__ == "__main__":
    unittest.main()
