"""Algoritmo de Bernstein-Vazirani.

Problema:
Dada una función oráculo tipo caja negra f: {0,1}^n -> {0,1} que calcula
el producto punto escalar binario f(x) = s · x (mod 2) para una cadena
secreta s de n bits, el objetivo es determinar s.

Complejidad:
- Clásica: O(n) consultas al oráculo.
- Cuántica: O(1) consulta al oráculo (exactamente 1 ejecución).
"""

from typing import Dict, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_bernstein_vazirani_circuit(secret_string: str) -> QuantumCircuit:
    """Construye el circuito cuántico para el algoritmo de Bernstein-Vazirani.

    Args:
        secret_string: Cadena binaria secreta s (ej. '1011').

    Returns:
        QuantumCircuit: Circuito configurado con oráculo de fase kickback y medición.
    """
    if not secret_string or not all(c in "01" for c in secret_string):
        raise ValueError(f"secret_string debe ser una cadena no vacía de '0' y '1'. Recibido: {secret_string}")

    n = len(secret_string)
    qr_input = QuantumRegister(n, name="q_in")
    qr_ancilla = QuantumRegister(1, name="q_anc")
    cr = ClassicalRegister(n, name="c_out")
    qc = QuantumCircuit(qr_input, qr_ancilla, cr)

    # 1. Preparación del estado ancilla en |->
    qc.x(qr_ancilla[0])
    qc.h(qr_ancilla[0])

    # 2. Aplicar superposición Hadamard a los qubits de entrada |+>^n
    qc.h(qr_input)
    qc.barrier()

    # 3. Oráculo para f(x) = s · x (mod 2)
    # Por convención, secret_string[i] corresponde al qubit i (0 <= i < n)
    for i, bit in enumerate(secret_string):
        if bit == "1":
            qc.cx(qr_input[i], qr_ancilla[0])
    qc.barrier()

    # 4. Transformada Hadamard inversa en el registro de entrada
    qc.h(qr_input)
    qc.barrier()

    # 5. Medición de los qubits de entrada
    qc.measure(qr_input, cr)

    return qc


def run_bernstein_vazirani(
    secret_string: str, shots: int = 1024
) -> Tuple[str, Dict[str, int], QuantumCircuit]:
    """Ejecuta el algoritmo de Bernstein-Vazirani en AerSimulator.

    Args:
        secret_string: Cadena secreta esperada.
        shots: Número de tomas de medición.

    Returns:
        Tuple[str, Dict[str, int], QuantumCircuit]:
            - Cadena secreta detectada.
            - Diccionario de conteos de medición (claves tal como las entrega Qiskit).
            - Objeto QuantumCircuit ejecutado.
    """
    qc = build_bernstein_vazirani_circuit(secret_string)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=shots).result()
    counts = result.get_counts()

    # La clave más frecuente obtenida en la medición
    most_frequent_raw = max(counts, key=counts.get)
    n = len(secret_string)

    # En Qiskit, el bit correspondiente a cr[0] se ubica a la derecha (índice n - 1).
    # Reconstruimos la cadena según la correspondencia qubit i -> secret_string[i]:
    detected_string = "".join(most_frequent_raw[n - 1 - i] for i in range(n))

    return detected_string, counts, qc


if __name__ == "__main__":
    secret_test = "101101"
    print("=" * 60)
    print("EJECUCIÓN: Algoritmo de Bernstein-Vazirani")
    print(f"Cadena secreta objetivo: '{secret_test}'")
    print("=" * 60)

    found, raw_counts, circuit = run_bernstein_vazirani(secret_test)
    print(f"Conteos obtenidos: {raw_counts}")
    print(f"Cadena recuperada:       '{found}'")
    print(f"¿Coincidencia exitosa?   {found == secret_test}")
    print(f"Número total de qubits:  {circuit.num_qubits}")
    print("=" * 60)
