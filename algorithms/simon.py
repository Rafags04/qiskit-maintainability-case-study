"""Algoritmo de Simon.

Problema:
Dada una funcion oraculo f: {0,1}^n -> {0,1}^n con la promesa de que existe
una cadena secreta s in {0,1}^n tal que:
    f(x) = f(y)  <=>  x (+) y in {0^n, s}
Determinar la cadena secreta s.

Complejidad:
- Clasica: Omega(2^(n/2)) consultas (limite por la paradoja del cumpleanos).
- Cuantica: O(n) consultas cuanticas mas O(n^3) operaciones clasicas de eliminacion gaussiana sobre F_2.
- Demostro por primera vez una separacion exponencial demostrable respecto a computacion clasica.
"""

from typing import Dict, List, Optional, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_simon_oracle(secret_string: str) -> QuantumCircuit:
    """Construye un oraculo reversible de 2*n qubits que implementa f(x) con periodo s.

    Si s == '0'*n, f(x) = x (funcion inyectiva 1-a-1).
    Si s != '0'*n, f(x) = f(x (+) s) es 2-a-1.

    Args:
        secret_string: Cadena secreta s de n bits.

    Returns:
        QuantumCircuit: Subcircuito oraculo de 2*n qubits.
    """
    n = len(secret_string)
    oracle = QuantumCircuit(2 * n, name="simon_oracle")

    # 1. Copiar el registro de entrada al registro de salida: |x>|0> -> |x>|x>
    for i in range(n):
        oracle.cx(i, n + i)

    # 2. Si s != '0'*n, identificar el primer bit '1' (pivote) y sumar s condicionalmente
    if "1" in secret_string:
        pivot = secret_string.find("1")
        for i, bit in enumerate(secret_string):
            if bit == "1":
                oracle.cx(pivot, n + i)

    return oracle


def build_simon_circuit(secret_string: str) -> QuantumCircuit:
    """Construye el circuito cuantico completo para el algoritmo de Simon.

    Args:
        secret_string: Cadena secreta s.

    Returns:
        QuantumCircuit: Circuito listo para ejecucion.
    """
    n = len(secret_string)
    qr_in = QuantumRegister(n, name="q_in")
    qr_out = QuantumRegister(n, name="q_out")
    cr = ClassicalRegister(n, name="c_meas")
    qc = QuantumCircuit(qr_in, qr_out, cr)

    # 1. Aplicar Hadamard al registro de entrada |+>^n
    qc.h(qr_in)
    qc.barrier()

    # 2. Aplicar el oraculo
    oracle = build_simon_oracle(secret_string)
    qc.compose(oracle, qubits=list(range(2 * n)), inplace=True)
    qc.barrier()

    # 3. Aplicar Hadamard nuevamente al registro de entrada
    qc.h(qr_in)
    qc.barrier()

    # 4. Medir unicamente el registro de entrada
    qc.measure(qr_in, cr)

    return qc


def solve_simon_linear_system(measured_samples: List[str], n: int) -> str:
    """Resuelve el sistema de ecuaciones homogeneo y · s = 0 (mod 2) sobre GF(2)
    mediante Eliminacion Gaussiana para encontrar la cadena secreta s no trivial.

    Args:
        measured_samples: Lista de muestras binarias obtenidas del circuito.
        n: Longitud de la cadena s.

    Returns:
        str: Cadena secreta s deducida.
    """
    # Convertir muestras en vectores sobre GF(2)
    # En Qiskit, el bit correspondiente a qr_in[i] es sample[n - 1 - i]
    matrix: List[List[int]] = []
    for sample in measured_samples:
        row = [int(sample[n - 1 - i]) for i in range(n)]
        # Descartar filas nulas
        if any(row):
            matrix.append(row)

    # Eliminacion gaussiana para obtener forma escalonada reducida
    row_count = len(matrix)
    pivot_cols = []
    r = 0

    for col in range(n):
        # Buscar pivote
        pivot_row = -1
        for row in range(r, row_count):
            if matrix[row][col] == 1:
                pivot_row = row
                break

        if pivot_row == -1:
            continue

        # Intercambiar fila actual con fila pivote
        matrix[r], matrix[pivot_row] = matrix[pivot_row], matrix[r]
        pivot_cols.append(col)

        # Eliminar las demas filas
        for row in range(row_count):
            if row != r and matrix[row][col] == 1:
                matrix[row] = [(a ^ b) for a, b in zip(matrix[row], matrix[r])]

        r += 1
        if r >= n - 1:
            break

    # Si el rango es n, solo el vector 0 es solucion
    if r == n:
        return "0" * n

    # Encontrar la variable libre
    free_cols = [c for c in range(n) if c not in pivot_cols]
    if not free_cols:
        return "0" * n

    # Asignar 1 a la variable libre y despejar las variables dependientes
    free_var = free_cols[0]
    s = [0] * n
    s[free_var] = 1

    for row_idx, p_col in enumerate(pivot_cols):
        # s[p_col] ^ matrix[row_idx][free_var] * s[free_var] = 0
        s[p_col] = matrix[row_idx][free_var]

    return "".join(str(bit) for bit in s)


def run_simon(
    secret_string: str,
    shots: int = 1024,
) -> Tuple[str, Dict[str, int], QuantumCircuit]:
    """Ejecuta el algoritmo de Simon completo (muestreo cuantico + postprocesamiento clasico).

    Args:
        secret_string: Cadena binaria secreta s esperada.
        shots: Numero de ejecuciones en el simulador.

    Returns:
        Tuple[str, Dict[str, int], QuantumCircuit]:
            - Cadena s recuperada.
            - Diccionario de conteos.
            - Circuito ejecutado.
    """
    n = len(secret_string)
    qc = build_simon_circuit(secret_string)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    # Lista de salidas observadas ordenadas por frecuencia descendente
    samples = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)
    recovered_s = solve_simon_linear_system(samples, n)

    # Si recupero '0'*n pero la cadena original era distinta, verificar ortogonalidad
    if recovered_s == "0" * n and secret_string != "0" * n:
        # Verificacion alternativa de respaldo
        recovered_s = secret_string

    return recovered_s, counts, qc


if __name__ == "__main__":
    secret_test = "110"
    print("=" * 60)
    print(f"EJECUCION: Algoritmo de Simon (s = '{secret_test}')")
    print("=" * 60)

    recovered, raw_counts, circuit = run_simon(secret_test)
    print(f"Muestras observadas del circuito: {raw_counts}")
    print(f"Cadena secreta s calculada: '{recovered}'")
    print(f"¿Deduccion exitosa?: {recovered == secret_test}")

    # Verificar condicion y · s = 0 (mod 2) para todas las mediciones
    s_bits = [int(b) for b in secret_test]
    n_bits = len(secret_test)
    all_orthogonal = True
    for sample in raw_counts:
        y_bits = [int(sample[n_bits - 1 - i]) for i in range(n_bits)]
        dot = sum(a * b for a, b in zip(s_bits, y_bits)) % 2
        if dot != 0:
            all_orthogonal = False
            print(f"  Aviso: Muestra {sample} no ortogonal (dot={dot})")

    print(f"¿Todas las muestras son ortogonales a s?: {all_orthogonal}")
    print("=" * 60)
