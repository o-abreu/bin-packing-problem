# AGENTS.md — bin-packing-problem

Guidance for coding agents working in this repository (USP *Programação
Matemática* project: a variable-size/cost bin packing model — VSBPP — built on
real freight logistics data).

## Language

- **All repository documentation — `TODO.md`, `DATASETS.md`, the deliverable
  report `report/main.qmd`, and any new workspace document — is written in
  Brazilian Portuguese (pt-BR) from now on**; updated sections must keep the
  language. Code, identifiers, and bibliography keys stay as-is.
- `AGENTS.md` itself is kept in English (agent-facing guidance).
- Conversations and commit messages: Portuguese welcome.

## Project layout

| Path | What it is |
| --- | --- |
| `Projeto_PM_BCC_2026.md` | Course brief (generic BPP formulation — the model must extend it) |
| `DATASETS.md` | Dataset research; provenance and column-by-column annotations |
| `TODO.md` | Phased plan — check it before starting work; note what phase a change belongs to |
| `report/main.qmd` + `report/refs.bib` | IEEE-formatted Quarto report/notebook (the deliverable) — `report/` is self-contained |
| `report/_extensions/ieee/` | Vendored `dfolio/quarto-ieee` journal format extension (must sit next to `main.qmd`) |
| `data/raw/*.csv` | Committed dataset files — **keep them tracked, never re-fetch or gitignore** |
| `output/` | Generated render artifacts — ignored by git |
| `devenv.nix` / `devenv.yaml` / `devenv.lock` / `requirements.txt` | Declarative environment |

## Environment rules (NixOS + devenv)

- **Never install anything imperatively.** No `pip install`, no ad-hoc
  downloads of tools. Python deps go in `requirements.txt` (managed venv,
  devenv reinstalls only on file change); system tools go in `devenv.nix`
  `packages`. If a command is missing from PATH in a pinch, use the `,`
  (comma) tool prefix for one-off programs, but record the outcome as a
  proposed devenv edit.
- Work inside the shell (`devenv shell -- <cmd>` or direnv).
- **Quarto is pinned to 1.6.43** via the `nixpkgs-quarto` input
  (`devenv.yaml`; there is a comment explaining why). Do not bump it without
  re-rendering `report/main.qmd` end to end.
- **`pdf-engine` for `report/main.qmd` must be `pdflatex`.** Quarto's engine
  whitelist is only pdflatex/xelatex/lualatex/latexmk — setting `tectonic`
  makes the custom-template format fail with the cryptic error
  *“the format pdf does not support providing any template partials”*.
- Missing LaTeX package at render time → add that specific package to the
  `texlive.withPackages` list in `devenv.nix`; do not switch to a bigger
  scheme wholesale.
- Missing Python module at render time → add to `requirements.txt`.
- File-editing rule: use the **edit tool** for modifications; `write` only
  for brand-new files. Stop and ask instead of working around it.

## Rendering

```bash
devenv shell -- render-report          # devenv script (report/main.qmd → output/)
```

The script pins `QUARTO_PYTHON` to the project's venv interpreter. The venv
has `nbclient`/`nbformat` because quarto's kernel runner needs them.

## Domain vocabulary — terminology is part of the model

- This is **VSBPP** (variable-size/cost bin packing): items are **packages**
  (`Item_ID`; size = area in m² **and** weight in kg); bins are **trucks**; bin
  **classes** are the four truck types with $(A_t, W_t, c_t)$ — area capacity,
  weight capacity and cost per km.
- **The instance is two-dimensional.** A truck is feasible only if
  $\sum_i a_i x_{ij} \le A_t$ **and** $\sum_i w_i x_{ij} \le W_t$. Never collapse
  it to 1D without saying so: item density (median 797 kg/m²) exceeds the
  16.5 m truck's ratio (671 kg/m²), so **area binds more often than weight**.
- **Cost is per km, not per truck and not per kg.** For a fixed lane $(o,d)$ a
  truck of type $t$ costs $c_t \times \mathrm{dist}(o,d)$: a fixed charge per
  bin. The model is a fixed-charge VSBPP, not a tariffed per-kg problem.
- Say **item/package** and **truck**. The old freight vocabulary (orders,
  bookings, tariffs, `rate`/`minimum cost`) belongs to the **legacy case
  study** and must not leak into the new model.

## Data facts (already verified — do not re-derive)

- **Primary dataset:** `mexwell/large-scale-route-optimization` (Kaggle, MIT),
  mirror of the Microsoft *Large-Scale Route Optimization* accelerator
  (`microsoft/dstoolkit-route-optimization`, MIT). Files in `data/raw/`:
  `order_small.csv` (10 items, 2 lanes), `order_large.csv` (**4,635 items**,
  365 orders, **61 O–D pairs**), `distance.csv` (metres), `trucks.csv` (fleet,
  transcribed from `src/core/structure.py`).
- **Units:** `Area` and `Weight` are scaled by $10^4$ — divide by 10,000 to get
  m² and kg. Work in m²/kg (or convert the capacities the same way).
