"""Shor's Algorithm for Integer Factorization.

Problem:
Given a composite integer N, find its non-trivial prime factors p and q
such that N = p * q.

Reduction to Order Finding:
For an integer 'a' coprime to N (gcd(a, N) = 1), the order (period) r is the
smallest positive integer such that a^r = 1 (mod N).
If r is even and a^(r/2) != -1 (mod N), then gcd(a^(r/2) - 1, N) and
gcd(a^(r/2) + 1, N) yield non-trivial factors of N.

Complexity:
- Classical: Subexponential (General Number Field Sieve - GNFS: exp(O(n^(1/3)))).
- Quantum: Polynomial O(n^3) where n = log2(N) bits.
"""

from fractions import Fraction
import math
from typing import Dict, List, Optional, Set, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator


def c_amod15(a: int, power: int) -> QuantumCircuit:
    """Constructs the controlled modular multiplication gate for N = 15:
    C-U^(power) |y> = |(a^power * y) mod 15>.

    Args:
        a: Base coprime to 15 (2, 4, 7, 8, 11, 13, 14).
        power: Exponent to which 'a' is raised.

    Returns:
        ControlledGate: Controlled gate over 1 control qubit + 4 work qubits.

    Raises:
        ValueError: If 'a' is not coprime to 15 or not in the supported list.
    """
    if a not in [2, 4, 7, 8, 11, 13, 14]:
        raise ValueError(
            f"'a' must be coprime to 15 and belong to [2, 4, 7, 8, 11, 13, 14]. Received: {a}"
        )

    qc = QuantumCircuit(4, name=f"{a}^{power} mod 15")
    # Reduce power modulo the maximum order in mod 15 (maximum order = 4)
    effective_power = power % 4

    for _ in range(effective_power):
        if a in [2, 13]:
            qc.swap(2, 3)
            qc.swap(1, 2)
            qc.swap(0, 1)
        elif a in [7, 8]:
            qc.swap(0, 1)
            qc.swap(1, 2)
            qc.swap(2, 3)
        elif a in [4, 11]:
            qc.swap(1, 3)
            qc.swap(0, 2)
        elif a == 14:
            qc.swap(0, 3)
            qc.swap(1, 2)

        if a in [7, 11, 13, 14]:
            for q in range(4):
                qc.x(q)

    gate = qc.to_gate()
    return gate.control(1)


def build_shor_circuit(a: int = 7, n_count: int = 4) -> QuantumCircuit:
    """Builds the quantum order-finding circuit for N = 15.

    Args:
        a: Coprime base (default 7).
        n_count: Number of counting qubits for the QPE phase register.

    Returns:
        QuantumCircuit: Configured quantum circuit.

    Raises:
        ValueError: If n_count < 1.
    """
    if n_count < 1:
        raise ValueError(f"n_count must be at least 1. Received: {n_count}")

    qr_count = QuantumRegister(n_count, name="q_count")
    qr_work = QuantumRegister(4, name="q_work")
    cr = ClassicalRegister(n_count, name="c_phase")
    qc = QuantumCircuit(qr_count, qr_work, cr)

    # 1. Initialize counting register in uniform superposition
    qc.h(qr_count)

    # 2. Initialize work register to computational basis state |1> (binary 0001)
    qc.x(qr_work[0])
    qc.barrier()

    # 3. Controlled modular exponentiation a^(2^j) mod 15
    for j in range(n_count):
        c_gate = c_amod15(a, 2**j)
        qc.append(c_gate, [qr_count[j]] + list(qr_work))
    qc.barrier()

    # 4. Inverse Quantum Fourier Transform on counting register
    qc.append(QFTGate(n_count).inverse(), qr_count)
    qc.barrier()

    # 5. Measure counting register
    qc.measure(qr_count, cr)

    return qc


def run_shor(
    a: int = 7,
    N: int = 15,
    n_count: int = 4,
    shots: int = 1024,
) -> Tuple[Set[int], List[int], Dict[str, int], QuantumCircuit]:
    """Executes the full Shor algorithm (quantum order-finding + classical post-processing) for N = 15.

    Args:
        a: Chosen coprime base (e.g. 7).
        N: Number to factor (15).
        n_count: Phase register precision in qubits.
        shots: Number of simulation shots.

    Returns:
        Tuple[Set[int], List[int], Dict[str, int], QuantumCircuit]:
            - Set of non-trivial prime factors found (e.g. {3, 5}).
            - List of candidate periods r evaluated.
            - Phase register measurement counts.
            - Executed circuit.

    Raises:
        NotImplementedError: If N != 15.
    """
    if N != 15:
        raise NotImplementedError(
            "Modular exponentiation gates in this implementation are compiled for N=15."
        )

    common_factor = math.gcd(a, N)
    if common_factor > 1:
        # Classical lucky case: 'a' already shares a non-trivial factor with N
        factors = {common_factor, N // common_factor}
        qc = QuantumCircuit(1)
        return factors, [1], {}, qc

    qc = build_shor_circuit(a=a, n_count=n_count)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    factors_found: Set[int] = set()
    periods_tested: List[int] = []

    for bitstring in counts:
        decimal = int(bitstring, 2)
        phase = decimal / (2**n_count)
        # Approximate phase using continued fractions expansion
        frac = Fraction(phase).limit_denominator(N)
        r_candidate = frac.denominator

        if r_candidate not in periods_tested:
            periods_tested.append(r_candidate)

        # Test if r_candidate or its double is the true period
        for mult in [1, 2]:
            r = r_candidate * mult
            if pow(a, r, N) == 1 and (r % 2 == 0):
                half_power = pow(a, r // 2, N)
                if half_power != N - 1:  # a^(r/2) != -1 (mod N)
                    f1 = math.gcd(half_power - 1, N)
                    f2 = math.gcd(half_power + 1, N)
                    if 1 < f1 < N:
                        factors_found.add(f1)
                    if 1 < f2 < N:
                        factors_found.add(f2)

    return factors_found, periods_tested, counts, qc


if __name__ == "__main__":
    N_test = 15
    a_test = 7
    print("=" * 60)
    print(f"EXECUTION: Shor's Algorithm (Factoring N = {N_test} with base a = {a_test})")
    print("=" * 60)

    factors, tested_r, raw_counts, circuit = run_shor(a=a_test, N=N_test)
    print(f"Phase circuit counts:      {raw_counts}")
    print(f"Tested periods 'r':        {tested_r}")
    print(f"Non-trivial factors found: {factors}")
    print(f"Factorization complete?    {factors == {3, 5}}")
    print("=" * 60)
