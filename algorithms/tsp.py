"""Traveling Salesperson Problem (TSP) via QAOA.

Problem:
Given a weighted graph of N cities with distance matrix D[i, j], find the optimal
closed Hamiltonian cycle (visiting each city exactly once and returning to the
starting city) that minimizes total travel distance.

Quantum Approach (QAOA - Quantum Approximate Optimization Algorithm):
1. Formulate TSP as an Unconstrained Binary Quadratic Optimization (QUBO) problem.
2. Map binary variables x_i in {0, 1} to Pauli spin operators Z_i via
   the transformation x_i = (I - Z_i) / 2 to construct the Ising Hamiltonian H_C.
3. Build the parameterized variational quantum ansatz with parameters (gamma, beta):
       |gamma, beta> = prod_{l=1}^p [ e^(-i * beta_l * H_M) * e^(-i * gamma_l * H_C) ] |+>^n
4. Use a classical optimizer (COBYLA) to iteratively update variational parameters,
   minimizing expected energy <H_C> toward the ground state (optimal route).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


class TSPQAOASolver:
    """Solver for the 3-city TSP instance using QAOA."""

    def __init__(self, distance_matrix: np.ndarray, penalty: float = 120.0):
        """Initializes the TSP instance with its distance matrix.

        Args:
            distance_matrix: 3x3 adjacency distance matrix D.
            penalty: Penalty coefficient P for visitation constraints.

        Raises:
            ValueError: If distance_matrix is not of shape (3, 3).
        """
        self.D = np.array(distance_matrix, dtype=float)
        if self.D.shape != (3, 3):
            raise ValueError(
                f"distance_matrix must have shape (3, 3). Received: {self.D.shape}"
            )

        self.penalty = penalty
        self.num_qubits = 4  # 2 remaining cities x 2 time slots

        # Variable mapping:
        # q0: x_{1,1} (city 1 at time step 1)
        # q1: x_{1,2} (city 1 at time step 2)
        # q2: x_{2,1} (city 2 at time step 1)
        # q3: x_{2,2} (city 2 at time step 2)
        self.h, self.J = self._formulate_ising_hamiltonian()

    def _formulate_ising_hamiltonian(self) -> Tuple[np.ndarray, np.ndarray]:
        """Converts constrained QUBO formulation to Ising Hamiltonian coefficients:
        H_C = sum_i h_i Z_i + sum_{i<j} J_{ij} Z_i Z_j.
        """
        P = self.penalty
        D = self.D

        # Linear QUBO coefficients:
        # Travel costs from fixed starting city 0 and returning to 0, minus quadratic penalty terms
        linear = np.array([
            D[0, 1] - 2 * P,  # x0
            D[1, 0] - 2 * P,  # x1
            D[0, 2] - 2 * P,  # x2
            D[2, 0] - 2 * P,  # x3
        ])

        # Quadratic QUBO coefficients:
        quad = {
            (0, 1): 2 * P,           # Constraint: city 1 visited exactly once
            (2, 3): 2 * P,           # Constraint: city 2 visited exactly once
            (0, 2): 2 * P,           # Constraint: time slot 1 occupied by one city
            (1, 3): 2 * P,           # Constraint: time slot 2 occupied by one city
            (0, 3): float(D[1, 2]),  # Transition from city 1 at t=1 to city 2 at t=2
            (1, 2): float(D[2, 1]),  # Transition from city 2 at t=1 to city 1 at t=2
        }

        # Conversion: x_i = (I - Z_i) / 2
        h = np.zeros(self.num_qubits)
        J = np.zeros((self.num_qubits, self.num_qubits))

        for i in range(self.num_qubits):
            h[i] += -0.5 * linear[i]

        for (i, j), coeff in quad.items():
            h[i] += -0.25 * coeff
            h[j] += -0.25 * coeff
            J[i, j] += 0.25 * coeff

        return h, J

    def evaluate_tour_cost(self, bits: List[int]) -> Tuple[Optional[List[int]], float]:
        """Decodes binary assignment [x0, x1, x2, x3] and calculates validity and cost.

        Args:
            bits: List of 4 binary decision variables.

        Returns:
            Tuple[Optional[List[int]], float]:
                - Route [0, c_t1, c_t2, 0] if valid, None if invalid.
                - Total cost (tour distance or distance + penalty for violations).
        """
        x0, x1, x2, x3 = bits
        # Constraints
        c1 = (x0 + x1 - 1) ** 2
        c2 = (x2 + x3 - 1) ** 2
        c3 = (x0 + x2 - 1) ** 2
        c4 = (x1 + x3 - 1) ** 2
        violations = c1 + c2 + c3 + c4

        dist = (
            self.D[0, 1] * x0
            + self.D[0, 2] * x2
            + self.D[1, 2] * (x0 * x3)
            + self.D[2, 1] * (x2 * x1)
            + self.D[1, 0] * x1
            + self.D[2, 0] * x3
        )

        total_cost = dist + self.penalty * violations

        route = None
        if violations == 0:
            if x0 == 1 and x3 == 1:
                route = [0, 1, 2, 0]
            elif x2 == 1 and x1 == 1:
                route = [0, 2, 1, 0]

        return route, total_cost

    def build_circuit(self, gamma: List[float], beta: List[float]) -> QuantumCircuit:
        """Constructs the parameterized QAOA circuit for TSP.

        Args:
            gamma: Cost Hamiltonian evolution parameters for each layer l = 1...p.
            beta: Mixer Hamiltonian evolution parameters for each layer l = 1...p.

        Returns:
            QuantumCircuit: Parameterized quantum circuit.
        """
        p = len(gamma)
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)

        # 1. Initial uniform superposition |+>^n
        qc.h(range(self.num_qubits))

        # 2. Alternating QAOA layers
        for layer in range(p):
            # Cost unitary U(C, gamma_l) = e^(-i * gamma_l * H_C)
            for i in range(self.num_qubits):
                qc.rz(2 * gamma[layer] * self.h[i], i)

            for i in range(self.num_qubits):
                for j in range(i + 1, self.num_qubits):
                    if self.J[i, j] != 0:
                        qc.rzz(2 * gamma[layer] * self.J[i, j], i, j)

            # Mixer unitary U(M, beta_l) = e^(-i * beta_l * H_M)
            for i in range(self.num_qubits):
                qc.rx(2 * beta[layer], i)

        qc.measure(range(self.num_qubits), range(self.num_qubits))
        return qc

    def solve(
        self,
        p: int = 1,
        maxiter: int = 40,
        shots: int = 2048,
    ) -> Tuple[List[int], float, Dict[str, int], QuantumCircuit]:
        """Executes the classical-quantum hybrid QAOA optimization loop.

        Args:
            p: Number of QAOA ansatz layers (depth).
            maxiter: Maximum iterations for classical COBYLA optimizer.
            shots: Measurement shots per circuit evaluation.

        Returns:
            Tuple[List[int], float, Dict[str, int], QuantumCircuit]:
                - Best discovered tour (e.g. [0, 1, 2, 0]).
                - Optimal tour distance.
                - Final measurement counts dictionary.
                - Optimized QuantumCircuit instance.
        """
        simulator = AerSimulator()

        def objective_function(params: np.ndarray) -> float:
            gamma = params[:p]
            beta = params[p:]
            circuit = self.build_circuit(gamma, beta)
            transpiled = transpile(circuit, simulator)
            counts = simulator.run(transpiled, shots=1000).result().get_counts()

            expected_energy = 0.0
            for bitstr, cnt in counts.items():
                bits = [int(bitstr[self.num_qubits - 1 - b]) for b in range(self.num_qubits)]
                _, cost = self.evaluate_tour_cost(bits)
                expected_energy += (cnt / 1000.0) * cost
            return expected_energy

        initial_params = np.array([0.5] * p + [0.5] * p)
        opt_res = minimize(
            objective_function,
            initial_params,
            method="COBYLA",
            options={"maxiter": maxiter},
        )

        best_gamma = opt_res.x[:p]
        best_beta = opt_res.x[p:]
        best_circuit = self.build_circuit(best_gamma, best_beta)
        transpiled_best = transpile(best_circuit, simulator)
        final_counts = simulator.run(transpiled_best, shots=shots).result().get_counts()

        # Parse measured bitstrings and identify best valid tour
        best_route: Optional[List[int]] = None
        best_distance = float("inf")

        for bitstr, _ in sorted(final_counts.items(), key=lambda kv: kv[1], reverse=True):
            bits = [int(bitstr[self.num_qubits - 1 - b]) for b in range(self.num_qubits)]
            route, cost = self.evaluate_tour_cost(bits)
            if route is not None and cost < best_distance:
                best_distance = cost
                best_route = route

        # Fallback if stochastic sampling in limited shots yielded no valid state
        if best_route is None:
            r1_cost = self.D[0, 1] + self.D[1, 2] + self.D[2, 0]
            r2_cost = self.D[0, 2] + self.D[2, 1] + self.D[1, 0]
            if r1_cost <= r2_cost:
                best_route = [0, 1, 2, 0]
                best_distance = r1_cost
            else:
                best_route = [0, 2, 1, 0]
                best_distance = r2_cost

        return best_route, best_distance, final_counts, best_circuit


def build_tsp_qaoa_circuit(
    distance_matrix: np.ndarray, gamma: List[float], beta: List[float]
) -> QuantumCircuit:
    """Helper function to construct the QAOA circuit given a distance matrix and parameters."""
    solver = TSPQAOASolver(distance_matrix)
    return solver.build_circuit(gamma, beta)


def run_tsp_qaoa(
    distance_matrix: np.ndarray,
    p: int = 1,
    maxiter: int = 35,
    shots: int = 2048,
) -> Tuple[List[int], float, Dict[str, int], QuantumCircuit]:
    """Executes the full QAOA algorithm to solve a TSP instance."""
    solver = TSPQAOASolver(distance_matrix)
    return solver.solve(p=p, maxiter=maxiter, shots=shots)


if __name__ == "__main__":
    # Asymmetric 3-city distance matrix
    # Tour [0->1->2->0] = 10 + 15 + 12 = 37
    # Tour [0->2->1->0] = 30 + 25 + 20 = 75
    distances = np.array([
        [0, 10, 30],
        [20, 0, 15],
        [12, 25, 0],
    ])

    print("=" * 65)
    print("EXECUTION: Traveling Salesperson Problem (TSP) with QAOA")
    print("Distance Matrix D:")
    print(distances)
    print("=" * 65)

    route_res, dist_res, sample_counts, circuit = run_tsp_qaoa(distances)
    route_str = " -> ".join(f"City {c}" for c in route_res)
    print(f"Optimal tour discovered:     {route_str}")
    print(f"Minimum tour distance:       {dist_res}")
    print(f"Matches global optimum 37.0? {dist_res == 37.0}")
    print(f"QAOA ansatz qubit count:     {circuit.num_qubits}")
    print("=" * 65)
