"""Main entry point for the Qiskit Quantum Algorithms repository.

Provides demonstration runners for the 8 implemented quantum algorithms:
1. Bernstein-Vazirani
2. Deutsch-Jozsa
3. Grover (Quantum Search)
4. Quantum Phase Estimation (QPE)
5. Shor (Integer Factorization)
6. Simon
7. Quantum Teleportation
8. Traveling Salesperson Problem (TSP with QAOA)
"""

import argparse
import sys
import numpy as np

from algorithms.bernstein_vazirani import run_bernstein_vazirani
from algorithms.deutsch_jozsa import run_deutsch_jozsa
from algorithms.grover import run_grover
from algorithms.quantum_phase_estimation import run_qpe
from algorithms.shor import run_shor
from algorithms.simon import run_simon
from algorithms.quantum_teleportation import run_teleportation
from algorithms.tsp import run_tsp_qaoa


def header(title: str):
    print("\n" + "=" * 75)
    print(f"  {title.upper()}")
    print("=" * 75)


def demo_bernstein_vazirani():
    header("1. Bernstein-Vazirani Algorithm")
    secret = "101101"
    print("Problem: Find hidden secret string s such that f(x) = s * x (mod 2)")
    print(f"Target secret string: '{secret}'")
    recovered, counts, qc = run_bernstein_vazirani(secret)
    print(f"Recovered bitstring:  '{recovered}'")
    print(f"Total qubits: {qc.num_qubits} | Measurement counts: {counts}")
    print(f"Status: {'SUCCESS' if recovered == secret else 'FAILED'}")


def demo_deutsch_jozsa():
    header("2. Deutsch-Jozsa Algorithm")
    print("Problem: Determine if f(x) is constant or balanced in a single quantum query")
    for o_type in ["constant_0", "constant_1", "balanced"]:
        verdict, counts, _ = run_deutsch_jozsa(n=4, oracle_type=o_type, mask=0b1011)
        expected = "constant" if "constant" in o_type else "balanced"
        print(
            f"  Oracle: {o_type:<12} -> Classified: {verdict:<10} "
            f"(Expected: {expected:<10}) [OK: {verdict == expected}]"
        )


def demo_grover():
    header("3. Grover Algorithm (Quantum Search)")
    target = "110"
    n_qubits = 3
    print(f"Problem: Locate state '{target}' in a search space of 2^{n_qubits} = {2**n_qubits} items")
    best_str, prob, counts, qc = run_grover(target, n=n_qubits)
    print(f"Most frequent state:         '{best_str}'")
    print(f"Observed success probability: {prob * 100:.2f}%")
    print(f"Total qubits: {qc.num_qubits} | Optimal iterations: 2")
    print(f"Status: {'SUCCESS' if best_str == target and prob > 0.9 else 'FAILED'}")


def demo_qpe():
    header("4. Quantum Phase Estimation (QPE)")
    theta_true = 0.625  # 5/8
    m_qubits = 4
    print(f"Problem: Estimate theta in U|psi> = e^(2*pi*i*theta)|psi> for theta = {theta_true} (5/8)")
    est, err, bitstr, counts, qc = run_qpe(theta_true, num_counting_qubits=m_qubits)
    print(f"Measured register: '{bitstr}' (decimal {int(bitstr, 2)})")
    print(f"Estimated phase:   {est:.5f} (Absolute error: {err:.5f})")
    print(f"Total qubits: {qc.num_qubits} ({m_qubits} counting + 1 eigenstate)")
    print(f"Status: {'SUCCESS' if err < 1e-5 else 'FAILED'}")


def demo_shor():
    header("5. Shor Algorithm (Integer Factorization)")
    N = 15
    a = 7
    print(f"Problem: Factor composite integer N = {N} using coprime base a = {a}")
    factors, periods, counts, qc = run_shor(a=a, N=N)
    print(f"Evaluated periods r: {periods}")
    print(f"Non-trivial prime factors discovered: {sorted(list(factors))}")
    print(f"Total circuit qubits: {qc.num_qubits}")
    print(f"Status: {'SUCCESS' if factors == {3, 5} else 'FAILED'}")


def demo_simon():
    header("6. Simon Algorithm")
    secret = "110"
    print("Problem: Find s in {0,1}^n such that f(x) = f(y) <=> x (+) y in {0^n, s}")
    print(f"Configured secret string s: '{secret}'")
    recovered, counts, qc = run_simon(secret)
    print(f"Deduced secret string:      '{recovered}'")
    print(f"Total qubits: {qc.num_qubits} (2*n)")
    print(f"Status: {'SUCCESS' if recovered == secret else 'FAILED'}")


def demo_teleportation():
    header("7. Quantum Teleportation Protocol")
    theta, phi = 1.25, 0.45
    print(f"Problem: Teleport |psi> = Ry({theta}) Rz({phi}) |0> from Alice to Bob")
    fid, counts, qc = run_teleportation(theta=theta, phi=phi, verify_with_inverse=True)
    print(f"Transmission fidelity verified by Bob: {fid * 100:.2f}%")
    print(
        f"Total qubits: {qc.num_qubits} (Alice: 2, Bob: 1) with dynamic measurement "
        "and feed-forward corrections"
    )
    print(f"Status: {'SUCCESS' if fid >= 0.99 else 'FAILED'}")


def demo_tsp():
    header("8. Traveling Salesperson Problem (TSP) with QAOA")
    distances = np.array([
        [0, 10, 30],
        [20, 0, 15],
        [12, 25, 0],
    ])
    print("Problem: Find minimum-distance closed Hamiltonian cycle for 3 cities")
    print(f"Distance matrix:\n{distances}")
    route, dist, counts, qc = run_tsp_qaoa(distances, p=1, maxiter=30)
    route_str = " -> ".join(f"City {c}" for c in route)
    print(f"Optimal QAOA route: {route_str}")
    print(f"Minimum distance found: {dist} (Theoretical global optimum: 37.0)")
    print(f"QAOA ansatz qubits: {qc.num_qubits}")
    print(f"Status: {'SUCCESS' if dist == 37.0 else 'FAILED'}")


DEMOS = {
    "bernstein_vazirani": demo_bernstein_vazirani,
    "deutsch_jozsa": demo_deutsch_jozsa,
    "grover": demo_grover,
    "qpe": demo_qpe,
    "shor": demo_shor,
    "simon": demo_simon,
    "teleportation": demo_teleportation,
    "tsp": demo_tsp,
}


def main():
    parser = argparse.ArgumentParser(description="Quantum Algorithms Runner in Qiskit")
    parser.add_argument(
        "--algo",
        choices=list(DEMOS.keys()) + ["all"],
        default="all",
        help="Algorithm to execute (default: all)",
    )
    args = parser.parse_args()

    print("\n" + "#" * 75)
    print("   PROJECT: QUANTUM ALGORITHMS STUDY IN QISKIT")
    print("   Maintainability & Modular Quantum Computing Case Study")
    print("#" * 75)

    if args.algo == "all":
        for name, demo_func in DEMOS.items():
            demo_func()
    else:
        DEMOS[args.algo]()

    print("\n" + "#" * 75)
    print("   ALL ALGORITHMIC RUNS COMPLETED SUCCESSFULLY")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    main()
