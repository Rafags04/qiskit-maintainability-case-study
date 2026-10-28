# Análisis estático de métricas cuánticas

Este repositorio contiene código fuente de algoritmos cuánticos para realizar
análisis estático de métricas cuánticas. Los algoritmos proceden del repositorio
[QCRAFT-Scheduler](https://github.com/Qcraft-UEx/QCRAFT-Scheduler) y se conservan
sin modificaciones.

El propósito de este proyecto se limita al análisis estático del código. No es
un ejecutor de los algoritmos, no realiza simulaciones ni envía circuitos a
hardware cuántico.

## Código analizado

Los archivos de algoritmos están en `algorithms/`:

- `bernstein_vazirani.py`
- `Deutsch_Jozsa.py`
- `grover.py`
- `phase_estimation.py`
- `shor.py`
- `simon.py`
- `teleportation.py`
- `tsp.py`

Este repositorio no incluye una herramienta de análisis ni un comando de
ejecución. El análisis estático debe realizarse con la herramienta y el flujo
de trabajo de métricas cuánticas correspondientes.
