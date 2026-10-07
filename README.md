# Qiskit Maintainability Case Study: Quantum Algorithms

This repository provides a modular, maintainable, and mathematically rigorous implementation in **Python** and **Qiskit** of eight foundational quantum computing algorithms and protocols. Designed as a software engineering and maintainability case study for quantum software systems, each algorithm is decoupled into its own independent module within `algorithms/`, featuring circuit construction primitives, execution pipelines using `AerSimulator`, measurement post-processing, and self-verifying standalone demonstration entry points.

Furthermore, each algorithm is paired with an extensive unit test suite located in `tests/`, fully compatible with both `pytest` and `unittest`.

---

## 📋 Implemented Quantum Algorithms

| Algorithm | Source File | Classical Complexity | Quantum Complexity | Problem Description & Formulation |
| :--- | :--- | :---: | :---: | :--- |
| **Bernstein–Vazirani** | [`bernstein_vazirani.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/bernstein_vazirani.py) | $O(n)$ | $O(1)$ | Finds a hidden secret bitstring $s \in \{0, 1\}^n$ from oracle $f(x) = s \cdot x \pmod 2$ in a single query. |
| **Deutsch–Jozsa** | [`deutsch_jozsa.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/deutsch_jozsa.py) | $O(2^{n-1} + 1)$ | $O(1)$ | Deterministically decides whether a boolean function $f: \{0,1\}^n \to \{0,1\}$ is constant or balanced in 1 query. |
| **Grover** | [`grover.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/grover.py) | $O(N)$ | $O(\sqrt{N})$ | Unstructured database search over $N = 2^n$ items via iterative amplitude amplification and phase inversion. |
| **Quantum Phase Estimation (QPE)** | [`quantum_phase_estimation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_phase_estimation.py) | - | $O(m^2)$ | Estimates the phase eigenvalue $\theta$ in $U\|\psi\rangle = e^{2\pi i \theta}\|\psi\rangle$ with $m$ bits of precision via inverse QFT. |
| **Shor** | [`shor.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/shor.py) | $\exp(O(n^{1/3}))$ | $O(n^3)$ | Factors composite integers $N$ into non-trivial prime factors by reducing factorization to order-finding via QPE. |
| **Simon** | [`simon.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/simon.py) | $\Omega(2^{n/2})$ | $O(n)$ | Recovers the hidden period $s$ of a 2-to-1 function $f(x) = f(y) \iff x \oplus y \in \{0^n, s\}$ via $\mathbb{F}_2$ linear system solving. |
| **Quantum Teleportation** | [`quantum_teleportation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_teleportation.py) | Impossible (No-Cloning) | 1 Bell pair + 2 classical bits | Teleports an arbitrary quantum state $\|\psi\rangle = \alpha\|0\rangle + \beta\|1\rangle$ using dynamic circuits and feed-forward operations. |
| **TSP (Traveling Salesperson)** | [`tsp.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/tsp.py) | NP-Hard ($O(n!)$ or $O(n^2 2^n)$) | Variational Heuristic (QAOA) | Formulates route optimization as a QUBO/Ising Hamiltonian solved using QAOA and classical COBYLA parameter optimization. |

---

## 📂 Repository Architecture

```text
qiskit-maintainability-case-study/
│
├── algorithms/                              # Core algorithmic modules
│   ├── __init__.py                          # Public API exports
│   ├── bernstein_vazirani.py                # Bernstein-Vazirani implementation
│   ├── deutsch_jozsa.py                     # Deutsch-Jozsa implementation
│   ├── grover.py                            # Grover's search algorithm
│   ├── quantum_phase_estimation.py          # Quantum Phase Estimation (QPE)
│   ├── shor.py                              # Shor's integer factorization algorithm
│   ├── simon.py                             # Simon's algorithm (quantum sampling + GF(2) solver)
│   ├── quantum_teleportation.py             # Quantum teleportation protocol with dynamic circuits
│   └── tsp.py                               # Traveling Salesperson Problem via Ising Hamiltonian & QAOA
│
├── tests/                                   # Comprehensive unit testing suite
│   ├── __init__.py
│   ├── test_bernstein_vazirani.py
│   ├── test_deutsch_jozsa.py
│   ├── test_grover.py
│   ├── test_quantum_phase_estimation.py
│   ├── test_shor.py
│   ├── test_simon.py
│   ├── test_quantum_teleportation.py
│   └── test_tsp.py
│
├── main.py                                  # CLI orchestrator and interactive runner
├── requirements.txt                         # Package dependencies
└── README.md                                # Technical documentation and publication reference
```

---

