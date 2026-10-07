# Qiskit Maintainability Case Study: Quantum Algorithms

This project investigates maintainability and software engineering patterns in quantum computing using Qiskit. Quantum software often suffers from common architectural pitfalls: algorithmic logic tightly coupled inside monolithic Jupyter notebooks, hardcoded circuit configurations, reliance on deprecated APIs, and an absence of automated unit tests.

To study how standard software engineering practices apply to quantum development, this repository implements eight foundational quantum algorithms as clean, modular Python components. Each algorithm isolates circuit construction, hardware/simulator execution, and classical post-processing, and each is verified with automated tests.

---

## Implemented Algorithms

The table below summarizes the algorithms included in this study, comparing their theoretical complexity and outlining the problem each one solves.

| Algorithm | File | Classical | Quantum | Problem Formulation |
| :--- | :--- | :---: | :---: | :--- |
| **Bernstein–Vazirani** | [`bernstein_vazirani.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/bernstein_vazirani.py) | $O(n)$ | $O(1)$ | Recovers a hidden bitstring $s \in \{0, 1\}^n$ from oracle $f(x) = s \cdot x \pmod 2$ in a single query. |
| **Deutsch–Jozsa** | [`deutsch_jozsa.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/deutsch_jozsa.py) | $O(2^{n-1} + 1)$ | $O(1)$ | Determines whether a boolean function $f: \{0,1\}^n \to \{0,1\}$ is constant or balanced with certainty. |
| **Grover** | [`grover.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/grover.py) | $O(N)$ | $O(\sqrt{N})$ | Searches an unsorted space of $N = 2^n$ elements using amplitude amplification. |
| **Quantum Phase Estimation (QPE)** | [`quantum_phase_estimation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_phase_estimation.py) | - | $O(m^2)$ | Estimates the phase eigenvalue $\theta$ in $U\|\psi\rangle = e^{2\pi i \theta}\|\psi\rangle$ to $m$ bits using inverse QFT. |
| **Shor** | [`shor.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/shor.py) | $\exp(O(n^{1/3}))$ | $O(n^3)$ | Factors composite integer $N$ by reducing order-finding to phase estimation. Compiled here for $N = 15$. |
| **Simon** | [`simon.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/simon.py) | $\Omega(2^{n/2})$ | $O(n)$ | Finds hidden period $s$ for a 2-to-1 function where $f(x)=f(y) \iff x \oplus y \in \{0^n, s\}$ via $\mathbb{F}_2$ linear system solving. |
| **Quantum Teleportation** | [`quantum_teleportation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_teleportation.py) | Impossible (No-Cloning) | 1 Bell pair + 2 classical bits | Teleports an arbitrary single-qubit state using Bell measurement and dynamic feed-forward corrections. |
| **TSP (Traveling Salesperson)** | [`tsp.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/tsp.py) | NP-Hard ($O(n!)$ or $O(n^2 2^n)$) | Variational Heuristic (QAOA) | Solves route optimization by mapping a constrained QUBO to an Ising Hamiltonian optimized via QAOA + COBYLA. |

---

## Project Structure

The project separates algorithm implementations from test suites and entry-point scripts:

```text
qiskit-maintainability-case-study/
├── algorithms/
│   ├── __init__.py                  # Public exports
│   ├── bernstein_vazirani.py        # Bernstein-Vazirani implementation
│   ├── deutsch_jozsa.py             # Deutsch-Jozsa implementation
│   ├── grover.py                    # Grover search & diffusion operators
│   ├── quantum_phase_estimation.py  # Phase estimation with QFT inverse
│   ├── shor.py                      # Shor order-finding for N=15
│   ├── simon.py                     # Simon algorithm + GF(2) Gaussian solver
│   ├── quantum_teleportation.py     # Dynamic circuit teleportation
│   └── tsp.py                       # Ising Hamiltonian & QAOA variational solver
├── tests/
│   ├── __init__.py
│   ├── test_bernstein_vazirani.py
│   ├── test_deutsch_jozsa.py
│   ├── test_grover.py
│   ├── test_quantum_phase_estimation.py
│   ├── test_shor.py
│   ├── test_simon.py
│   ├── test_quantum_teleportation.py
│   └── test_tsp.py
├── main.py                          # CLI runner for quick execution
├── requirements.txt                 # Pinned dependencies
└── README.md
```

