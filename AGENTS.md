# AGENTS.md — bin-packing-problem

Guidance for coding agents working in this repository (USP _Programação
Matemática_ project: a variable-size/cost bin packing model — VSBPP — built on
the real-world route-optimization benchmark of `data/raw/`).

**Project state (2026-11):** modeling and preprocessing are closed; the report
has Introduction, Data, Preprocessing and Mathematical Modeling done. In
development: the solver-experiments section (metrics harness pending), the
alternative method, and the conclusion. The live tracker is `project.md`
(Pending Work) with per-item plans in `work/<slug>/README.md`.

## Language

- **All repository documentation and commit messages — the deliverable report
  `report/main.qmd`, `project.md`, `work/<slug>/README.md`, and any other
  workspace document — should be written in Brazilian Portuguese (pt-BR).
- `AGENTS.md` itself is kept in English (agent-facing guidance).

## Project layout

| Path                                                              | What it is                                                                                                                         |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `Projeto_PM_BCC_2026.md`                                          | Course brief (generic BPP formulation — the model must extend it). **Local only**: gitignored, not distributed with the repository |
| `notes/`                                                          | **Removed** (Nov 2026): the legacy phased plan, dataset annotations and experiment log. Dataset provenance now lives in the report (§III, `disponibilidade.qmd`); the deleted files remain recoverable from git history |
| `project.md` + `work/<slug>/README.md`                            | **Source of truth for project progress**: tracker (Goal/Background/Pending Work) and one plan+results file per work item            |
| `scripts/`                                                        | **Removed** in `62c702f` (Nov 2026) as unused; a solver-metrics harness is planned work (`work/solver-metrics-harness/`) — recreate there rather than resurrecting old references |
| `report/main.qmd` + `report/refs.bib`                             | IEEE-formatted Quarto report/notebook (the deliverable) — `report/` is self-contained                                              |
| `report/_extensions/ieee/`                                        | Vendored `dfolio/quarto-ieee` journal format extension (must sit next to `main.qmd`)                                               |
| `data/raw/*.csv`                                                  | Committed dataset files — **keep them tracked, never re-fetch or gitignore**                                                       |
| `data/pre-processed/`                                             | Generated instances and groups (`instances.csv`, `groups.csv`, `meta.json`) — versioned, regenerable in ~0.2 s                     |
| `presentations/`                                                  | Class presentations (untracked so far)                                                                                            |
| `pyrightconfig.json` / `ruff.toml`                                | Type checking (basedpyright) and lint config                                                                                       |
| `devenv.nix` / `devenv.yaml` / `devenv.lock` / `requirements.txt` | Declarative environment                                                                                                            |

## Environment rules (NixOS + devenv)

- **Never install anything imperatively.** No `pip install`, no ad-hoc downloads
  of tools. Python deps go in `requirements.txt` (managed venv, devenv
  reinstalls only on file change); system tools go in `devenv.nix` `packages`.
  If a command is missing from PATH in a pinch, use the `,` (comma) tool prefix
  for one-off programs, but record the outcome as a proposed devenv edit.
- Work inside the shell (`devenv shell -- <cmd>` or direnv).
- **Quarto is pinned to 1.6.43** via the `nixpkgs-quarto` input (`devenv.yaml`;
  there is a comment explaining why). Do not bump it without re-rendering
  `report/main.qmd` end to end.
- **`pdf-engine` for `report/main.qmd` must be `pdflatex`.** Quarto's engine
  whitelist is only pdflatex/xelatex/lualatex/latexmk — setting `tectonic` makes
  the custom-template format fail with the cryptic error _“the format pdf does
  not support providing any template partials”_.
- Missing LaTeX package at render time → add that specific package to the
  `texlive.withPackages` list in `devenv.nix`; do not switch to a bigger scheme
  wholesale.
- Missing Python module at render time → add to `requirements.txt`.
- File-editing rule: use the **edit tool** for modifications; `write` only for
  brand-new files. Stop and ask instead of working around it.

## Rendering

```bash
devenv shell -- render-report          # devenv script (report/main.qmd → report/main.pdf)
```

There is **one** PDF location: `report/main.pdf`, written next to the source by
both the script and `:QuartoPreview` in Neovim. Do not pass `--output-dir` —
Quarto resolves it relative to the *input file*, which is how a second copy
under `report/output/` used to appear. `report/main.pdf` is tracked in git (it
is the deliverable); the `report/main_files/` intermediates are ignored.

