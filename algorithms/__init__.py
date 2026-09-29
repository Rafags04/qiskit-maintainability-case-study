"""Módulo de Algoritmos Cuánticos implementados en Qiskit.

Incluye implementaciones modulares, testeables y reproducibles de:
- Bernstein-Vazirani
- Deutsch-Jozsa
- Grover
- Estimación Cuántica de Fase (Quantum Phase Estimation - QPE)
- Algoritmo de Shor (Factorización de enteros)
- Algoritmo de Simon
- Teletransportación Cuántica (Quantum Teleportation)
- Problema del Viajante de Comercio (Traveling Salesperson Problem - TSP con QAOA)
"""

from .bernstein_vazirani import run_bernstein_vazirani, build_bernstein_vazirani_circuit
from .deutsch_jozsa import run_deutsch_jozsa, build_deutsch_jozsa_circuit
from .grover import run_grover, build_grover_circuit
from .quantum_phase_estimation import run_qpe, build_qpe_circuit
from .shor import run_shor, build_shor_circuit
from .simon import run_simon, build_simon_circuit
from .quantum_teleportation import run_teleportation, build_teleportation_circuit
from .tsp import run_tsp_qaoa, build_tsp_qaoa_circuit

__all__ = [
    "run_bernstein_vazirani",
    "build_bernstein_vazirani_circuit",
    "run_deutsch_jozsa",
    "build_deutsch_jozsa_circuit",
    "run_grover",
    "build_grover_circuit",
    "run_qpe",
    "build_qpe_circuit",
    "run_shor",
    "build_shor_circuit",
    "run_simon",
    "build_simon_circuit",
    "run_teleportation",
    "build_teleportation_circuit",
    "run_tsp_qaoa",
    "build_tsp_qaoa_circuit",
]
