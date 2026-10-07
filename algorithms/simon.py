"""Simon's Algorithm.

Problem:
Given a black-box oracle function f: {0,1}^n -> {0,1}^n promised to satisfy:
    f(x) = f(y)  <=>  x (+) y in {0^n, s}
for some hidden secret period string s in {0,1}^n, find s.
If s = 0^n, f is a 1-to-1 (injective) function.
If s != 0^n, f is a 2-to-1 function.

Complexity:
- Classical: Omega(2^(n/2)) queries (birthday paradox bound).
- Quantum: O(n) quantum queries plus O(n^3) classical operations via
  Gaussian elimination over GF(2) (field F_2).
- Historically provided the first provable exponential separation between
  quantum and classical computation in the black-box setting.
"""

from typing import Dict, List, Optional, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


def build_simon_oracle(secret_string: str) -> QuantumCircuit:
    """Constructs a reversible (2*n)-qubit oracle implementing f(x) with period s.

    If s == '0'*n, f(x) = x (1-to-1 identity mapping).
    If s != '0'*n, f(x) = x (+) (x_pivot * s) is 2-to-1.

    Args:
        secret_string: Secret period string s of n bits.

    Returns:
        QuantumCircuit: Oracle subcircuit on 2*n qubits.

    Raises:
        ValueError: If secret_string is empty or contains non-binary characters.
    """
    if not secret_string or not all(c in "01" for c in secret_string):
        raise ValueError(
            f"secret_string must be a non-empty string of '0' and '1'. Received: '{secret_string}'"
        )

    n = len(secret_string)
    oracle = QuantumCircuit(2 * n, name="simon_oracle")

    # 1. Copy input register to output register: |x>|0> -> |x>|x>
    for i in range(n):
        oracle.cx(i, n + i)

    # 2. If s != '0'*n, locate first '1' bit (pivot index) and conditionally add s
    if "1" in secret_string:
        pivot = secret_string.find("1")
        for i, bit in enumerate(secret_string):
            if bit == "1":
                oracle.cx(pivot, n + i)

    return oracle


def build_simon_circuit(secret_string: str) -> QuantumCircuit:
    """Constructs the complete quantum circuit for Simon's algorithm.

    Args:
        secret_string: Secret period string s.

    Returns:
        QuantumCircuit: Quantum circuit ready for execution.
    """
    if not secret_string or not all(c in "01" for c in secret_string):
        raise ValueError(
            f"secret_string must be a non-empty string of '0' and '1'. Received: '{secret_string}'"
        )

    n = len(secret_string)
    qr_in = QuantumRegister(n, name="q_in")
    qr_out = QuantumRegister(n, name="q_out")
    cr = ClassicalRegister(n, name="c_meas")
    qc = QuantumCircuit(qr_in, qr_out, cr)

    # 1. Apply Hadamard transform to input register |+>^n
    qc.h(qr_in)
    qc.barrier()

    # 2. Evaluate oracle
    oracle = build_simon_oracle(secret_string)
    qc.compose(oracle, qubits=list(range(2 * n)), inplace=True)
    qc.barrier()

    # 3. Apply inverse Hadamard transform to input register
    qc.h(qr_in)
    qc.barrier()

    # 4. Measure input register only
    qc.measure(qr_in, cr)

    return qc


def solve_simon_linear_system(measured_samples: List[str], n: int) -> str:
    """Solves the homogeneous linear system y · s = 0 (mod 2) over GF(2)
    using Gaussian elimination to recover the secret bitstring s.

    Args:
        measured_samples: List of measured bitstrings obtained from circuit execution.
        n: Bit length of the secret string s.

    Returns:
        str: Deduce secret string s.
    """
    # Convert samples to row vectors over GF(2).
    # In Qiskit, bit qr_in[i] corresponds to sample[n - 1 - i].
    matrix: List[List[int]] = []
    for sample in measured_samples:
        row = [int(sample[n - 1 - i]) for i in range(n)]
        # Filter out zero rows
        if any(row):
            matrix.append(row)

    row_count = len(matrix)
    pivot_cols: List[int] = []
    r = 0

    for col in range(n):
        # Locate pivot in current column
        pivot_row = -1
        for row in range(r, row_count):
            if matrix[row][col] == 1:
                pivot_row = row
                break

        if pivot_row == -1:
            continue

        # Swap current row with pivot row
        matrix[r], matrix[pivot_row] = matrix[pivot_row], matrix[r]
        pivot_cols.append(col)

        # Eliminate column entries in all other rows
        for row in range(row_count):
            if row != r and matrix[row][col] == 1:
                matrix[row] = [(a ^ b) for a, b in zip(matrix[row], matrix[r])]

        r += 1
        if r == n:
            break

    # If the system has full rank n, the only solution to M s = 0 is the all-zeros vector
    if r == n:
        return "0" * n

    # Identify free variables
    free_cols = [c for c in range(n) if c not in pivot_cols]
    if not free_cols:
        return "0" * n

    # Set the first free variable to 1 and back-substitute dependent variables
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
    """Executes Simon's algorithm (quantum sampling + classical GF(2) linear solver).

    Args:
        secret_string: Expected secret period string s.
        shots: Number of measurement shots.

    Returns:
        Tuple[str, Dict[str, int], QuantumCircuit]:
            - Recovered secret string s.
            - Full measurement counts dictionary.
            - Executed circuit.
    """
    n = len(secret_string)
    qc = build_simon_circuit(secret_string)
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    counts = simulator.run(transpiled_qc, shots=shots).result().get_counts()

    # Pass observed samples to the GF(2) linear equation solver
    samples = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)
    recovered_s = solve_simon_linear_system(samples, n)

    return recovered_s, counts, qc


if __name__ == "__main__":
    secret_test = "110"
    print("=" * 60)
    print(f"EXECUTION: Simon's Algorithm (s = '{secret_test}')")
    print("=" * 60)

    recovered, raw_counts, circuit = run_simon(secret_test)
    print(f"Observed measurement samples: {raw_counts}")
    print(f"Deduced secret string s:      '{recovered}'")
    print(f"Deduction successful?         {recovered == secret_test}")

    # Verify orthogonality condition y · s = 0 (mod 2) for all measurements
    s_bits = [int(b) for b in secret_test]
    n_bits = len(secret_test)
    all_orthogonal = True
    for sample in raw_counts:
        y_bits = [int(sample[n_bits - 1 - i]) for i in range(n_bits)]
        dot = sum(a * b for a, b in zip(s_bits, y_bits)) % 2
        if dot != 0:
            all_orthogonal = False
            print(f"  Warning: Sample {sample} violates orthogonality (dot={dot})")

    print(f"Are all samples orthogonal to s? {all_orthogonal}")
    print("=" * 60)
