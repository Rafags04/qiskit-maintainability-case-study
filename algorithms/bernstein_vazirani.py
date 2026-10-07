"""Bernstein-Vazirani Algorithm.

Problem:
Given a black-box oracle function f: {0,1}^n -> {0,1} computing the binary
inner product f(x) = s · x (mod 2) for a hidden secret bitstring s of n bits,
the goal is to determine s.

Complexity:
- Classical: O(n) queries to the oracle.
- Quantum: O(1) query to the oracle (exactly 1 quantum evaluation).
"""

from typing import Dict, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_bernstein_vazirani_circuit(secret_string: str) -> QuantumCircuit:
    """Builds the quantum circuit for the Bernstein-Vazirani algorithm.

    Args:
        secret_string: Secret binary string s (e.g., '1011').

    Returns:
        QuantumCircuit: Quantum circuit configured with phase-kickback oracle and measurement.

    Raises:
        ValueError: If secret_string is empty or contains non-binary characters.
    """
    if not secret_string or not all(c in "01" for c in secret_string):
        raise ValueError(
            f"secret_string must be a non-empty string of '0' and '1'. Received: '{secret_string}'"
        )

    n = len(secret_string)
    qr_input = QuantumRegister(n, name="q_in")
    qr_ancilla = QuantumRegister(1, name="q_anc")
    cr = ClassicalRegister(n, name="c_out")
    qc = QuantumCircuit(qr_input, qr_ancilla, cr)

    # 1. Prepare ancilla qubit in the |-> state via X followed by H
    qc.x(qr_ancilla[0])
    qc.h(qr_ancilla[0])

    # 2. Apply Hadamard gates to initialize input qubits in uniform superposition |+>^n
    qc.h(qr_input)
    qc.barrier()

    # 3. Query oracle for f(x) = s · x (mod 2)
    # By convention, secret_string[i] corresponds to input qubit i (0 <= i < n)
    for i, bit in enumerate(secret_string):
        if bit == "1":
            qc.cx(qr_input[i], qr_ancilla[0])
    qc.barrier()

    # 4. Apply inverse Hadamard transform on the input register
    qc.h(qr_input)
    qc.barrier()

    # 5. Measure the input register
    qc.measure(qr_input, cr)

    return qc


def run_bernstein_vazirani(
    secret_string: str, shots: int = 1024
) -> Tuple[str, Dict[str, int], QuantumCircuit]:
    """Executes the Bernstein-Vazirani algorithm on AerSimulator.

    Args:
        secret_string: Expected secret bitstring.
        shots: Number of measurement shots.

    Returns:
        Tuple[str, Dict[str, int], QuantumCircuit]:
            - Detected secret bitstring.
            - Raw measurement counts dictionary.
            - Executed QuantumCircuit instance.
    """
    qc = build_bernstein_vazirani_circuit(secret_string)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=shots).result()
    counts = result.get_counts()

    # Retrieve most frequent measurement outcome
    most_frequent_raw = max(counts, key=counts.get)
    n = len(secret_string)

    # In Qiskit, the bit corresponding to cr[0] is at the rightmost index (n - 1 - 0).
    # Reconstruct the string following qubit i -> secret_string[i]:
    detected_string = "".join(most_frequent_raw[n - 1 - i] for i in range(n))

    return detected_string, counts, qc


if __name__ == "__main__":
    secret_test = "101101"
    print("=" * 60)
    print("EXECUTION: Bernstein-Vazirani Algorithm")
    print(f"Target secret bitstring: '{secret_test}'")
    print("=" * 60)

    found, raw_counts, circuit = run_bernstein_vazirani(secret_test)
    print(f"Measurement counts:      {raw_counts}")
    print(f"Recovered bitstring:     '{found}'")
    print(f"Exact match verified?    {found == secret_test}")
    print(f"Total circuit qubits:    {circuit.num_qubits}")
    print("=" * 60)
