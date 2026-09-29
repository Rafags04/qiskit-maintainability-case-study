"""Algoritmo de Shor para Factorizacion de Enteros.

Problema:
Dado un numero entero compuesto N, encontrar sus factores primos no triviales p y q
tales que N = p * q.

Reduccion al Problema del Periodo (Order Finding):
Para un entero 'a' coprimo con N (gcd(a, N) = 1), el periodo r es el menor entero positivo
tal que a^r = 1 (mod N).
Si r es par y a^(r/2) != -1 (mod N), entonces gcd(a^(r/2) - 1, N) y gcd(a^(r/2) + 1, N)
son factores no triviales de N.

Complejidad:
- Clasica: Subexponencial (Criba de Campos de Numeros General - GNFS: exp(O(n^(1/3)))).
- Cuantica: Polinomial O(n^3) donde n = log2(N) bits.
"""

from fractions import Fraction
import math
from typing import Dict, List, Optional, Set, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator


def c_amod15(a: int, power: int) -> QuantumCircuit:
    """Construye la compuerta controlada de multiplicacion modular para N = 15:
    C-U^(power) |y> = |(a^power * y) mod 15>.

    Args:
        a: Base coprima con 15 (2, 4, 7, 8, 11, 13, 14).
        power: Exponente al cual se eleva 'a'.

    Returns:
        ControlledGate: Compuerta controlada sobre 1 qubit de control + 4 qubits auxiliares.
    """
    if a not in [2, 4, 7, 8, 11, 13, 14]:
        raise ValueError(f"'a' debe ser coprimo con 15 y pertenecer a [2, 4, 7, 8, 11, 13, 14]. Recibido: {a}")

    qc = QuantumCircuit(4, name=f"{a}^{power} mod 15")
    # Reducir power modulo el orden maximo de multiplicacion en mod 15 (periodo maximo = 4)
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
    """Construye el circuito cuantico de busqueda de orden para N = 15.

    Args:
        a: Base coprima (por defecto 7).
        n_count: Numero de qubits de conteo para la fase QPE.

    Returns:
        QuantumCircuit: Circuito cuantico configurado.
    """
    qr_count = QuantumRegister(n_count, name="q_count")
    qr_work = QuantumRegister(4, name="q_work")
    cr = ClassicalRegister(n_count, name="c_phase")
    qc = QuantumCircuit(qr_count, qr_work, cr)

    # 1. Superposicion uniforme en el registro de conteo
    qc.h(qr_count)

    # 2. Inicializar el registro de trabajo en el estado |1> (binario 0001)
    qc.x(qr_work[0])
    qc.barrier()

    # 3. Exponenciacion modular controlada a^(2^j) mod 15
    for j in range(n_count):
        c_gate = c_amod15(a, 2**j)
        qc.append(c_gate, [qr_count[j]] + list(qr_work))
    qc.barrier()

    # 4. Transformada Cuantica de Fourier Inversa en el registro de conteo
    qc.append(QFTGate(n_count).inverse(), qr_count)
    qc.barrier()

    # 5. Medir el registro de conteo
    qc.measure(qr_count, cr)

    return qc


def run_shor(
    a: int = 7,
    N: int = 15,
    n_count: int = 4,
    shots: int = 1024,
) -> Tuple[Set[int], List[int], Dict[str, int], QuantumCircuit]:
    """Ejecuta el algoritmo de Shor completo (cuantico + clasico) para factorizar N = 15.

    Args:
        a: Base coprima seleccionada (ej. 7).
        N: Numero a factorizar (15).
        n_count: Precision en qubits del registro de fase.
        shots: Numero de tomas de simulacion.

    Returns:
        Tuple[Set[int], List[int], Dict[str, int], QuantumCircuit]:
            - Conjunto de factores primos no triviales encontrados (ej. {3, 5}).
            - Lista de candidatos de periodo r evaluados.
            - Diccionario de conteos de fase.
            - Circuito ejecutado.
    """
    if N != 15:
        raise NotImplementedError("La construccion de compuertas modulares de este modulo esta optimizada para N=15.")

    common_factor = math.gcd(a, N)
    if common_factor > 1:
        # Caso afortunado clasico: 'a' ya comparte un factor con N
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
        # Aproximar fase mediante fracciones continuas
        frac = Fraction(phase).limit_denominator(N)
        r_candidate = frac.denominator

        if r_candidate not in periods_tested:
            periods_tested.append(r_candidate)

        # Probar si r_candidate es un periodo valido
        # Tambien probar múltiplos por si la fraccion simplifico factores comunes
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
    print(f"EJECUCION: Algoritmo de Shor (Factorizando N = {N_test} con base a = {a_test})")
    print("=" * 60)

    factors, tested_r, raw_counts, circuit = run_shor(a=a_test, N=N_test)
    print(f"Conteos del circuito de fase: {raw_counts}")
    print(f"Periodos 'r' deducidos: {tested_r}")
    print(f"Factores no triviales hallados: {factors}")
    print(f"¿Factorizacion completa?: {factors == {3, 5}}")
    print("=" * 60)
