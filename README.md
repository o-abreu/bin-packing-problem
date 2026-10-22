# Bin Packing Problem (BPP) — SME 0110 · Programação Matemática

> **Provisional project description** — subject to refinement as the project evolves.

## Project

Implementation of the **Bin Packing Problem** (*Problema do Empacotamento*) for the
course **SME 0110 – Programação Matemática** (IME-USP, 2nd semester 2026), applied to a
real-world scenario following the official assignment
([`Projeto_PM_BCC_2026.pdf`](./Projeto_PM_BCC_2026.pdf)).

The work requires, per group:

1. **Mathematical modeling** (MILP) of a chosen packing/resource-allocation scenario;
2. **Exact solution** with a commercial solver (**Gurobi**) and a free solver (**SCIP**);
3. **An alternative solution method** (heuristic such as FFD/BFD, or a meta-heuristic);
4. A **technical report** (ABNT/IEEE), structured in the 5 mandated sections;
5. **Two presentations** during the semester + final delivery on e-disciplinas
   (single compacted archive: code + test instances + PDF report).

## Chosen scenario

**Alocação de Cargas em Veículos / Contêineres** — minimize the number of
trucks/containers needed to transport a set of goods with limited weight/volume
capacity. This maps 1:1 onto the generic BPP MILP from the assignment brief
(items = boxes; bins = trucks with capacity `C`):

$$\min \sum_{j \in J} y_j \quad \text{s.t.} \quad \sum_{j} x_{ij} = 1 \;\; \forall i, \qquad \sum_{i} w_i x_{ij} \le C y_j \;\; \forall j$$

**Dataset (provisional choice):** [Supply Chain Logistics Optimization Dataset](https://www.kaggle.com/datasets/omarstat2/supply-chain-logistics-data)
(Brunel University London research data) — 9,215 real customer orders with weights,
units and shipping dates; BPP mapping: items = order lines, `w_i` = order weight,
bins = trucks/containers with capacity `C` set by the freight weight brackets.
**Tentative — we may switch datasets later.** Research and alternatives:
[`DATASETS.md`](./DATASETS.md).

## Assignment & schedule

Requirements, grading breakdown, and dates are specified in the official assignment
(`Projeto_PM_BCC_2026.pdf` — kept locally, not tracked in this repository) and in the
work plan [`TODO.md`](./TODO.md).

## Repository layout (planned)

```
data/        # BPP instances (Kaggle-derived buckets + preprocessed real set) & provenance
src/         # parsers, MILP models (Gurobi/PySCIPOpt), heuristics (FFD/BFD, SA), harness
report/      # LaTeX report sources (`relatorio.pdf` is the final artifact)
work/        # scratch: solver logs, intermediate analyses
```

## Environment

The development environment is declaratively managed with
[devenv](https://devenv.sh) (Nix):

```sh
devenv shell        # enter the environment (git, python toolchain…)
```

Solver dependencies (`gurobipy` with academic license, `PySCIPOpt` + SCIP binary)
are being set up per [`TODO.md`](./TODO.md) Phase 0.

## License

Academic coursework — all rights reserved to the group members until submission.
Dataset licensing is documented in `data/README.md` (to be created in Phase 2).
