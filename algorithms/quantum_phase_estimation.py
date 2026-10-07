"""Quantum Phase Estimation (QPE) Algorithm.

Problem:
Given a unitary operator U and an eigenstate |psi> such that:
    U |psi> = e^(2*pi*i*theta) |psi>   with theta in [0, 1)
the goal is to estimate the phase parameter theta with m bits of precision.

Complexity:
- Foundational quantum algorithmic primitive for Shor's factoring algorithm,
  HHL (linear systems solver), quantum chemistry, and Hamiltonian simulation.
"""

from typing import Dict, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator


def build_qpe_circuit(
    theta: float,
    num_counting_qubits: int = 3,
) -> QuantumCircuit:
    """Constructs the Quantum Phase Estimation circuit for a phase gate P(2*pi*theta)
    with eigenstate |1>.

    Args:
        theta: True phase to estimate (in range [0, 1)).
        num_counting_qubits: Number m of counting qubits (precision = 2^-m, m >= 1).

    Returns:
        QuantumCircuit: Quantum circuit configured for simulation.

    Raises:
        ValueError: If num_counting_qubits < 1.
    """
    if num_counting_qubits < 1:
        raise ValueError(
            f"num_counting_qubits must be at least 1. Received: {num_counting_qubits}"
        )

    # Normalize theta to [0, 1)
    theta = theta % 1.0

    m = num_counting_qubits
    qr_count = QuantumRegister(m, name="q_count")
    qr_target = QuantumRegister(1, name="q_target")
    cr = ClassicalRegister(m, name="c_out")
    qc = QuantumCircuit(qr_count, qr_target, cr)

    # 1. Prepare target eigenstate |psi> = |1>
    qc.x(qr_target[0])

    # 2. Initialize counting register in uniform superposition |+>^m
    qc.h(qr_count)
    qc.barrier()

    # 3. Apply controlled unitary operations C-U^(2^j)
    # Here U = PhaseGate(2*pi*theta), hence U^(2^j) = PhaseGate(2^j * 2*pi*theta)
    angle = 2 * np.pi * theta
    for j in range(m):
        power = 2**j
        qc.cp(angle * power, qr_count[j], qr_target[0])
    qc.barrier()

    # 4. Apply inverse Quantum Fourier Transform (QFT^\dagger) to counting register
    qc.append(QFTGate(m).inverse(), qr_count)
    qc.barrier()

    # 5. Measure counting register
    qc.measure(qr_count, cr)

    return qc


def run_qpe(
    theta: float,
    num_counting_qubits: int = 3,
    shots: int = 1024,
) -> Tuple[float, float, str, Dict[str, int], QuantumCircuit]:
    """Executes QPE and estimates the phase theta from the most frequent bitstring.

    Args:
        theta: True phase in [0, 1).
        num_counting_qubits: Number of measurement qubits (m).
        shots: Number of measurement shots.

    Returns:
        Tuple[float, float, str, Dict[str, int], QuantumCircuit]:
            - Estimated phase (theta_est).
            - Absolute estimation error (|theta - theta_est|).
            - Dominant bitstring measured.
            - Full measurement counts dictionary.
            - Executed circuit.
    """
    qc = build_qpe_circuit(theta, num_counting_qubits=num_counting_qubits)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    best_bitstring = max(counts, key=counts.get)
    decimal_val = int(best_bitstring, 2)
    theta_estimated = decimal_val / (2**num_counting_qubits)
    error = abs((theta % 1.0) - theta_estimated)

    return theta_estimated, error, best_bitstring, counts, qc


if __name__ == "__main__":
    test_cases = [
        (0.5, 3),      # 1/2 = 4/8 -> bitstring '100'
        (0.125, 3),    # 1/8 = 1/8 -> bitstring '001'
        (0.625, 4),    # 5/8 = 10/16 -> bitstring '1010'
        (0.33333, 4),  # 1/3 ~ 5/16 = 0.3125
    ]

    print("=" * 65)
    print("EXECUTION: Quantum Phase Estimation (QPE)")
    print("=" * 65)

    for true_theta, m_qubits in test_cases:
        est, err, bitstr, raw_counts, circuit = run_qpe(true_theta, num_counting_qubits=m_qubits)
        print(
            f"True theta: {true_theta:<8.5f} | m={m_qubits} | Binary: '{bitstr}' | "
            f"Estimated: {est:.5f} | Error: {err:.5f}"
        )

    print("=" * 65)