## 🚀 Prerequisites and Installation

The codebase targets **Python 3.10+** and modern **Qiskit (>=1.0.0)** with **Qiskit Aer (>=0.14.0)**.

1. **Clone or navigate to the repository:**
   ```bash
   cd qiskit-maintainability-case-study
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Execution Modes

### 1. Unified Execution via CLI Orchestrator
Execute all eight quantum algorithms sequentially with structured console output:
```bash
python main.py
```

Run a specific algorithm using the `--algo` argument:
```bash
python main.py --algo grover
python main.py --algo shor
python main.py --algo simon
python main.py --algo teleportation
python main.py --algo tsp
```

Available options: `bernstein_vazirani`, `deutsch_jozsa`, `grover`, `qpe`, `shor`, `simon`, `teleportation`, `tsp`, `all`.

### 2. Standalone Algorithm Execution
Every file under `algorithms/` is directly executable and contains a dedicated, self-contained verification routine:
```bash
python algorithms/bernstein_vazirani.py
python algorithms/deutsch_jozsa.py
python algorithms/grover.py
python algorithms/quantum_phase_estimation.py
python algorithms/shor.py
python algorithms/simon.py
python algorithms/quantum_teleportation.py
python algorithms/tsp.py
```

### 3. Automated Unit Testing
The project includes automated unit test suites covering circuit structures, register allocations, theoretical probabilities, boundary conditions, and invalid input validation:

- **Using pytest:**
  ```bash
  pytest -v
  ```

- **Using Python's built-in unittest:**
  ```bash
  python -m unittest discover tests -v
  ```

---

## 🔬 Implementation Highlights & Maintainability Principles

- **Qiskit Modern Dynamic Circuits Support:**
  In [`quantum_teleportation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_teleportation.py), classical feed-forward corrections are realized via `qc.if_test((cr, val))` context managers, adhering to standard Qiskit 1.x / 2.x dynamic circuit specifications without deprecated c_if semantics.
- **Unitary Synthesis of Inverse QFT:**
  Inverse quantum Fourier transformations in [`quantum_phase_estimation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_phase_estimation.py) and [`shor.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/shor.py) utilize `QFTGate(n).inverse()`, preventing deprecation warnings and ensuring decomposition into elementary basis gates.
- **Native Linear System Solver over $\mathbb{F}_2$:**
  In [`simon.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/simon.py), the classical post-processing stage incorporates a native Gaussian elimination routine over the Galois Field $\mathrm{GF}(2)$, accurately distinguishing between 1-to-1 functions (full rank $n$ yielding $s = 0^n$) and 2-to-1 functions (rank $n-1$ yielding non-trivial $s$) without third-party algebraic dependencies.
- **Rigorous QAOA Mapping for Combinatorial Optimization:**
  In [`tsp.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/tsp.py), the constrained QUBO formulation maps binary variables $x_i \in \{0, 1\}$ to Pauli spin operators $Z_i$ through $x_i = \frac{I - Z_i}{2}$. The corresponding Ising cost Hamiltonian $H_C = \sum_i h_i Z_i + \sum_{i<j} J_{ij} Z_i Z_j$ is evaluated with alternating parameterized unitaries $e^{-i \gamma_l H_C}$ and transverse mixer unitaries $e^{-i \beta_l H_M}$, optimized classically with SciPy's COBYLA.

---

## 📚 Selected Scientific References

1. **Bernstein, E., & Vazirani, U.** (1993). *Quantum complexity theory*. Proceedings of the 25th Annual ACM Symposium on Theory of Computing (STOC '93), 11–20.
2. **Deutsch, D., & Jozsa, R.** (1992). *Rapid solution of problems by quantum computation*. Proceedings of the Royal Society of London. Series A, 439(1907), 553–558.
3. **Grover, L. K.** (1996). *A fast quantum mechanical algorithm for database search*. Proceedings of the 28th Annual ACM Symposium on Theory of Computing (STOC '96), 212–219.
4. **Shor, P. W.** (1994). *Algorithms for quantum computation: discrete logarithms and factoring*. Proceedings of 35th Annual Symposium on Foundations of Computer Science (FOCS '94), 124–134.
5. **Simon, D. R.** (1994). *On the power of quantum computation*. Proceedings of 35th Annual Symposium on Foundations of Computer Science (FOCS '94), 116–123.
6. **Bennett, C. H., et al.** (1993). *Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels*. Physical Review Letters, 70(13), 1895–1899.
7. **Farhi, E., Goldstone, J., & Gutmann, S.** (2014). *A Quantum Approximate Optimization Algorithm*. arXiv:1411.4028.
