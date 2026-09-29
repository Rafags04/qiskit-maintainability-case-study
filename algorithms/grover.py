"""Algoritmo de Grover (Busqueda Cuantica no Estructurada).

Problema:
Dada una base de datos no ordenada de N = 2^n elementos, encontrar uno o mas
elementos marcados w que satisfacen una condicion booleana f(w) = 1.

Complejidad:
- Clasica: O(N) consultas.
- Cuantica: O(sqrt(N)) consultas (aceleracion cuadratica optima).
"""

import math
from typing import Dict, List, Tuple, Union
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_grover_oracle(target_bitstrings: Union[str, List[str]], n: int) -> QuantumCircuit:
    """Construye el oraculo de fase de Grover que invierte el signo de los estados marcados:
    U_w |x> = (-1)^f(x) |x>.

    Args:
        target_bitstrings: Cadena o lista de cadenas binarias objetivo (ej. '101').
        n: Numero de qubits.

    Returns:
        QuantumCircuit: Subcircuito oraculo de fase.
    """
    if isinstance(target_bitstrings, str):
        targets = [target_bitstrings]
    else:
        targets = list(target_bitstrings)

    for t in targets:
        if len(t) != n or not all(c in "01" for c in t):
            raise ValueError(f"El objetivo '{t}' debe ser una cadena binaria de longitud {n}.")

    oracle = QuantumCircuit(n, name="grover_oracle")

    for target in targets:
        # En Qiskit: target[n - 1 - i] corresponde al qubit i si usamos la convencion estandar
        # Para que '101' signifique q2='1', q1='0', q0='1':
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
    """Construye el operador difusor de Grover (inversion respecto a la media):
    U_s = 2|s><s| - I = H^n (2|0><0| - I) H^n.

    Args:
        n: Numero de qubits.

    Returns:
        QuantumCircuit: Subcircuito difusor.
    """
    diffuser = QuantumCircuit(n, name="grover_diffuser")

    # 1. Aplicar Hadamard a todos los qubits
    diffuser.h(range(n))

    # 2. Aplicar compuertas X
    diffuser.x(range(n))

    # 3. Multi-controlled Z sobre |1...1>
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

    # 4. Invertir compuertas X y Hadamard
    diffuser.x(range(n))
    diffuser.h(range(n))

    return diffuser


def optimal_iterations(n: int, num_targets: int = 1) -> int:
    """Calcula el numero optimo de iteraciones de Grover:
    R = round( (pi / 4) * sqrt( 2^n / M ) ).
    """
    if num_targets <= 0:
        return 0
    theta = math.asin(math.sqrt(num_targets / (2**n)))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def build_grover_circuit(
    target_bitstrings: Union[str, List[str]],
    n: int,
    iterations: int = None,
) -> QuantumCircuit:
    """Construye el circuito completo para el algoritmo de Grover.

    Args:
        target_bitstrings: Elemento(s) objetivo a buscar.
        n: Numero de qubits.
        iterations: Numero de iteraciones (calculado automaticamente si es None).

    Returns:
        QuantumCircuit: Circuito listo para simular.
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

    # Estado inicial: superposicion uniforme |s> = H^n |0>^n
    qc.h(qr)
    qc.barrier()

    # Iteraciones del operador de Grover G = Diffuser * Oracle
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
    iterations: int = None,
) -> Tuple[str, float, Dict[str, int], QuantumCircuit]:
    """Ejecuta el algoritmo de Grover y retorna el estado de mayor probabilidad.

    Args:
        target_bitstrings: Elemento(s) marcado(s).
        n: Numero de qubits.
        shots: Numero de tomas de medicion.
        iterations: Iteraciones a ejecutar.

    Returns:
        Tuple[str, float, Dict[str, int], QuantumCircuit]:
            - Estado mas probable medido.
            - Probabilidad observada de exito.
            - Diccionario completo de conteos.
            - Circuito ejecutado.
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
    print(f"EJECUCION: Algoritmo de Grover (n = {n_qubits} qubits, N = {2**n_qubits})")
    print(f"Objetivo buscado: '{target}'")
    print(f"Iteraciones optimas teoricas: {optimal_iterations(n_qubits, 1)}")
    print("=" * 60)

    best_str, prob, all_counts, circuit = run_grover(target, n_qubits)
    print(f"Estado mas medido: '{best_str}'")
    print(f"Probabilidad de exito: {prob * 100:.2f}%")
    print(f"Distribucion de conteos: {all_counts}")
    print(f"¿Busqueda exitosa?: {best_str == target and prob > 0.9}")
    print("=" * 60)
