# AGENTS.md — bin-packing-problem

Guidance for coding agents working in this repository (USP *Programação
Matemática* project: a variable-size/cost bin packing model — VSBPP — built on
real freight logistics data).

## Language

- **All repository documentation — `TODO.md`, `DATASETS.md`, the deliverable
  report `report.qmd`, and any new workspace document — is written in
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
| `report.qmd` + `refs.bib` | IEEE-formatted Quarto report/notebook (the deliverable) |
| `_extensions/ieee/` | Vendored `dfolio/quarto-ieee` journal format extension |
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
  re-rendering `report.qmd` end to end.
- **`pdf-engine` for `report.qmd` must be `pdflatex`.** Quarto's engine
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
devenv shell -- render-report          # devenv script (report.qmd → output/)
```

The script pins `QUARTO_PYTHON` to the project's venv interpreter. The venv
has `nbclient`/`nbformat` because quarto's kernel runner needs them.

## Domain vocabulary — terminology is part of the model

- This is **VSBPP** (variable-size/cost bin packing): items are **orders**
  (weight $w_i$ in kg); bins are **freight bookings**; bin **classes** are
  tariff lines with $C_k$ = `max_wgh_qty`, $l_k$ = `minm_wgh_qty`,
  $f_k$ = `minimum cost`.
- **Class key** — mirrors the companion paper's line index $pjcstm$, restricted
  to one lane:
  $k = (\text{carrier},\ \text{svc\_cd},\ \text{tpt\_day\_cnt},\ \text{mode\_dsc},\ \text{bracket})$.
  In the air-only instances it collapses to
  $(\text{carrier},\ \text{svc\_cd},\ \text{bracket})$, and that collapse must be
  **stated explicitly** wherever the model is written down. Never let one class
  mix `mode_dsc` values or transit days without declaring it.
- A **bracket is a price, not a resource.** Brackets are weight bands of a
  tariff schedule: each consignment is priced by the band containing *its own*
  weight, so the same carrier × svc can be booked any number of times, in as
  many different brackets as needed. R4 ("one class per booking") is
  per-consignment pricing — it is **not** carrier-level exclusivity. There is no
  per-carrier booking quota anywhere in the dataset (`tpt_day_cnt` is transit
  time in days, 0–14; `Carrier type` is a grouping code) and the paper imposes
  none (its eq. (4) is per line).
- Say **booking/shipment**; transport mode is `AIR`/`GROUND` (`mode_dsc`) — see
  the mode facts below before assuming "air".

## Data facts (already verified — do not re-derive)

- Source: Kaggle `omarstat2/supply-chain-logistics-data` (Brunel figshare),
  fetched via the public mirror `Eden1029/SQL_SupplyChainLogistics` —
  identical schema: `OrderList` 9,215 × 14, `FreightRates` 1,540 × 11.
- All orders share one date (2013-05-26). Workload decomposes into priced
  VSBPP instances **per (lane × service level)**; CRF orders are excluded
  (see below): `PORT04→PORT09`×DTP 6,184 orders and ×DTD 2,143;
  `PORT09→PORT09`×DTP 34 (GROUND-only — see mode facts below); CRF totals 854
  across the three lanes, so
  `PORT05→PORT09` has no priced instance at all.
- Service levels (`svc_cd`): `DTP` = Door to Port, `DTD` = Door to Door, `CRF`
  = Customer Referred Freight. The customer *requires* the service level, so a
  booking (carrier × svc × bracket) may only serve orders of its **own**
  service level — that is why instances are scoped per (lane × svc).
- CRF orders (854, always on the discontinued carrier `V44_3`, which has no
  `FreightRates` rows) ship customer-arranged at transport cost **0** per the
  companion paper's Fig. 3 — they are **excluded from the packing instances**,
  not reassigned to priced bookings.
- Billing rule (verified against the companion paper, Fig. 3): the per-kg
  `rate` is charged on the **whole consignment weight** and the tariff band is
  selected by that weight; the true fee is $\max(R_k\, w,\ f_k)$ — there is no
  charging on the weight excess above `minm_wgh_qty`. The MILP objective
  carries **both** terms, $f_k\,y_{jk} + R_k\,q_{jk}$, with the epigraph R6
  (see Solver stack); a fee-only objective is only a lower bound on the real
  cost.
- **Mode is not uniform, and it is not implied by (carrier, svc_cd).**
  `mode_dsc`: 1,511 `AIR` + 29 `GROUND` rows, and `V444_0`/`V444_5` sell **both**
  modes in both service levels. Lane composition: `PORT04→PORT09` and
  `PORT05→PORT09` are 100% `AIR` (mode may be collapsed away there);
  `PORT09→PORT09`×**DTP has zero AIR rows — it is 100% GROUND** (`V444_0`
  rate 12.28 / `V444_5` rate 20.28, single window [0, 5000], `minimum cost`
  31.28), so never present it as an air instance; `PORT09→PORT09`×DTD mixes
  `AIR` (`V444_8`) with 4 `GROUND` rows.
- **GROUND is billed by Fig. 3 rule 2, not by $\max(Rw, f)$**: the order pays a
  proportional share (by weight) of the per-line / full-truck rate, and the
  GROUND schedule is one [0, 5000] bucket with no weight bands. Derive the cost
  rule explicitly before modelling any GROUND instance.
- The same (carrier, lane, svc, bracket window) can appear on **several rows**
  differing in `tpt_day_cnt` and even in `minimum cost` — 132 of 1,258 windows
  (91 with a different `rate`, 112 with a different `minimum cost`). E.g.
  `V444_8` DTD sells 14/5/2/0-day variants of every bracket with different
  rate+fee, and `V444_1` carries twin fees (11.63 / 11.23) per day class. Any
  collapse needs an explicit, documented rule (keep the cheapest fee; transit
  time is not a customer constraint in our scope) — otherwise the collapsed
  rows linger as twin classes that only add symmetry.
- Some carriers' brackets are quoted in **pounds** (granularity of
  0.45359237) — normalize to kg during preprocessing.
- 2 zero-weight orders exist (both `PORT04→PORT09`×DTP): keep them in the
  committed dataset, but **leave them out of the MILP** — they are cost-neutral
  and only create $B^{z}$ cost-identical optima ($B$ = open bookings) stacked on
  top of the $n!$ slot symmetry; size the slot set by the positive-weight order
  count and post-assign the two zeros to any open booking.
- `FreightRates.csv` has comma-quoted numerics with malformed-looking quote
  artifacts (`000.00"` / `99999.99"`) in the header row — parse
  quote-aware.
- `WarehouseCosts.csv` ends with a stray empty record (`,\r\n`) → one `NaN`
  row when read naively; guard joins by `Plant ID`.
- `WhCapacities` is orders/**day** throughput — **not** usable as a bin
  capacity.
- `FreightRates` includes a pricing baseline per order; the per-order
  carrier assignment is the *baseline*, not a constraint of our model.

## Solver stack

- MILP modeling: **PuLP**. Objective
  $\min \sum_{j,k}\big(f_k\,y_{jk} + R_k\,q_{jk}\big)$ — the dataset tariff
  $\max(f_k,\ R_k W_j)$ linearized by the epigraph R6
  ($q_{jk} \ge W_j - \beta_k y_{jk} - M(1-y_{jk})$, $M=\max_k C_k$,
  $\beta_k=f_k/R_k$) — with constraints R1–R6 as stated in
  `report/sections/modelagem-matematica.md`.
- **PuLP in the venv is 4.2.x**: `LpVariable.dicts`, `PULP_CBC_CMD` and
  `pulp.LpStatus` **no longer exist**. Use
  `m.add_variable_dicts(name, (idx0, idx1), cat="Binary")` (nested dicts,
  `x[i][j]`), `stats = m.solve(pulp.HiGHS(msg=False))`, then
  `stats.objective` / `stats.has_solution`. The only available solver is
  **HiGHS** (`pulp.listSolvers(onlyAvailable=True) == ['HiGHS']`).
- **HiGHS** (`highspy`) is also installed directly for scaling experiments.
- Exact solves are for small instances (≤ ~30 items) for now; scaling is a
  later TODO phase.
- **Caution:** `report.qmd` and its code still build lane-scoped classes
  (mixing both service levels) and interpret CRF orders as reassignable — the
  (lane × svc) scoping and CRF exclusion above are recorded in `TODO.md`
  Phase 2 but **not yet implemented** in the notebook; treat its rendered
  numbers as pre-decomposition.

## Writing & citations

- Bibliography is `refs.bib`; entries were verified (e.g., the VSBPP origin
  paper is **Friesen & Langston**, *SIAM J. Comput.* 15(1), 1986 —
  *not* "Friesen & Kuo"). Cite library work via verified DOIs; never invent
  page numbers.
- Dataset pricing/service-level semantics come from the companion paper
  **Dzalbs & Kalganova 2020**, *Computers & Industrial Engineering* 147:106610
  (`refs.bib`: `dzalbs2020`; green OA at arXiv:2001.08102) — cite it whenever
  billing or dispatch claims need a source.
- Verified references live in **both** `refs.bib` and the local Zotero
  collection *"Programação Matemática — Bin Packing (VSBPP)"* (key
  `VRWHXMP6`, writable via `zotero-cli` — local API write is already
  authorized); add new bibliography entries to both.
- The author block in `report.qmd` is still a TODO placeholder.
- Documentation and the report are written in **pt-BR** (see Language);
  this file stays in English.

## Git

- Commit environment changes (`devenv.*`, `requirements.txt`) together with
  the code change that requires them.
- `output/` artifacts, `__pycache__`, `.devenv` state, and Quarto's
  `report.quarto_ipynb` caches are not committed.