The venv interpreter (it has `nbclient`/`nbformat`, which quarto's kernel runner
needs) is pinned by the **patched `quarto` wrapper** defined in `devenv.nix` —
not by the script. nixpkgs' `quarto` wrapper prepends its own python through
`--prefix QUARTO_PYTHON :`, which turns the variable into a `:`-joined list;
Quarto rejects it and falls back to the first `python3` on `PATH`, which is
_not_ the venv when `.devenv/profile/bin` comes first (the resulting failure is
`ModuleNotFoundError: No module named 'yaml'` / `Jupyter: (None)`). Do **not**
reintroduce `env.QUARTO_PYTHON`, and don't "simplify" that `runCommand` away:
the render works the same from `devenv shell`, direnv and editors
(`quarto preview` in Neovim) only because of it.

## Domain vocabulary — terminology is part of the model

- This is **VSBPP** (variable-size/cost bin packing): items are **packages**
  (`Item_ID`; size = area in m² **and** weight in kg); bins are **trucks**; bin
  **classes** are the four truck types with $(A_t, W_t, c_t)$ — area capacity,
  weight capacity and cost per km.
- **The instance is two-dimensional.** A truck is feasible only if
  $\sum_i a_i x_{ij} \le A_t$ **and** $\sum_i w_i x_{ij} \le W_t$. Never
  collapse it to 1D without saying so: package density (median 589 kg/m²,
  computed from `order_large.csv`) sits just below the 16.5 m truck's ratio
  (671 kg/m²), and the route-by-route fleet lower bounds give 270 trucks by
  area vs 226 by weight — so **area binds more often than weight**.
- **Cost is per km, not per truck and not per kg.** For a fixed lane $(o,d)$ a
  truck of type $t$ costs $c_t \times \mathrm{dist}(o,d)$: a fixed charge per
  bin. The model is a fixed-charge VSBPP, not a tariffed per-kg problem.
- Say **item/package** and **truck**. The old freight vocabulary (orders,
  bookings, tariffs, `rate`/`minimum cost`) belongs to the **legacy case study**
  and must not leak into the new model.

## Data facts (already verified — do not re-derive)

- **Primary dataset:** `mexwell/large-scale-route-optimization` (Kaggle, MIT),
  mirror of the Microsoft _Large-Scale Route Optimization_ accelerator
  (`microsoft/dstoolkit-route-optimization`, MIT). Files in `data/raw/`:
  `order_small.csv` (10 items, 2 lanes), `order_large.csv` (**4,635 items**, 365
  orders, **61 O–D pairs**), `distance.csv` (metres), `trucks.csv` (fleet,
  transcribed from `src/core/structure.py`).
- **Units:** `Area` and `Weight` are scaled by $10^4$ — divide by 10,000 to get
  m² and kg. Work in m²/kg (or convert the capacities the same way).
- **Fleet (the code is authoritative; the repo README lists an older 3-type
  table with 10/5/2 t):** 16.5 m → 40.25 m² / 27,000 kg / 10.0 per km; 12.5 m →
  30.25 m² / 24,000 kg / 9.0; 9.6 m → 20.93 m² / 14,000 kg / 6.5; 7.6 m → 16.56
  m² / 8,000 kg / 5.5.
- **Cost per unit capacity is monotone in truck size** ($c_t/A_t$ falls from
  0.332 to 0.248 \$/m²; $c_t/W_t$ from 0.00069 to 0.00037 \$/kg) — a coherent
  "bigger is cheaper per unit" schedule, unlike the legacy freight table.
- Item distributions: area 0.64–9.72 m² (median 1.25), weight 46–3,130 kg
  (median 1,000); **no item exceeds the largest truck**; density median 589
  kg/m².
- **Preprocessing decomposition (measured, in `data/pre-processed/meta.json`):**
  4,635 packages collapse into **239 identical-package groups**; the (route ×
  day) decomposition yields **111 MILP instances**, of which **44 close by
  inspection** (no MILP needed) and **0 items are infeasible** by
  window/weight/area. Largest instance: 198 packages in **11 groups** — no
  instance exceeds 11 groups.
