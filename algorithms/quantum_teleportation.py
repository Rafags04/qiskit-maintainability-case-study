"""Protocolo de Teletransportacion Cuantica (Quantum Teleportation).

Problema:
Transmitir el estado cuantico desconocido de un qubit |psi> = alpha|0> + beta|1>
desde un emisor (Alice) a un receptor distante (Bob), consumiendo un par entrelazado
de Bell (estado EPR) y transmitiendo exactamente dos bits clasicos de informacion.

Propiedad del No-Clonado:
El estado original en el qubit de Alice es destruido en el proceso de medicion,
respetando el teorema de no clonacion cuantica.

Fidelidad Cuantica:
Para verificar que el estado llego intacto a Bob, se puede aplicar la operacion inversa
de preparacion en el qubit de Bob y comprobar que colapsa a |0> con probabilidad 100%.
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
    """Construye el circuito de teletransportacion cuantica utilizando circuitos dinamicos de Qiskit.

    Args:
        theta: Angulo de rotacion en Y para preparar el estado |psi>.
        phi: Angulo de rotacion en Z para la fase relativa de |psi>.
        verify_with_inverse: Si es True, Bob aplica el inverso de la preparacion
                             y mide su qubit para confirmar fidelidad = 1 (debe dar '0').
                             Si es False, Bob mide su qubit directamente.

    Returns:
        QuantumCircuit: Circuito de teletransportacion con correcciones clasicas condicionales.
    """
    qr_alice_state = QuantumRegister(1, name="alice_psi")
    qr_alice_bell = QuantumRegister(1, name="alice_bell")
    qr_bob = QuantumRegister(1, name="bob")

    crz = ClassicalRegister(1, name="crz")  # Medicion en Z de Alice
    crx = ClassicalRegister(1, name="crx")  # Medicion en X de Alice
    cr_bob = ClassicalRegister(1, name="c_bob")  # Medicion final de Bob

    qc = QuantumCircuit(qr_alice_state, qr_alice_bell, qr_bob, crz, crx, cr_bob)

    # 1. Preparacion del estado arbitrario |psi> en Alice
    qc.ry(theta, qr_alice_state[0])
    qc.rz(phi, qr_alice_state[0])
    qc.barrier()

    # 2. Creacion del par de Bell entrelazado (|00> + |11>)/sqrt(2) entre Alice y Bob
    qc.h(qr_alice_bell[0])
    qc.cx(qr_alice_bell[0], qr_bob[0])
    qc.barrier()

    # 3. Medicion en la base de Bell por parte de Alice
    qc.cx(qr_alice_state[0], qr_alice_bell[0])
    qc.h(qr_alice_state[0])
    qc.barrier()

    qc.measure(qr_alice_state[0], crz[0])
    qc.measure(qr_alice_bell[0], crx[0])
    qc.barrier()

    # 4. Correcciones cuanticas condicionales de Bob basadas en los bits clasicos de Alice
    # Si crx == 1 -> aplicar X a Bob
    with qc.if_test((crx[0], 1)):
        qc.x(qr_bob[0])

    # Si crz == 1 -> aplicar Z a Bob
    with qc.if_test((crz[0], 1)):
        qc.z(qr_bob[0])
    qc.barrier()

    # 5. Medicion o Verificacion del estado de Bob
    if verify_with_inverse:
        # Aplicar el operador inverso de preparacion: (Rz(phi) Ry(theta))^\dagger = Ry(-theta) Rz(-phi)
        qc.rz(-phi, qr_bob[0])
        qc.ry(-theta, qr_bob[0])
        qc.measure(qr_bob[0], cr_bob[0])
    else:
        # Medir directamente el estado teletransportado
        qc.measure(qr_bob[0], cr_bob[0])

    return qc


def run_teleportation(
    theta: float = 1.2,
    phi: float = 0.5,
    verify_with_inverse: bool = True,
    shots: int = 2048,
) -> Tuple[float, Dict[str, int], QuantumCircuit]:
    """Ejecuta la simulacion del protocolo de teletransportacion cuantica.

    Args:
        theta: Parametro polar del estado de Alice.
        phi: Parametro azimutal del estado de Alice.
        verify_with_inverse: Realizar prueba de fidelidad con rotacion inversa.
        shots: Numero de tomas de simulacion.

    Returns:
        Tuple[float, Dict[str, int], QuantumCircuit]:
            - Fidelidad o probabilidad observada de coincidencia.
            - Diccionario de conteos.
            - Circuito ejecutado.
    """
    qc = build_teleportation_circuit(theta=theta, phi=phi, verify_with_inverse=verify_with_inverse)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    # En Qiskit, el resultado tiene el formato: "c_bob crx crz"
    # El bit de Bob esta en el primer bloque o posicion inicial separada por espacio
    bob_zeros = 0
    bob_ones = 0
    for key, count in counts.items():
        parts = key.split()
        # parts[0] corresponde a cr_bob
        bob_bit = parts[0]
        if bob_bit == "0":
            bob_zeros += count
        else:
            bob_ones += count

    if verify_with_inverse:
        # Si el estado es identico a |psi>, tras aplicar el inverso debe resultar '0' el 100% de las veces
        fidelity = bob_zeros / shots
    else:
        # Probabilidad de medir '0' en el estado |psi>
        p0_observed = bob_zeros / shots
        fidelity = p0_observed

    return fidelity, counts, qc


if __name__ == "__main__":
    t_angle = 1.25
    p_angle = 0.45
    print("=" * 60)
    print("EJECUCION: Protocolo de Teletransportacion Cuantica")
    print(f"Estado inicial preparado con: theta = {t_angle} rad, phi = {p_angle} rad")
    print("=" * 60)

    # 1. Prueba con verificacion de fidelidad inversa
    fid, raw_counts, circuit = run_teleportation(theta=t_angle, phi=p_angle, verify_with_inverse=True)
    print(f"Fidelidad del estado recibido por Bob: {fid * 100:.2f}% (Esperado teorico: 100%)")
    print(f"¿Teletransportacion exitosa?: {fid >= 0.99}")

    # 2. Prueba de medicion directa de la distribucion de probabilidad
    direct_p0, _, _ = run_teleportation(theta=t_angle, phi=p_angle, verify_with_inverse=False)
    expected_p0 = float(np.cos(t_angle / 2) ** 2)
    print(f"Medicion directa P(0): {direct_p0:.4f} | Esperado teorico: {expected_p0:.4f}")
    print("=" * 60)
