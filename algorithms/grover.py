"""Grover's Algorithm (Unstructured Quantum Search).

Problem:
Given an unsorted search space of N = 2^n elements, locate one or more marked
items w satisfying a boolean oracle condition f(w) = 1.

Complexity:
- Classical: O(N) queries.
- Quantum: O(sqrt(N)) queries (provably optimal quadratic speedup).
"""

import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_grover_oracle(target_bitstrings: Union[str, List[str]], n: int) -> QuantumCircuit:
    """Constructs the Grover phase oracle that flips the phase of marked states:
    U_w |x> = (-1)^f(x) |x>.

    Args:
        target_bitstrings: Single target bitstring or list of target bitstrings (e.g. '101').
        n: Total number of qubits (n >= 1).

    Returns:
        QuantumCircuit: Phase oracle subcircuit.

    Raises:
        ValueError: If n < 1, targets are empty, or target length differs from n.
    """
    if n < 1:
        raise ValueError(f"Number of qubits n must be at least 1. Received: {n}")

    if isinstance(target_bitstrings, str):
        targets = [target_bitstrings]
    else:
        targets = list(target_bitstrings)

    if not targets:
        raise ValueError("Target bitstrings cannot be empty.")

    for t in targets:
        if len(t) != n or not all(c in "01" for c in t):
            raise ValueError(
                f"Target '{t}' must be a binary string of length {n} containing only '0' and '1'."
            )

    oracle = QuantumCircuit(n, name="grover_oracle")

    for target in targets:
        # In Qiskit: target[n - 1 - i] corresponds to qubit i (little-endian standard)
        for i in range(n):
            if target[n - 1 - i] == "0":
                oracle.x(i)

        # Multi-controlled Z gate
        if n == 1:
            oracle.z(0)
        elif n == 2:
            oracle.cz(0, 1)
        else:
            controls = list(range(n - 1))
            target_qubit = n - 1
            oracle.h(target_qubit)
            oracle.mcx(controls, target_qubit)
            oracle.h(target_qubit)

        for i in range(n):
            if target[n - 1 - i] == "0":
                oracle.x(i)

    return oracle


def build_grover_diffuser(n: int) -> QuantumCircuit:
    """Constructs the Grover diffusion operator (inversion about the mean):
    U_s = 2|s><s| - I = H^n (2|0><0| - I) H^n.

    Args:
        n: Number of qubits (n >= 1).

    Returns:
        QuantumCircuit: Diffuser subcircuit.

    Raises:
        ValueError: If n < 1.
    """
    if n < 1:
        raise ValueError(f"Number of qubits n must be at least 1. Received: {n}")

    diffuser = QuantumCircuit(n, name="grover_diffuser")

    # 1. Apply Hadamard gates to all qubits
    diffuser.h(range(n))

    # 2. Apply X gates to all qubits
    diffuser.x(range(n))

    # 3. Multi-controlled Z gate on |1...1>
    if n == 1:
        diffuser.z(0)
    elif n == 2:
        diffuser.cz(0, 1)
    else:
        controls = list(range(n - 1))
        target_qubit = n - 1
        diffuser.h(target_qubit)
        diffuser.mcx(controls, target_qubit)
        diffuser.h(target_qubit)

    # 4. Invert X and Hadamard gates
    diffuser.x(range(n))
    diffuser.h(range(n))

    return diffuser


def optimal_iterations(n: int, num_targets: int = 1) -> int:
    """Computes the theoretical optimal number of Grover iterations:
    R = round( (pi / 4) * sqrt( 2^n / M ) ).

    Args:
        n: Number of qubits.
        num_targets: Number of marked states M.

    Returns:
        int: Optimal iteration count R.
    """
    if num_targets <= 0 or n <= 0:
        return 0
    if num_targets >= 2**n:
        return 0
    theta = math.asin(math.sqrt(num_targets / (2**n)))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def build_grover_circuit(
    target_bitstrings: Union[str, List[str]],
    n: int,
    iterations: Optional[int] = None,
) -> QuantumCircuit:
    """Constructs the complete circuit for Grover's search algorithm.

    Args:
        target_bitstrings: Target element(s) to locate.
        n: Total number of qubits.
        iterations: Number of Grover iterations (calculated automatically if None).

    Returns:
        QuantumCircuit: Ready-to-run quantum circuit.
    """
    if isinstance(target_bitstrings, str):
        targets = [target_bitstrings]
    else:
        targets = list(target_bitstrings)

    if iterations is None:
        iterations = optimal_iterations(n, len(targets))

    oracle = build_grover_oracle(targets, n)
    diffuser = build_grover_diffuser(n)

    qr = QuantumRegister(n, name="q")
    cr = ClassicalRegister(n, name="c")
    qc = QuantumCircuit(qr, cr)

    # Initial state: uniform superposition |s> = H^n |0>^n
    qc.h(qr)
    qc.barrier()

    # Grover iterations: G = Diffuser * Oracle
    for _ in range(iterations):
        qc.compose(oracle, qubits=list(range(n)), inplace=True)
        qc.barrier()
        qc.compose(diffuser, qubits=list(range(n)), inplace=True)
        qc.barrier()

    qc.measure(qr, cr)
    return qc


def run_grover(
    target_bitstrings: Union[str, List[str]],
    n: int,
    shots: int = 2048,
    iterations: Optional[int] = None,
) -> Tuple[str, float, Dict[str, int], QuantumCircuit]:
    """Executes Grover's search algorithm and returns the highest-probability state.

    Args:
        target_bitstrings: Marked element(s).
        n: Number of qubits.
        shots: Number of measurement shots.
        iterations: Number of Grover iterations to apply.

    Returns:
        Tuple[str, float, Dict[str, int], QuantumCircuit]:
            - Most frequently measured state bitstring.
            - Total observed success probability of finding any target.
            - Complete measurement counts dictionary.
            - Executed QuantumCircuit instance.
    """
    if isinstance(target_bitstrings, str):
        targets = [target_bitstrings]
    else:
        targets = list(target_bitstrings)

    qc = build_grover_circuit(targets, n, iterations=iterations)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    best_match = max(counts, key=counts.get)
    target_counts = sum(counts.get(t, 0) for t in targets)
    success_probability = target_counts / shots

    return best_match, success_probability, counts, qc


if __name__ == "__main__":
    n_qubits = 3
    target = "101"
    print("=" * 60)
    print(f"EXECUTION: Grover's Search Algorithm (n = {n_qubits} qubits, N = {2**n_qubits})")
    print(f"Target state: '{target}'")
    print(f"Theoretical optimal iterations: {optimal_iterations(n_qubits, 1)}")
    print("=" * 60)

    best_str, prob, all_counts, circuit = run_grover(target, n_qubits)
    print(f"Most frequent measurement:   '{best_str}'")
    print(f"Observed success rate:       {prob * 100:.2f}%")
    print(f"Measurement count histogram: {all_counts}")
    print(f"Search successful?           {best_str == target and prob > 0.9}")
    print("=" * 60)