- Consolidation windows: median availability window per route is 24 h (max
  56 h) against $\Delta = 4$ h ⇒ wide consolidation is impossible by
  construction.
- `Distance(M)` is in **metres**, despite the column name.
- The data is a **published sample** "inspired by a real-world scenario" of a
  manufacturing customer — not raw company data; state that in the report.
- `Danger_Type`, `Available_Time` and `Deadline` enable extensions (incompatible
  items, time windows) that the core BPP ignores.
- **Legacy (documented, not used):** the freight dataset
  (`omarstat2/supply-chain-logistics-data`) was dropped as primary in 2026-10 —
  its `minimum cost` sits below the implied floor price in 78% of classes
  (median $f/(R\,l)=0.09$), `V444_4` has a `rate` **increasing** with weight,
  and `PORT09→PORT09`×DTP is 100% GROUND with a different cost rule (full
  annotations were in `notes/DATASETS.md`, recoverable from git history).

## Solver stack

- MILP modeling: **PuLP**. The official model is the **aggregated
  fixed-charge, two-dimensional VSBPP (R1–R10)**, restated in
  `report/sections/metodologia/modelagem-matematica/` (authoritative statement:
  `sumario.qmd`): the instance is defined over **groups $g$ of identical
  packages** (same area, weight, availability, deadline) with multiplicity
  $n_g$; decisions are $z_{gj} \in \{0,\dots,n_g\}$ (how many packages of $g$
  go in truck $j$), $u_{gj} \in \{0,1\}$ (group used in $j$), $y_{jt} \in
  \{0,1\}$ (truck type) and $\tau_j \ge 0$ (departure time):
  $\min \sum_{j,t} C_t\, y_{jt}$ with $C_t = c_t\,\mathrm{dist}(o,d)$, subject
  to R1 (assignment $\sum_j z_{gj} = n_g$), R2/R3 (area and weight capacity),
  R4 (one type per truck), R5 (linking), R6 (occupancy), R7–R9 (availability,
  consolidation window $\Delta$, deadline) and R10 (open trucks occupy a
  prefix). The item-to-item formulation (binary $x_{ij}$, with the R11
  package-symmetry cut) is **historical/reference only** — it validated the
  aggregated objective on small instances; R11 vanished with the item index.
  The freight formulation R1–R6 with the $\max(f, RW)$ epigraph is **legacy**
  (kept only for the case study).
- **Solvers in the venv (verified):** `pulp.listSolvers(onlyAvailable=True)`
  → `['GUROBI', 'GUROBI_CMD', 'HiGHS']`. **Gurobi 13.0.3** (`pkgs.gurobi` +
  `gurobipy==13.0.3`) with an academic license in `gurobi.lic` at the repo
  root — **gitignored**, wired through `GRB_LICENSE_FILE` in `devenv.nix`;
  without the license Gurobi falls back to the restricted size (2,000
  vars/rows), insufficient for the instances. **HiGHS** (`highspy`) is also
  installed directly.
- **PuLP is 4.2.x**: `LpVariable.dicts`, `PULP_CBC_CMD` and `pulp.LpStatus`
  **no longer exist**. Use
  `m.add_variable_dicts(name, (idx0, idx1), cat="Binary")` (nested dicts,
  `x[i][j]`), `stats = m.solve(pulp.HiGHS(msg=False))` (or
  `pulp.GUROBI(msg=False)`), then `stats.objective` / `stats.has_solution`.
- The aggregation makes every instance small in *groups* (≤ 11), but hard
  routes still spike (`City_48`, `City_54`); the pending harness
  (`work/solver-metrics-harness/`) re-collects that node/time evidence.
- **`scripts/` is gone** (removed in `62c702f`): the symmetry/parity benchmarks
  ran from there; their measured findings were logged in `notes/EXPERIMENTOS.md`
  (deleted — recoverable from git history). Do not treat the old script paths
  as existing.
- **Caution:** the report's executable chunks (numbers come from code, never
  typed) now live in `report/sections/introducao.qmd`,
  `metodologia/base-de-dados/*` (route network, package density, trucks per
  route, orders), `metodologia/pre-processamento/*` (normalização, redução,
  custo) and `metodologia/modelagem-matematica/*` (instance sizes, parameter
  tables, constraints, complexity), all computed from `data/raw/` +
  `data/pre-processed/`. The legacy notebook draft
  `report/sections/experimento.qmd` is **not included** in `main.qmd`; treat
  its numbers as pre-decomposition. The legacy (lane × svc) scoping and CRF
  exclusion are recoverable from git history (`notes/DATASETS.md`, deleted).