---

## Setup and Installation

Requirements: Python 3.10+ and modern Qiskit (1.0+).

```bash
git clone https://github.com/Rafags04/qiskit-maintainability-case-study.git
cd qiskit-maintainability-case-study
pip install -r requirements.txt
```

Dependencies include `qiskit`, `qiskit-aer`, `numpy`, `scipy`, and `pytest`.

---

## How to Run

### Command-line Runner

To run a demonstration of all eight algorithms in sequence:

```bash
python main.py
```

You can also target an individual algorithm with the `--algo` flag:

```bash
python main.py --algo grover
python main.py --algo shor
python main.py --algo simon
python main.py --algo tsp
```

Available options: `bernstein_vazirani`, `deutsch_jozsa`, `grover`, `qpe`, `shor`, `simon`, `teleportation`, `tsp`, `all`.

### Standalone Execution

Each file in `algorithms/` can be run on its own. Every module includes a `__main__` block with sample inputs and verification:

```bash
python algorithms/grover.py
python algorithms/quantum_teleportation.py
python algorithms/tsp.py
```

### Running the Test Suite

The test suite contains 40 automated tests covering circuit sizes, edge cases (e.g. invalid inputs, injective functions in Simon's algorithm, multi-target search in Grover), and measurement distributions:

```bash
# Using pytest
pytest -v

# Using standard unittest
python -m unittest discover tests -v
```

---

## Technical Notes and Design Decisions

Here are a few notable implementation choices made during development:

- **Dynamic circuits in Quantum Teleportation (`quantum_teleportation.py`):**
  Instead of relying on legacy `c_if` gate conditioning (which is deprecated in modern Qiskit), conditional operations use Qiskit's `qc.if_test((classical_bit, value))` context managers. This ensures compatibility with modern runtime targets that support real-time classical feed-forward.
  
- **Modular Inverse QFT (`quantum_phase_estimation.py`, `shor.py`):**
  Rather than writing manual phase-rotation ladders, inverse Fourier transforms use `QFTGate(n).inverse()`. This avoids repetitive code and delegates gate decomposition directly to Qiskit's transpiler passes.

- **Self-contained GF(2) Solver (`simon.py`):**
  Simon's algorithm requires solving a system of linear equations $y \cdot s = 0 \pmod 2$ over the Galois Field $\mathbb{F}_2$. Instead of pulling in heavy computer algebra libraries like SymPy, we included a straightforward Gaussian elimination routine directly in the module. It handles both 2-to-1 functions (where the matrix has rank $n-1$ and reveals a non-trivial period $s$) and 1-to-1 functions (where the matrix has full rank $n$ and correctly yields $s = 0^n$).

- **Ising Hamiltonian Mapping for QAOA (`tsp.py`):**
  The traveling salesperson instance is formulated as an unconstrained binary quadratic program (QUBO) for a 3-city tour (with city 0 fixed as start/end, leaving 4 binary variables). We map binary variables $x_i \in \{0, 1\}$ to Pauli operators via $x_i = \frac{I - Z_i}{2}$, producing an Ising Hamiltonian $H_C = \sum h_i Z_i + \sum J_{ij} Z_i Z_j$. The QAOA ansatz applies alternating layers of $e^{-i \gamma H_C}$ and transverse mixer $e^{-i \beta \sum X_i}$, with variational parameters $(\gamma, \beta)$ optimized using SciPy's COBYLA.

---

## References

1. Bernstein, E., & Vazirani, U. (1993). *Quantum complexity theory*. STOC '93, 11–20.
2. Deutsch, D., & Jozsa, R. (1992). *Rapid solution of problems by quantum computation*. Proc. R. Soc. Lond. A, 439(1907), 553–558.
3. Grover, L. K. (1996). *A fast quantum mechanical algorithm for database search*. STOC '96, 212–219.
4. Shor, P. W. (1994). *Algorithms for quantum computation: discrete logarithms and factoring*. FOCS '94, 124–134.
5. Simon, D. R. (1994). *On the power of quantum computation*. FOCS '94, 116–123.
6. Bennett, C. H., et al. (1993). *Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels*. Phys. Rev. Lett., 70(13), 1895–1899.
7. Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm*. arXiv:1411.4028.