- **Fleet (the code is authoritative; the repo README lists an older 3-type
  table with 10/5/2 t):** 16.5 m → 40.25 m² / 27,000 kg / 10.0 per km;
  12.5 m → 30.25 m² / 24,000 kg / 9.0; 9.6 m → 20.93 m² / 14,000 kg / 6.5;
  7.6 m → 16.56 m² / 8,000 kg / 5.5.
- **Cost per unit capacity is monotone in truck size** ($c_t/A_t$ falls from
  0.332 to 0.248 \$/m²; $c_t/W_t$ from 0.00069 to 0.00037 \$/kg) — a coherent
  "bigger is cheaper per unit" schedule, unlike the legacy freight table.
- Item distributions: area 0.64–9.72 m² (median 1.25), weight 46–3,130 kg
  (median 1,000); **no item exceeds the largest truck**; density median
  797 kg/m².
- `Distance(M)` is in **metres**, despite the column name.
- The data is a **published sample** "inspired by a real-world scenario" of a
  manufacturing customer — not raw company data; state that in the report.
- `Danger_Type`, `Available_Time` and `Deadline` enable extensions (incompatible
  items, time windows) that the core BPP ignores.
- **Legacy (documented, not used):** the freight dataset
  (`omarstat2/supply-chain-logistics-data`) was dropped as primary in 2026-10 —
  its `minimum cost` sits below the implied floor price in 78% of classes
  (median $f/(R\,l)=0.09$), `V444_4` has a `rate` **increasing** with weight,
  and `PORT09→PORT09`×DTP is 100% GROUND with a different cost rule. See
  `DATASETS.md`.

## Solver stack

- MILP modeling: **PuLP**. The new instance is a **fixed-charge, two-dimensional
  VSBPP**: $\min \sum_j \sum_t c_t\,\mathrm{dist}(o,d)\,y_{jt}$ subject to
  $\sum_i x_{ij}=1$, $\sum_t y_{jt}\le 1$, $x_{ij}\le \sum_t y_{jt}$,
  $\sum_i a_i x_{ij} \le \sum_t A_t y_{jt}$ and
  $\sum_i w_i x_{ij} \le \sum_t W_t y_{jt}$ — to be restated in
  `report/sections/modelagem-matematica.qmd`. The freight formulation R1–R6 with
  the $\max(f, RW)$ epigraph is **legacy** (kept only for the case study).
- **PuLP in the venv is 4.2.x**: `LpVariable.dicts`, `PULP_CBC_CMD` and
  `pulp.LpStatus` **no longer exist**. Use
  `m.add_variable_dicts(name, (idx0, idx1), cat="Binary")` (nested dicts,
  `x[i][j]`), `stats = m.solve(pulp.HiGHS(msg=False))`, then
  `stats.objective` / `stats.has_solution`. The only available solver is
  **HiGHS** (`pulp.listSolvers(onlyAvailable=True) == ['HiGHS']`).
- **HiGHS** (`highspy`) is also installed directly for scaling experiments.
- Exact solves are for small instances (≤ ~30 items) for now; scaling is a
  later TODO phase.
- **Caution:** `report/main.qmd` and its code still build lane-scoped classes
  (mixing both service levels) and interpret CRF orders as reassignable — the
  (lane × svc) scoping and CRF exclusion above are recorded in `TODO.md`
  Phase 2 but **not yet implemented** in the notebook; treat its rendered
  numbers as pre-decomposition.

## Writing & citations

- Bibliography is `refs.bib`; entries were verified (e.g., the VSBPP origin
  paper is **Friesen & Langston**, *SIAM J. Comput.* 15(1), 1986 —
  *not* "Friesen & Kuo"). Cite library work via verified DOIs; never invent
  page numbers.
- Dataset provenance: cite `routeopt2022` (GitHub accelerator, MIT) and
  `routeopt2026` (Kaggle mirror). The fleet table must be attributed to
  `src/core/structure.py`, **not** to the repository README (which lists an
  older 3-type table).
- The **legacy** freight dataset and its companion paper (Dzalbs & Kalganova
  2020, `dzalbs2020`) stay in `refs.bib` for the case study; they are not the
  primary instance anymore.
- Verified references live in **both** `refs.bib` and the local Zotero
  collection *"Programação Matemática — Bin Packing (VSBPP)"* (key
  `VRWHXMP6`, writable via `zotero-cli` — local API write is already
  authorized); add new bibliography entries to both.
- That collection is split in two: the **parent** holds the theory/method
  references, and the subcollection **`Datasets`** (key `B75NG9DP`) holds the
  data/software entries (`dataset2026`, `dzalbs2020`, `routeopt2022`,
  `routeopt2026`). Zotero's parent view does not inherit subcollection items, so
  a dataset entry lives **only** in `Datasets`. Current counts: 14 + 4 = 18 =
  the number of `refs.bib` entries.
- The author block in `report/main.qmd` is still a TODO placeholder.
- Documentation and the report are written in **pt-BR** (see Language);
  this file stays in English.

## Git

- Commit environment changes (`devenv.*`, `requirements.txt`) together with
  the code change that requires them.
- `output/` artifacts, `__pycache__`, `.devenv` state, and Quarto's
  `report.quarto_ipynb` caches are not committed.