## Report prose style (pt-BR)

Decisions fixed in the Nov 2026 style pass; keep new prose consistent with them.

- **Voice.** Impersonal for descriptions and results; first-person plural
  ("nosso", "faremos") only for deliberate authorial/modeling decisions
  (abstract, objectives, formulation choices). Never "o nosso dataset" — the
  dataset head-noun in prose is **"conjunto"** ("o conjunto", "o conjunto de
  referência"); "dataset" survives only in the section title and code-adjacent
  contexts.
- **Emphasis.** Inline numbers are never bolded — the prose carries the
  emphasis; bold is reserved for term definitions, concepts and list lead-ins
  (e.g., **classes**, **grupos de pacotes idênticos**).
- **Em-dash.** At most one per sentence; asides go in parentheses or commas;
  keep the dash only for true contrast ("não fragmenta a instância
  artificialmente — ele reflete...").
- **Stock phrases.** "consequência direta", "mordem/morde" (capacity metaphor),
  "regra de bolso": at most one occurrence each in the whole report.
- **Foreign/technical terms.** Italic + gloss on first use only (_bin packing
  problem_, _slots_ (posições), _first fit decreasing_ (FFD), _gap_ de
  otimalidade), plain afterwards.
- **Reserved words.** "teto" = the slot cap ($m$); the VRP bound is "limite
  superior". Legacy freight vocabulary ("reserva", "tarifa", "pedido
  solicitado") stays out of the new-model prose.
- **Numbers and units.** Every inline number comes from a `{python}` chunk via
  `ptbr()`; hard-coded constants survive only in the abstract and figure
  captions and must be re-verified against `data/raw/` after any edit. Always
  attach the unit (dias, h, km) — including after parenthetical medians.
- **Quoted translations.** Must preserve the source's logical content (e.g.,
  the Δ constraint is "deve ser **menor que** um limite definido pelo
  usuário").

## Writing & citations

- Bibliography is `refs.bib`; entries were verified (e.g., the VSBPP origin
  paper is **Friesen & Langston**, _SIAM J. Comput._ 15(1), 1986 — _not_
  "Friesen & Kuo"). Cite library work via verified DOIs; never invent page
  numbers.
- Dataset provenance: cite `routeopt2022` (GitHub accelerator, MIT) and
  `routeopt2026` (Kaggle mirror). The fleet table must be attributed to
  `src/core/structure.py`, **not** to the repository README (which lists an
  older 3-type table).
- The **legacy** freight dataset and its companion paper (Dzalbs & Kalganova
  2020, `dzalbs2020`) stay in `refs.bib` for the case study; they are not the
  primary instance anymore.
- Verified references live in **both** `refs.bib` and the local Zotero
  collection _"Programação Matemática — Bin Packing (VSBPP)"_ (key `VRWHXMP6`,
  writable via `zotero-cli` — local API write is already authorized); add new
  bibliography entries to both.
- That collection is split in two: the **parent** holds the theory/method
  references, and the subcollection **`Datasets`** (key `B75NG9DP`) holds the
  data/software entries (`dataset2026`, `dzalbs2020`, `routeopt2022`,
  `routeopt2026`). Zotero's parent view does not inherit subcollection items, so
  a dataset entry lives **only** in `Datasets`. Current counts: 19 + 4 = 23 =
  the number of `refs.bib` entries.
- The author block in `report/main.qmd` is filled in (five authors, ICMC-USP,
  ORCID of the first); keep it in sync with the group if it changes.
- Documentation and the report are written in **pt-BR** (see Language); this
  file stays in English.

## Git

- Commit environment changes (`devenv.*`, `requirements.txt`) together with the
  code change that requires them.
- `report/main_files/` intermediates, `__pycache__`, `.devenv` state, and
  Quarto's `report.quarto_ipynb` caches are not committed.
- **`gurobi.lic` and `gurobi.log` are gitignored** — never commit the license
  file.
- `project.md`, `work/` (and `.asta/` run outputs, when present) are the
  research workspace: research-workflow commits may touch them, but commits
  stay inside those paths — never mix them with report or code changes.
