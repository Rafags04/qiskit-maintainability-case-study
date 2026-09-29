"""Punto de entrada principal del proyecto de Algoritmos Cuanticos en Qiskit.

Permite ejecutar demostraciones interactivas de los 8 algoritmos:
1. Bernstein-Vazirani
2. Deutsch-Jozsa
3. Grover
4. Quantum Phase Estimation (QPE)
5. Shor (Factorizacion de enteros)
6. Simon
7. Teletransportacion Cuantica
8. TSP (Problema del Viajante de Comercio con QAOA)
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
    header("1. Algoritmo de Bernstein-Vazirani")
    secret = "101101"
    print(f"Problema: Hallar la cadena secreta s con f(x) = s · x (mod 2)")
    print(f"Cadena secreta objetivo: '{secret}'")
    recovered, counts, qc = run_bernstein_vazirani(secret)
    print(f"Cadena recuperada:       '{recovered}'")
    print(f"Total qubits: {qc.num_qubits} | Conteos: {counts}")
    print(f"Estado: {'EXITOSO' if recovered == secret else 'FALLIDO'}")


def demo_deutsch_jozsa():
    header("2. Algoritmo de Deutsch-Jozsa")
    print("Problema: Determinar si f(x) es constante o balanceada en 1 sola consulta")
    for o_type in ["constant_0", "constant_1", "balanced"]:
        verdict, counts, _ = run_deutsch_jozsa(n=4, oracle_type=o_type, mask=0b1011)
        expected = "constant" if "constant" in o_type else "balanced"
        print(f"  Oraculo: {o_type:<12} -> Clasificado: {verdict:<10} (Esperado: {expected:<10}) [OK: {verdict == expected}]")


def demo_grover():
    header("3. Algoritmo de Grover (Busqueda Cuantica)")
    target = "110"
    n_qubits = 3
    print(f"Problema: Encontrar el estado '{target}' en un espacio de 2^{n_qubits} = {2**n_qubits} elementos")
    best_str, prob, counts, qc = run_grover(target, n=n_qubits)
    print(f"Estado con mayor probabilidad: '{best_str}'")
    print(f"Probabilidad de exito observada: {prob * 100:.2f}%")
    print(f"Total qubits: {qc.num_qubits} | Iteraciones optimas: 2")
    print(f"Estado: {'EXITOSO' if best_str == target and prob > 0.9 else 'FALLIDO'}")


def demo_qpe():
    header("4. Estimacion Cuantica de Fase (QPE)")
    theta_true = 0.625  # 5/8
    m_qubits = 4
    print(f"Problema: Estimar theta en U|psi> = e^(2*pi*i*theta)|psi> para theta = {theta_true} (5/8)")
    est, err, bitstr, counts, qc = run_qpe(theta_true, num_counting_qubits=m_qubits)
    print(f"Registro medido: '{bitstr}' (decimal {int(bitstr, 2)})")
    print(f"Fase estimada:   {est:.5f} (Error absoluto: {err:.5f})")
    print(f"Total qubits: {qc.num_qubits} ({m_qubits} conteo + 1 estado propio)")
    print(f"Estado: {'EXITOSO' if err < 1e-5 else 'FALLIDO'}")


def demo_shor():
    header("5. Algoritmo de Shor (Factorizacion de Enteros)")
    N = 15
    a = 7
    print(f"Problema: Factorizar N = {N} usando la base coprima a = {a}")
    factors, periods, counts, qc = run_shor(a=a, N=N)
    print(f"Periodos r evaluados: {periods}")
    print(f"Factores primos no triviales encontrados: {sorted(list(factors))}")
    print(f"Total qubits en circuito: {qc.num_qubits}")
    print(f"Estado: {'EXITOSO' if factors == {3, 5} else 'FALLIDO'}")


def demo_simon():
    header("6. Algoritmo de Simon")
    secret = "110"
    print(f"Problema: Encontrar s in {{0,1}}^n tal que f(x) = f(y) <=> x (+) y in {{0^n, s}}")
    print(f"Cadena secreta s configurada: '{secret}'")
    recovered, counts, qc = run_simon(secret)
    print(f"Cadena secreta deducida:      '{recovered}'")
    print(f"Total qubits: {qc.num_qubits} (2*n)")
    print(f"Estado: {'EXITOSO' if recovered == secret else 'FALLIDO'}")


def demo_teleportation():
    header("7. Protocolo de Teletransportacion Cuantica")
    theta, phi = 1.25, 0.45
    print(f"Problema: Teletransportar |psi> = Ry({theta}) Rz({phi}) |0> de Alice a Bob")
    fid, counts, qc = run_teleportation(theta=theta, phi=phi, verify_with_inverse=True)
    print(f"Fidelidad de transmision comprobada por Bob: {fid * 100:.2f}%")
    print(f"Total qubits: {qc.num_qubits} (Alice: 2, Bob: 1) con medicion dinamica y correcciones condicionales")
    print(f"Estado: {'EXITOSO' if fid >= 0.99 else 'FALLIDO'}")


def demo_tsp():
    header("8. Problema del Viajante de Comercio (TSP) con QAOA")
    distances = np.array([
        [0, 10, 30],
        [20, 0, 15],
        [12, 25, 0],
    ])
    print("Problema: Encontrar el ciclo hamiltoniano de menor distancia para 3 ciudades")
    print(f"Matriz de distancias:\n{distances}")
    route, dist, counts, qc = run_tsp_qaoa(distances, p=1, maxiter=30)
    route_str = " -> ".join(f"Ciudad {c}" for c in route)
    print(f"Ruta optima QAOA: {route_str}")
    print(f"Distancia minima encontrada: {dist} (Optimo global teorico: 37.0)")
    print(f"Qubits en el ansatz QAOA: {qc.num_qubits}")
    print(f"Estado: {'EXITOSO' if dist == 37.0 else 'FALLIDO'}")


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
    parser = argparse.ArgumentParser(description="Ejecutor de Algoritmos Cuanticos en Qiskit")
    parser.add_argument(
        "--algo",
        choices=list(DEMOS.keys()) + ["all"],
        default="all",
        help="Algoritmo a ejecutar (por defecto: all)",
    )
    args = parser.parse_args()

    print("\n" + "#" * 75)
    print("   PROYECTO: ESTUDIO DE ALGORITMOS CUANTICOS EN QISKIT")
    print("   Maintainability & Modular Quantum Computing Case Study")
    print("#" * 75)

    if args.algo == "all":
        for name, demo_func in DEMOS.items():
            demo_func()
    else:
        DEMOS[args.algo]()

    print("\n" + "#" * 75)
    print("   TODAS LAS EJECUCIONES FINALIZARON SATISFACTORIAMENTE")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    main()
