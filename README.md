# Qiskit Maintainability Case Study: Algoritmos Cuanticos

Este repositorio contiene una implementacion modular, mantenible y rigurosa en **Python** y **Qiskit** de 8 algoritmos cuanticos fundamentales. Cada algoritmo se encuentra implementado en su propio modulo independiente dentro de la carpeta `algorithms/`, incluye funciones de construccion de circuitos, ejecucion en simulador (`AerSimulator`), decodificacion de resultados y un bloque de ejecucion directa autodocumentado.

Adicionalmente, cada algoritmo cuenta con un archivo correspondiente de pruebas unitarias en `tests/` compatible con `unittest` y `pytest`.

---

## 📋 Indice de Algoritmos Implementados

| Algoritmo | Archivo | Complejidad Clasica | Complejidad Cuantica | Descripcion / Problema |
| :--- | :--- | :---: | :---: | :--- |
| **Bernstein–Vazirani** | [`bernstein_vazirani.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/bernstein_vazirani.py) | $O(n)$ | $O(1)$ | Encuentra una cadena secreta $s$ a partir de $f(x) = s \cdot x \pmod 2$ en 1 sola consulta. |
| **Deutsch–Jozsa** | [`deutsch_jozsa.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/deutsch_jozsa.py) | $O(2^{n-1} + 1)$ | $O(1)$ | Determina con certeza absoluta si una funcion booleana es constante o balanceada. |
| **Grover** | [`grover.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/grover.py) | $O(N)$ | $O(\sqrt{N})$ | Busqueda en bases de datos no estructuradas con amplificacion de amplitud. |
| **Quantum Phase Estimation (QPE)** | [`quantum_phase_estimation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_phase_estimation.py) | - | $O(m^2)$ | Estima el autovalor de fase $\theta$ en $U\|\psi\rangle = e^{2\pi i \theta}\|\psi\rangle$ usando QFT inversa. |
| **Shor** | [`shor.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/shor.py) | $\exp(O(n^{1/3}))$ | $O(n^3)$ | Factorizacion de enteros en factores primos no triviales mediante busqueda de periodo modular. |
| **Simon** | [`simon.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/simon.py) | $\Omega(2^{n/2})$ | $O(n)$ | Determina el periodo oculto $s$ de una funcion 2-a-1 resolviendo un sistema en $\mathbb{F}_2$. |
| **Quantum Teleportation** | [`quantum_teleportation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_teleportation.py) | Imposible (No-clonado) | Consumo de 1 Bell pair + 2 bits clasicos | Teletransporta un estado cuantico arbitrario $|\psi\rangle$ aplicando circuitos dinamicos condicionales. |
| **TSP (Traveling Salesperson)** | [`tsp.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/tsp.py) | NP-Hard ($O(n!)$ o $O(n^2 2^n)$) | Heuristica Variacional (QAOA) | Mapea la optimizacion de rutas a un Hamiltoniano de Ising resuelto con QAOA + optimizador clasico. |

---

## 📂 Estructura del Proyecto

```text
qiskit-maintainability-case-study/
│
├── algorithms/                              # Modulo principal con cada uno de los algoritmos
│   ├── __init__.py                          # Exportacion de funciones clave
│   ├── bernstein_vazirani.py                # Algoritmo de Bernstein-Vazirani
│   ├── deutsch_jozsa.py                     # Algoritmo de Deutsch-Jozsa
│   ├── grover.py                            # Busqueda no estructurada de Grover
│   ├── quantum_phase_estimation.py          # Estimacion Cuantica de Fase (QPE)
│   ├── shor.py                              # Factorizacion de enteros de Shor
│   ├── simon.py                             # Algoritmo de Simon (muestreo + solver F_2)
│   ├── quantum_teleportation.py             # Teletransportacion con circuitos dinamicos
│   └── tsp.py                               # TSP resuelto via QUBO/Ising + QAOA
│
├── tests/                                   # Suite completa de pruebas unitarias
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
├── main.py                                  # Ejecutor interactivo / CLI general
├── requirements.txt                         # Dependencias requeridas
└── README.md                                # Documentacion tecnica y de uso
```

---

## 🚀 Requisitos e Instalacion

El proyecto es compatible con **Python 3.10+** y la version moderna de **Qiskit** (Qiskit 1.x / 2.x).

1. Clonar o acceder al repositorio:
   ```bash
   cd qiskit-maintainability-case-study
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Modos de Ejecucion

### 1. Ejecucion de la suite completa con el orquestador principal
Para ejecutar todos los algoritmos en secuencia con resumen formateado:
```bash
python main.py
```

Tambien es posible ejecutar un algoritmo especifico mediante el argumento `--algo`:
```bash
python main.py --algo grover
python main.py --algo shor
python main.py --algo tsp
```

### 2. Ejecucion independiente por archivo
Cada archivo en `algorithms/` es directamente ejecutable y cuenta con su propia rutina de demostracion y autoverificacion:
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

### 3. Ejecucion de Pruebas Unitarias
El proyecto cuenta con 32 pruebas unitarias que validan la construccion de circuitos, oraculos, medidas teoricas y casos limite:

- **Con pytest:**
  ```bash
  pytest -v
  ```

- **Con unittest:**
  ```bash
  python -m unittest discover tests -v
  ```

---

## 🔬 Detalles de Implementacion y Mantenibilidad

- **Compatibilidad con Circuitos Dinamicos de Qiskit 1.x / 2.x:**
  En [`quantum_teleportation.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/quantum_teleportation.py), las correcciones clasicas condicionales se implementan mediante `qc.if_test((cr, val))` garantizando soporte con los estandares modernos de Qiskit.
- **Transformada Cuantica de Fourier Inversa:**
  Se emplea `QFTGate(n).inverse()` para garantizar sintesis optima sin advertencias de obsolescencia.
- **Resolucion de Sistemas Lineales sobre $\mathbb{F}_2$:**
  En [`simon.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/simon.py), la rutina clasica de eliminacion gaussiana sobre el cuerpo finito $\mathbb{F}_2$ esta integrada nativamente sin requerir paquetes externos pesados.
- **Formulacion Rigurosa de QAOA para TSP:**
  En [`tsp.py`](file:///c:/Users/USUARIO/qiskit-maintainability-case-study/algorithms/tsp.py), se define la transformacion exacta de variables binarias $x_i \in \{0, 1\}$ a matrices de Pauli $Z_i$ mediante $x_i = \frac{I - Z_i}{2}$, construyendo un Hamiltoniano de Ising completo y optimizando sus parametros variacionales $(\gamma, \beta)$ con `scipy.optimize.minimize(method="COBYLA")`.
