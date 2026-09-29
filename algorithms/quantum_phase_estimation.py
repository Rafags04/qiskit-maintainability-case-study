"""Algoritmo de Estimacion Cuantica de Fase (Quantum Phase Estimation - QPE).

Problema:
Dada una operacion unitaria U y uno de sus estados propios |psi> tal que:
    U |psi> = e^(2*pi*i*theta) |psi>   con theta in [0, 1)
el objetivo es estimar el valor del parametro de fase theta con m bits de precision.

Complejidad:
- Fundamental para algoritmos cuanticos exponenciales como el Algoritmo de Shor
  y algoritmos de quimica cuantica / simulacion hamiltoniana.
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
    """Construye el circuito de Estimacion Cuantica de Fase para un operador de fase P(2*pi*theta)
    con estado propio |1>.

    Args:
        theta: Fase verdadera a estimar (en el rango [0, 1)).
        num_counting_qubits: Numero m de qubits en el registro de conteo (precision = 2^-m).

    Returns:
        QuantumCircuit: Circuito listo para simular.
    """
    if not (0.0 <= theta < 1.0):
        # Normalizar theta al rango [0, 1)
        theta = theta % 1.0

    m = num_counting_qubits
    qr_count = QuantumRegister(m, name="q_count")
    qr_target = QuantumRegister(1, name="q_target")
    cr = ClassicalRegister(m, name="c_out")
    qc = QuantumCircuit(qr_count, qr_target, cr)

    # 1. Preparar el estado propio |psi> = |1> en el qubit objetivo
    qc.x(qr_target[0])

    # 2. Inicializar el registro de conteo en superposicion uniforme |+>^m
    qc.h(qr_count)
    qc.barrier()

    # 3. Aplicar operaciones unitarias controladas C-U^(2^j)
    # U = PhaseGate(lambda) con lambda = 2 * pi * theta
    # U^(2^j) = PhaseGate(2^j * 2 * pi * theta)
    angle = 2 * np.pi * theta
    for j in range(m):
        power = 2**j
        qc.cp(angle * power, qr_count[j], qr_target[0])
    qc.barrier()

    # 4. Transformada Cuantica de Fourier Inversa (QFT^\dagger) sobre el registro de conteo
    qc.append(QFTGate(m).inverse(), qr_count)
    qc.barrier()

    # 5. Medicion del registro de conteo
    qc.measure(qr_count, cr)

    return qc


def run_qpe(
    theta: float,
    num_counting_qubits: int = 3,
    shots: int = 1024,
) -> Tuple[float, float, str, Dict[str, int], QuantumCircuit]:
    """Ejecuta QPE y estima la fase theta a partir del conteo mas frecuente.

    Args:
        theta: Fase verdadera en [0, 1).
        num_counting_qubits: Qubits de medicion (m).
        shots: Numero de tomas de medicion.

    Returns:
        Tuple[float, float, str, Dict[str, int], QuantumCircuit]:
            - Fase estimada (theta_est).
            - Error absoluto (|theta - theta_est|).
            - Cadena binaria dominante.
            - Diccionario de conteos.
            - Circuito ejecutado.
    """
    qc = build_qpe_circuit(theta, num_counting_qubits=num_counting_qubits)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    best_bitstring = max(counts, key=counts.get)
    decimal_val = int(best_bitstring, 2)
    theta_estimated = decimal_val / (2**num_counting_qubits)
    error = abs(theta - theta_estimated)

    return theta_estimated, error, best_bitstring, counts, qc


if __name__ == "__main__":
    test_cases = [
        (0.5, 3),      # 1/2 = 4/8 -> bitstring '100'
        (0.125, 3),    # 1/8 = 1/8 -> bitstring '001'
        (0.625, 4),    # 5/8 = 10/16 -> bitstring '1010'
        (0.33333, 4),  # 1/3 ~ 5/16 = 0.3125
    ]

    print("=" * 65)
    print("EJECUCION: Algoritmo de Estimacion Cuantica de Fase (QPE)")
    print("=" * 65)

    for true_theta, m_qubits in test_cases:
        est, err, bitstr, raw_counts, circuit = run_qpe(true_theta, num_counting_qubits=m_qubits)
        print(f"Theta real: {true_theta:<8.5f} | m={m_qubits} | Binario: '{bitstr}' | Estimado: {est:.5f} | Error: {err:.5f}")

    print("=" * 65)
