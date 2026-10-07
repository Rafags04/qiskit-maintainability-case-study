"""Quantum Teleportation Protocol.

Problem:
Transmit an unknown quantum state |psi> = alpha|0> + beta|1> from a sender (Alice)
to a distant receiver (Bob) by consuming one shared entangled Bell pair (EPR pair)
and communicating exactly two classical bits of information.

No-Cloning Theorem:
The original quantum state in Alice's qubit is destroyed during Bell-state measurement,
strictly upholding the quantum no-cloning theorem.

Quantum Fidelity:
To verify that Bob's received qubit is identical to |psi>, Bob can apply the inverse
of the state-preparation operator and measure in the computational basis. Perfect
teleportation yields outcome '0' with 100% fidelity.
"""

from typing import Dict, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_teleportation_circuit(
    theta: float = 1.2,
    phi: float = 0.5,
    verify_with_inverse: bool = True,
) -> QuantumCircuit:
    """Builds the quantum teleportation circuit using modern dynamic circuits in Qiskit.

    Args:
        theta: Polar rotation angle around Y for state preparation of |psi>.
        phi: Azimuthal rotation angle around Z for the relative phase of |psi>.
        verify_with_inverse: If True, Bob applies the inverse preparation unitary
                             and measures to verify fidelity = 1.0 (yielding outcome '0').
                             If False, Bob measures the teleported state directly.

    Returns:
        QuantumCircuit: Teleportation circuit with feed-forward conditional operations.
    """
    qr_alice_state = QuantumRegister(1, name="alice_psi")
    qr_alice_bell = QuantumRegister(1, name="alice_bell")
    qr_bob = QuantumRegister(1, name="bob")

    crz = ClassicalRegister(1, name="crz")  # Alice's Z-measurement
    crx = ClassicalRegister(1, name="crx")  # Alice's X-measurement
    cr_bob = ClassicalRegister(1, name="c_bob")  # Bob's final measurement

    qc = QuantumCircuit(qr_alice_state, qr_alice_bell, qr_bob, crz, crx, cr_bob)

    # 1. Prepare arbitrary state |psi> on Alice's qubit
    qc.ry(theta, qr_alice_state[0])
    qc.rz(phi, qr_alice_state[0])
    qc.barrier()

    # 2. Create entangled Bell pair (|00> + |11>)/sqrt(2) between Alice and Bob
    qc.h(qr_alice_bell[0])
    qc.cx(qr_alice_bell[0], qr_bob[0])
    qc.barrier()

    # 3. Bell-basis measurement by Alice
    qc.cx(qr_alice_state[0], qr_alice_bell[0])
    qc.h(qr_alice_state[0])
    qc.barrier()

    qc.measure(qr_alice_state[0], crz[0])
    qc.measure(qr_alice_bell[0], crx[0])
    qc.barrier()

    # 4. Conditional feed-forward quantum corrections applied by Bob
    # If crx == 1 -> apply X to Bob's qubit
    with qc.if_test((crx[0], 1)):
        qc.x(qr_bob[0])

    # If crz == 1 -> apply Z to Bob's qubit
    with qc.if_test((crz[0], 1)):
        qc.z(qr_bob[0])
    qc.barrier()

    # 5. Bob's state verification or direct measurement
    if verify_with_inverse:
        # Inverse of state preparation: (Rz(phi) Ry(theta))^\dagger = Ry(-theta) Rz(-phi)
        qc.rz(-phi, qr_bob[0])
        qc.ry(-theta, qr_bob[0])
        qc.measure(qr_bob[0], cr_bob[0])
    else:
        # Direct measurement in computational basis
        qc.measure(qr_bob[0], cr_bob[0])

    return qc


def run_teleportation(
    theta: float = 1.2,
    phi: float = 0.5,
    verify_with_inverse: bool = True,
    shots: int = 2048,
) -> Tuple[float, Dict[str, int], QuantumCircuit]:
    """Executes the simulation of the quantum teleportation protocol.

    Args:
        theta: Polar parameter of Alice's prepared state.
        phi: Azimuthal parameter of Alice's prepared state.
        verify_with_inverse: Whether to perform inverse-rotation fidelity verification.
        shots: Number of simulation shots.

    Returns:
        Tuple[float, Dict[str, int], QuantumCircuit]:
            - Observed transmission fidelity or state probability.
            - Full measurement counts dictionary.
            - Executed circuit.
    """
    qc = build_teleportation_circuit(theta=theta, phi=phi, verify_with_inverse=verify_with_inverse)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    # Parse Bob's measured bit.
    # In Qiskit, registers are ordered from last added to first added (space-separated: "c_bob crx crz").
    bob_zeros = 0
    bob_ones = 0
    for key, count in counts.items():
        parts = key.split()
        # If space-separated, parts[0] corresponds to cr_bob.
        # Otherwise, the leftmost character key[0] corresponds to the highest register index (cr_bob).
        bob_bit = parts[0] if len(parts) > 1 else key[0]
        if bob_bit == "0":
            bob_zeros += count
        else:
            bob_ones += count

    if verify_with_inverse:
        # If teleportation succeeded, inverse operation collapses state to |0> with probability 1
        fidelity = bob_zeros / shots
    else:
        # Observed probability of measuring '0'
        fidelity = bob_zeros / shots

    return fidelity, counts, qc


if __name__ == "__main__":
    t_angle = 1.25
    p_angle = 0.45
    print("=" * 60)
    print("EXECUTION: Quantum Teleportation Protocol")
    print(f"Prepared state angles: theta = {t_angle} rad, phi = {p_angle} rad")
    print("=" * 60)

    # 1. Inverse verification for state fidelity
    fid, raw_counts, circuit = run_teleportation(
        theta=t_angle, phi=p_angle, verify_with_inverse=True
    )
    print(f"Bob's state fidelity:     {fid * 100:.2f}% (Theoretical: 100%)")
    print(f"Teleportation successful? {fid >= 0.99}")

    # 2. Direct measurement distribution check
    direct_p0, _, _ = run_teleportation(
        theta=t_angle, phi=p_angle, verify_with_inverse=False
    )
    expected_p0 = float(np.cos(t_angle / 2) ** 2)
    print(f"Direct P(0) observed:     {direct_p0:.4f} | Theoretical: {expected_p0:.4f}")
    print("=" * 60)
