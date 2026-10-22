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

**Dataset:** [Pick and Place Binning Dataset](https://www.kaggle.com/datasets/panavraaj/pick-and-place-binning-dataset)
(Haggle/Kaggle, MIT license) — synthetic BPP instances at 6 sizes (3–200 items) with
greedy baselines; see [`DATASETS.md`](./DATASETS.md) for the research and the
planned real-dataset validation candidates.

## Deliverables & grading

| Component | Points |
|---|---|
| Mathematical modeling (NM) | 3 |
| Implementation (NI) — 2 solver + 2 alternative method | 4 |
| Report (NR) — ABNT/IEEE | 3 |
| Presentation (NA), individual | 1 |
| Self & peer assessment (NAAP), individual | 1 |

`NT = (NM + NI + NR) · min{NA, NAAP}` — plagiarized/duplicated work receives **zero**,
hence this repository is **private**.

## Key dates

| Milestone | Date | Status |
|---|---|---|
| Kickoff / scenario lock | Oct 21, 2026 | done |
| **Presentation 1 (intermediate)** | **Nov 16, 2026** | confirmed |
| Final delivery (e-disciplinas) | **Dec 12, 2026** | placeholder — TBC |

Full plan, per-actor lanes (A1–A5), and Gantt chart: [`TODO.md`](./TODO.md).

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
