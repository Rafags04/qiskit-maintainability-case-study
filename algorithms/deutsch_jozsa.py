"""Algoritmo de Deutsch-Jozsa.

Problema:
Dada una funcion oraculo f: {0,1}^n -> {0,1}, prometida ser o bien constante
(devuelve 0 para todas las entradas o 1 para todas) o bien balanceada
(devuelve 0 para exactamente la mitad de las entradas y 1 para la otra mitad).
El objetivo es determinar si f es constante o balanceada.

Complejidad:
- Clasica: Requiere en el peor caso 2^(n-1) + 1 consultas.
- Cuantica: Requiere exactamente 1 consulta con 100% de certeza.
"""

from typing import Dict, Literal, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

OracleType = Literal["constant_0", "constant_1", "balanced"]


def build_deutsch_jozsa_oracle(n: int, oracle_type: OracleType, mask: int = 1) -> QuantumCircuit:
    """Construye un subcircuito oraculo para Deutsch-Jozsa.

    Args:
        n: Numero de qubits de entrada.
        oracle_type: Tipo de oraculo ('constant_0', 'constant_1', 'balanced').
        mask: Mascara de bits para oraculo balanceado (1 <= mask < 2^n).

    Returns:
        QuantumCircuit: Circuito de (n + 1) qubits que actua como oraculo U_f.
    """
    oracle = QuantumCircuit(n + 1, name=f"oracle_{oracle_type}")

    if oracle_type == "constant_0":
        # f(x) = 0 para todo x: No se aplica ninguna compuerta al qubit ancilla
        pass
    elif oracle_type == "constant_1":
        # f(x) = 1 para todo x: Invierte el qubit ancilla (qubit n)
        oracle.x(n)
    elif oracle_type == "balanced":
        # f(x) = (mask · x) mod 2: Aplica CNOT desde los qubits indicados en mask hacia el ancilla
        # Para cualquier mask != 0, exactamente la mitad de los 2^n estados tienen f(x) = 1
        effective_mask = mask if (1 <= mask < (1 << n)) else 1
        for i in range(n):
            if (effective_mask >> i) & 1:
                oracle.cx(i, n)
    else:
        raise ValueError(f"oracle_type desconocido: '{oracle_type}'. Use 'constant_0', 'constant_1' o 'balanced'.")

    return oracle


def build_deutsch_jozsa_circuit(n: int, oracle: QuantumCircuit) -> QuantumCircuit:
    """Construye el circuito completo para el algoritmo de Deutsch-Jozsa.

    Args:
        n: Numero de qubits del registro de entrada.
        oracle: Subcircuito de (n + 1) qubits correspondiente a la funcion f.

    Returns:
        QuantumCircuit: Circuito listo para ejecucion con medicion en el registro de entrada.
    """
    qr_input = QuantumRegister(n, name="q_in")
    qr_ancilla = QuantumRegister(1, name="q_anc")
    cr = ClassicalRegister(n, name="c_out")
    qc = QuantumCircuit(qr_input, qr_ancilla, cr)

    # 1. Preparacion del ancilla en el estado |->
    qc.x(qr_ancilla[0])
    qc.h(qr_ancilla[0])

    # 2. Superposicion en los qubits de entrada |+>^n
    qc.h(qr_input)
    qc.barrier()

    # 3. Aplicacion del oraculo
    qc.compose(oracle, qubits=list(range(n + 1)), inplace=True)
    qc.barrier()

    # 4. Transformada Hadamard inversa en qubits de entrada
    qc.h(qr_input)
    qc.barrier()

    # 5. Medicion del registro de entrada
    qc.measure(qr_input, cr)

    return qc


def run_deutsch_jozsa(
    n: int,
    oracle_type: OracleType = "balanced",
    mask: int = 1,
    shots: int = 1024,
) -> Tuple[str, Dict[str, int], QuantumCircuit]:
    """Ejecuta el algoritmo de Deutsch-Jozsa y clasifica la funcion.

    Args:
        n: Numero de bits de entrada.
        oracle_type: 'constant_0', 'constant_1' o 'balanced'.
        mask: Mascara para el caso balanceado.
        shots: Numero de tomas de simulacion.

    Returns:
        Tuple[str, Dict[str, int], QuantumCircuit]:
            - Clasificacion: 'constant' o 'balanced'.
            - Conteos de medicion obtenidos.
            - Circuito ejecutado.
    """
    oracle = build_deutsch_jozsa_oracle(n, oracle_type=oracle_type, mask=mask)
    qc = build_deutsch_jozsa_circuit(n, oracle)

    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=shots).result()
    counts = result.get_counts()

    # Si todas las mediciones dan '0'*n, f es constante; de lo contrario es balanceada
    all_zeros = "0" * n
    is_constant = all_zeros in counts and counts[all_zeros] == shots
    classification = "constant" if is_constant else "balanced"

    return classification, counts, qc


if __name__ == "__main__":
    n_bits = 4
    print("=" * 60)
    print(f"EJECUCION: Algoritmo de Deutsch-Jozsa (n = {n_bits} qubits)")
    print("=" * 60)

    for o_type in ["constant_0", "constant_1", "balanced"]:
        verdict, raw_counts, circuit = run_deutsch_jozsa(n_bits, oracle_type=o_type, mask=0b1011)
        expected = "constant" if "constant" in o_type else "balanced"
        print(f"Tipo probado: {o_type:<12} | Resultado: {verdict:<10} | Esperado: {expected:<10} | Correcto: {verdict == expected}")
        print(f"  Conteos: {raw_counts}")

    print("=" * 60)
