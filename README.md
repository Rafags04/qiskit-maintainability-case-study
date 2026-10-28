# Static Analysis of Quantum Metrics

This repository contains quantum algorithm source code for static analysis of
quantum metrics. The algorithms come from the
[QCRAFT-Scheduler repository](https://github.com/Qcraft-UEx/QCRAFT-Scheduler)
and are preserved without modifications.

The scope of this project is limited to static code analysis. It is not an
algorithm runner, does not perform simulations, and does not submit circuits
to quantum hardware.

## Analyzed Source Code

The algorithm files are located in `algorithms/`:

- `bernstein_vazirani.py`
- `Deutsch_Jozsa.py`
- `grover.py`
- `phase_estimation.py`
- `shor.py`
- `simon.py`
- `teleportation.py`
- `tsp.py`

This repository does not include an analysis tool or an execution command.
Static analysis should be performed using the relevant quantum metrics tool
and workflow.
