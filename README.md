# Bin Packing Problem (BPP) — SME 0110 · Programação Matemática

> Work in progress — the phased plan is in [`TODO.md`](./notes/TODO.md) and what has
> already been measured is in [`EXPERIMENTOS.md`](./notes/EXPERIMENTOS.md).

## Project

Implementation of the **Bin Packing Problem** (*Problema do Empacotamento*) for the
course **SME 0110 – Programação Matemática** (ICMC-USP, 2nd semester 2026), applied to a
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
trucks/containers needed to transport a set of goods under limited floor area and
weight. The assignment's generic BPP MILP

$$\min \sum_{j \in J} y_j \quad \text{s.t.} \quad \sum_{j} x_{ij} = 1 \;\; \forall i, \qquad \sum_{i} w_i x_{ij} \le C y_j \;\; \forall j$$

is generalized in the two directions the real instance forces:

- **variable-sized bins with a cost (VSBPP):** the bins are four truck classes,
  each with floor area $A_t$, weight capacity $W_t$ and a cost $C_t$ per
  kilometre, so the objective is the cost of the fleet
  ($C_t \times \mathrm{dist}(o,d)$ per truck), not the number of trucks;
- **two dimensions:** a truck is loaded only if it respects **both** area and
  weight, which makes the instance a two-dimensional vector packing problem —
  and, in these data, area is the binding resource more often than weight.

**Dataset:** [Large-Scale Route
Optimization](https://www.kaggle.com/datasets/mexwell/large-scale-route-optimization)
(MIT), the sample data of Microsoft's route-optimization accelerator
([`microsoft/dstoolkit-route-optimization`](https://github.com/microsoft/dstoolkit-route-optimization)),
committed to `data/raw/`: **4,635 packages** over 365 orders, **61
origin–destination pairs** out of a single distribution centre (`City_61`), and a
fleet of four truck types. `Area` and `Weight` come scaled by $10^4$;
`distance.csv` is in metres. It is a **published sample** "inspired by a
real-world scenario" of a manufacturing customer, not raw company data.

**Scope:** we solve the *loading* subproblem under a **direct-trip policy** (one
stop per trip), so each route becomes an independent VSBPP instance and its
optimum is an **upper bound** on the cost of the underlying VRP — not the VRP
optimum.

The freight-tariff dataset used earlier in the project was dropped as the primary
instance — its `minimum cost` column places the floor below the implied price in
78% of the classes — and remains documented as a case study of inconsistent
data. Research, provenance and column-by-column notes:
[`DATASETS.md`](./notes/DATASETS.md).

## Assignment & schedule

Requirements, grading breakdown, and dates are specified in the official assignment
(`Projeto_PM_BCC_2026.pdf` — kept locally, not tracked in this repository) and in the
work plan [`TODO.md`](./notes/TODO.md).

## Report

The deliverable is `report/main.qmd` — an IEEE two-column article written in
pt-BR, whose body is assembled from included files:

```
report/
├── main.qmd                      # front matter + includes, nothing else
├── refs.bib
├── _extensions/ieee/             # vendored journal format (must sit next to main.qmd)
└── sections/
    ├── introducao.qmd            # I. Introdução
    ├── disponibilidade.qmd       # data and code availability
    ├── declaracao-uso-ia.qmd     # AI-use declaration
    ├── experimento.qmd           # draft, not included yet
    └── metodologia/
        ├── index.qmd             # II. Metodologia + the two includes below
        ├── base-de-dados.qmd     # fleet, instance statistics, 3 figures
        └── modelagem-matematica.qmd  # MILP formulation (R1–R11)
```

Include paths are resolved **relative to `main.qmd`**, even when nested — that is
why `metodologia/index.qmd` writes `sections/metodologia/base-de-dados.qmd`
rather than a path relative to itself.

```sh
devenv shell -- render-report   # writes report/output/main.pdf
```

Status of the five sections mandated by the assignment (§4): Introdução ✅,
Modelagem Matemática ✅ (as II.B), Solução via *Solvers* ⬜, Método de Solução
Alternativo ⬜, Conclusão ⬜ — see [`TODO.md`](./notes/TODO.md) phases 3–5.

## Repository layout

```
data/raw/          # dataset as published (MIT) — tracked, never re-fetched
notes/             # DATASETS.md, TODO.md, EXPERIMENTOS.md (research + plan + results)
report/            # Quarto sources for the article (see above)
scripts/           # experiment harnesses (symmetry-breaking benchmarks)
AGENTS.md          # guidance for coding agents
devenv.nix/.yaml   # declarative environment; pyrightconfig.json for type checking
```

## Environment

Declaratively managed with [devenv](https://devenv.sh) (Nix), with direnv
integration:

```sh
direnv allow                     # or: devenv shell
devenv shell -- render-report    # report/main.qmd -> report/output/main.pdf
```

- **Quarto 1.6.43**, pinned through the `nixpkgs-quarto` input — the vendored IEEE
  extension is built against 1.5/1.6.
- **PDF engine `pdflatex`** with TeX Live from the flake (IEEEtran, orcidlink,
  physics, mhchem). Quarto whitelists only pdflatex/xelatex/lualatex/latexmk.
- **Python venv** at `.devenv/state/venv` with `pulp` (CBC), `highspy`, `gurobipy`,
  `pandas`, `matplotlib`, `pandas-stubs`. `devenv.nix` exports `QUARTO_PYTHON`
  pointing at that interpreter, so the notebook chunks always run in the venv.
- **Solvers:** HiGHS and CBC are available out of the box. Gurobi needs the
  academic licence file (`gurobi.lic`, gitignored) and was **unavailable** at the
  last recorded run — the assignment asks for one commercial and one free solver,
  so this is tracked as a risk in [`TODO.md`](./notes/TODO.md) phase 3.

## License

Academic coursework — all rights reserved to the group members until submission.
Dataset licensing (MIT) and provenance are documented in
[`DATASETS.md`](./notes/DATASETS.md).
