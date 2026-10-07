"""Unit tests for Simon's algorithm."""

import unittest
from algorithms.simon import (
    build_simon_oracle,
    build_simon_circuit,
    run_simon,
    solve_simon_linear_system,
)


class TestSimon(unittest.TestCase):
    """Test suite for Simon's algorithm."""

    def test_circuit_qubits(self):
        """Verifies that the circuit allocates 2*n qubits and n classical bits."""
        secret = "110"
        qc = build_simon_circuit(secret)
        self.assertEqual(qc.num_qubits, 2 * len(secret))
        self.assertEqual(qc.num_clbits, len(secret))

    def test_simon_recovery_n3(self):
        """Verifies correct deduction of s='110'."""
        secret = "110"
        recovered_s, counts, _ = run_simon(secret, shots=1024)
        self.assertEqual(recovered_s, secret)

    def test_simon_recovery_n2(self):
        """Verifies correct deduction of s='11'."""
        secret = "11"
        recovered_s, counts, _ = run_simon(secret, shots=1024)
        self.assertEqual(recovered_s, secret)

    def test_simon_all_zero_secret_injective_function(self):
        """Verifies correct deduction of s='000' for an injective (1-to-1) function."""
        secret = "000"
        recovered_s, counts, _ = run_simon(secret, shots=1024)
        self.assertEqual(recovered_s, secret)

    def test_samples_orthogonality(self):
        """Verifies that all measured samples satisfy y * s = 0 (mod 2)."""
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
                f"Sample {sample} violates the condition y * s = 0 (mod 2) for s={secret}",
            )

    def test_invalid_secret_raises_error(self):
        """Verifies that invalid or empty secrets raise ValueError."""
        with self.assertRaises(ValueError):
            build_simon_oracle("")
        with self.assertRaises(ValueError):
            build_simon_oracle("102")


if __name__ == "__main__":
    unittest.main()
