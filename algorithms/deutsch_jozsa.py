"""Deutsch-Jozsa Algorithm.

Problem:
Given a black-box oracle function f: {0,1}^n -> {0,1}, promised to be either
constant (returns 0 for all inputs or 1 for all inputs) or balanced (returns 0
for exactly half of the inputs and 1 for the remaining half).
The objective is to determine whether f is constant or balanced.

Complexity:
- Classical: In the worst case, requires 2^(n-1) + 1 queries.
- Quantum: Requires exactly 1 query with 100% deterministic certainty.
"""

from typing import Dict, Literal, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

OracleType = Literal["constant_0", "constant_1", "balanced"]


def build_deutsch_jozsa_oracle(n: int, oracle_type: OracleType, mask: int = 1) -> QuantumCircuit:
    """Constructs an oracle subcircuit for Deutsch-Jozsa.

    Args:
        n: Number of input qubits (n >= 1).
        oracle_type: Type of oracle ('constant_0', 'constant_1', or 'balanced').
        mask: Bitmask for the balanced oracle (1 <= mask < 2^n).

    Returns:
        QuantumCircuit: An (n + 1)-qubit circuit acting as oracle U_f.

    Raises:
        ValueError: If n < 1 or oracle_type is invalid.
    """
    if n < 1:
        raise ValueError(f"Number of qubits n must be at least 1. Received: {n}")

    oracle = QuantumCircuit(n + 1, name=f"oracle_{oracle_type}")

    if oracle_type == "constant_0":
        # f(x) = 0 for all x: Identity operation on ancilla
        pass
    elif oracle_type == "constant_1":
        # f(x) = 1 for all x: Inverts ancilla qubit (qubit n)
        oracle.x(n)
    elif oracle_type == "balanced":
        # f(x) = (mask · x) mod 2: Applies CNOT from qubits indicated by mask to ancilla
        # For any non-zero mask, exactly 2^(n-1) inputs satisfy f(x) = 1
        effective_mask = mask if (1 <= mask < (1 << n)) else 1
        for i in range(n):
            if (effective_mask >> i) & 1:
                oracle.cx(i, n)
    else:
        raise ValueError(
            f"Unknown oracle_type: '{oracle_type}'. Use 'constant_0', 'constant_1', or 'balanced'."
        )

    return oracle


def build_deutsch_jozsa_circuit(n: int, oracle: QuantumCircuit) -> QuantumCircuit:
    """Builds the complete circuit for the Deutsch-Jozsa algorithm.

    Args:
        n: Number of qubits in the input register.
        oracle: Subcircuit of (n + 1) qubits implementing function f.

    Returns:
        QuantumCircuit: Ready-to-run circuit with measurement on the input register.
    """
    if n < 1:
        raise ValueError(f"Number of qubits n must be at least 1. Received: {n}")

    qr_input = QuantumRegister(n, name="q_in")
    qr_ancilla = QuantumRegister(1, name="q_anc")
    cr = ClassicalRegister(n, name="c_out")
    qc = QuantumCircuit(qr_input, qr_ancilla, cr)

    # 1. Prepare ancilla qubit in the |-> state
    qc.x(qr_ancilla[0])
    qc.h(qr_ancilla[0])

    # 2. Prepare input register in uniform superposition |+>^n
    qc.h(qr_input)
    qc.barrier()

    # 3. Apply the oracle
    qc.compose(oracle, qubits=list(range(n + 1)), inplace=True)
    qc.barrier()

    # 4. Apply inverse Hadamard transform to input qubits
    qc.h(qr_input)
    qc.barrier()

    # 5. Measure input register
    qc.measure(qr_input, cr)

    return qc


def run_deutsch_jozsa(
    n: int,
    oracle_type: OracleType = "balanced",
    mask: int = 1,
    shots: int = 1024,
) -> Tuple[str, Dict[str, int], QuantumCircuit]:
    """Executes the Deutsch-Jozsa algorithm and classifies the oracle function.

    Args:
        n: Number of input bits.
        oracle_type: 'constant_0', 'constant_1', or 'balanced'.
        mask: Bitmask for the balanced case.
        shots: Number of simulation shots.

    Returns:
        Tuple[str, Dict[str, int], QuantumCircuit]:
            - Classification: 'constant' or 'balanced'.
            - Measurement counts obtained.
            - Executed circuit.
    """
    oracle = build_deutsch_jozsa_oracle(n, oracle_type=oracle_type, mask=mask)
    qc = build_deutsch_jozsa_circuit(n, oracle)

    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=shots).result()
    counts = result.get_counts()

    # If 100% of measurements yield '0'*n, f is constant; otherwise balanced
    all_zeros = "0" * n
    is_constant = all_zeros in counts and counts[all_zeros] == shots
    classification = "constant" if is_constant else "balanced"

    return classification, counts, qc


if __name__ == "__main__":
    n_bits = 4
    print("=" * 60)
    print(f"EXECUTION: Deutsch-Jozsa Algorithm (n = {n_bits} qubits)")
    print("=" * 60)

    for o_type in ["constant_0", "constant_1", "balanced"]:
        verdict, raw_counts, circuit = run_deutsch_jozsa(n_bits, oracle_type=o_type, mask=0b1011)
        expected = "constant" if "constant" in o_type else "balanced"
        print(
            f"Tested: {o_type:<12} | Result: {verdict:<10} | Expected: {expected:<10} | Correct: {verdict == expected}"
        )
        print(f"  Counts: {raw_counts}")

    print("=" * 60)
