"""Demonstration runner for the quantum algorithms repository.

Runs sample executions for each implemented algorithm:
1. Bernstein-Vazirani
2. Deutsch-Jozsa
3. Grover
4. Quantum Phase Estimation (QPE)
5. Shor (order-finding for N=15)
6. Simon
7. Quantum Teleportation
8. Traveling Salesperson Problem (QAOA)
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
    print("\n" + "-" * 60)
    print(f" {title}")
    print("-" * 60)


def demo_bernstein_vazirani():
    header("1. Bernstein-Vazirani Algorithm")
    secret = "101101"
    print(f"Target secret bitstring: '{secret}'")
    recovered, counts, qc = run_bernstein_vazirani(secret)
    print(f"Recovered bitstring:     '{recovered}'")
    print(f"Circuit: {qc.num_qubits} qubits | Counts: {counts}")
    print(f"Result: {'PASS' if recovered == secret else 'FAIL'}")


def demo_deutsch_jozsa():
    header("2. Deutsch-Jozsa Algorithm")
    print("Classifying oracle functions (n = 4 input qubits):")
    for o_type in ["constant_0", "constant_1", "balanced"]:
        verdict, counts, _ = run_deutsch_jozsa(n=4, oracle_type=o_type, mask=0b1011)
        expected = "constant" if "constant" in o_type else "balanced"
        match = verdict == expected
        print(f"  {o_type:<12} -> classified as '{verdict}' (expected: '{expected}') [{ 'OK' if match else 'FAIL' }]")


def demo_grover():
    header("3. Grover Search Algorithm")
    target = "110"
    n_qubits = 3
    print(f"Target state: '{target}' in search space N = 2^{n_qubits} = {2**n_qubits}")
    best_str, prob, counts, qc = run_grover(target, n=n_qubits)
    print(f"Top measured state: '{best_str}' (observed probability: {prob * 100:.1f}%)")
    print(f"Circuit: {qc.num_qubits} qubits, 2 Grover iterations")
    print(f"Result: {'PASS' if best_str == target and prob > 0.9 else 'FAIL'}")


def demo_qpe():
    header("4. Quantum Phase Estimation (QPE)")
    theta_true = 0.625  # 5/8
    m_qubits = 4
    print(f"Target phase theta = {theta_true} (5/8) with m = {m_qubits} counting qubits")
    est, err, bitstr, counts, qc = run_qpe(theta_true, num_counting_qubits=m_qubits)
    print(f"Register measured: '{bitstr}' (decimal {int(bitstr, 2)}) -> estimated phase: {est:.5f}")
    print(f"Absolute error: {err:.5f}")
    print(f"Result: {'PASS' if err < 1e-5 else 'FAIL'}")


def demo_shor():
    header("5. Shor Algorithm (Order Finding for N = 15)")
    N = 15
    a = 7
    print(f"Factoring N = {N} using base a = {a}")
    factors, periods, counts, qc = run_shor(a=a, N=N)
    print(f"Evaluated periods r: {periods}")
    print(f"Non-trivial factors found: {sorted(list(factors))}")
    print(f"Circuit: {qc.num_qubits} total qubits (4 counting + 4 work)")
    print(f"Result: {'PASS' if factors == {3, 5} else 'FAIL'}")


def demo_simon():
    header("6. Simon Algorithm")
    secret = "110"
    print(f"Configured 2-to-1 period s: '{secret}'")
    recovered, counts, qc = run_simon(secret)
    print(f"Period deduced via GF(2) solver: '{recovered}'")
    print(f"Circuit: {qc.num_qubits} qubits (2*n)")
    print(f"Result: {'PASS' if recovered == secret else 'FAIL'}")


def demo_teleportation():
    header("7. Quantum Teleportation Protocol")
    theta, phi = 1.25, 0.45
    print(f"Teleporting state |psi> = Ry({theta}) Rz({phi}) |0>")
    fid, counts, qc = run_teleportation(theta=theta, phi=phi, verify_with_inverse=True)
    print(f"State fidelity after inverse verification: {fid * 100:.1f}%")
    print(f"Circuit: {qc.num_qubits} qubits with dynamic feed-forward corrections")
    print(f"Result: {'PASS' if fid >= 0.99 else 'FAIL'}")


def demo_tsp():
    header("8. Traveling Salesperson Problem (QAOA)")
    distances = np.array([
        [0, 10, 30],
        [20, 0, 15],
        [12, 25, 0],
    ])
    print("3-city distance matrix:")
    print(distances)
    route, dist, counts, qc = run_tsp_qaoa(distances, p=1, maxiter=30)
    route_str = " -> ".join(f"City {c}" for c in route)
    print(f"Best tour found: {route_str}")
    print(f"Tour distance:   {dist} (global optimum: 37.0)")
    print(f"QAOA circuit:    {qc.num_qubits} qubits (depth p=1)")
    print(f"Result: {'PASS' if dist == 37.0 else 'FAIL'}")


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
    parser = argparse.ArgumentParser(description="Run Qiskit quantum algorithm demonstrations")
    parser.add_argument(
        "--algo",
        choices=list(DEMOS.keys()) + ["all"],
        default="all",
        help="Algorithm to run (default: all)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(" Quantum Algorithms in Qiskit - Case Study Demonstrations")
    print("=" * 60)

    if args.algo == "all":
        for demo_func in DEMOS.values():
            demo_func()
    else:
        DEMOS[args.algo]()

    print("\n" + "=" * 60)
    print(" Execution finished.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
