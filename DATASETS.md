# Dataset Research — Real Candidates per Use Case

Companion to [`TODO.md`](./TODO.md) (Phase 2) and the project brief
[`Projeto_PM_BCC_2026.md`](./Projeto_PM_BCC_2026.md). Each candidate dataset is
mapped onto the **generic BPP formulation** from the brief: items $I$ with sizes
$w_i$, bins $J$ with capacity $C$, decision $x_{ij}$, $y_j$, objective
$\min \sum_j y_j$.

The five use cases named in the brief were used as keywords: **(1)**
carga/veículos · **(2)** consolidação de VMs · **(3)** backup/arquivamento ·
**(4)** armários de laboratório · **(5)** diagramação de provas.

**Fit legend:**

🟢 strong (1:1 mapping, real data)

🟡 moderate (needs preprocessing/derivation)

🔴 weak (illustrative only).

---

## 0. Synthetic reference — _Pick and Place Binning Dataset_ (current default)

|             |                                                                                                                                                           |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Source**  | [Kaggle `panavraaj/pick-and-place-binning-dataset`](https://www.kaggle.com/datasets/panavraaj/pick-and-place-binning-dataset)                             |
| **Type**    | Synthetic, MIT license, usability 7.5, ~188 MB (JSON)                                                                                                     |
| **Content** | Binning instances at 6 sizes (3/5/10/40/100/200 objects): `objects` (sizes), `bins` (capacities), precomputed `greedy_sequence` + `greedy_cost` baselines |

**Relation to use case (cargo/allocation):** generic stand-in. Objects =
packages ($w_i$), bins = truck/container capacity ($C$). The bundled
`greedy_cost` baselines make it valuable for the report's **alternative-method
section** (every instance has a documented greedy reference to beat, and makes
MILP optima directly comparable). Caveat: **no real demand/weight distribution**
— synthetic generator, so the report must be honest that instances reflect a
synthetic generator, not field data. Any of the real datasets below can
supersede it as the "real-world claim," or they can be combined (greedy-baseline
benchmark + real instances as validation).

---

## 1. Alocação de Cargas em Veículos (truck/container loading)

### 🟢 Supply Chain Logistics Optimization Dataset — _real research benchmark_

- **Source:**
  [Kaggle `omarstat2/supply-chain-logistics-data`](https://www.kaggle.com/datasets/omarstat2/supply-chain-logistics-data)
  (originating from research at Brunel University London)
- **Relates:** `OrderList` — **9,215 real customer orders** with weights, units,
  shipping dates and ports; `FreightRates` encodes **weight brackets** (min/max
  per tariff tier); `WhCapacities` — 19 daily throughput capacity limits.
- **BPP mapping:** items $i$ = order lines, $w_i$ = `OrderList` weight; bins =
  trucks/containers, $C$ = chosen weight-bracket threshold; objective = min
  trucks per shipping date bucket. Optionally extend to cost minimization (min
  Σcᵢⱼxᵢⱼ) if asking for tariff rate targets — nice bridge to the "minimize
  cost/waste" variant the brief explicitly allows.

### 🟢 Large-Scale Route Optimization (Microsoft solution accelerator)

- **Source:**
  [Kaggle `mexwell/large-scale-route-optimization`](https://www.kaggle.com/datasets/mexwell/large-scale-route-optimization)
- **Relates:** item-to-truck assignment; items carry `Area (m²)` and
  `Weight (kg)`; 3 truck types with capacity on both dimensions (16.5 m: 10,000
  kg / 16.1×2.5 m², 12.5 m: 5,000 kg / 12.1×2.5 m², 9.6 m: 2,000 kg / 9.1×2.3
  m²).
- **BPP mapping:** formally a VRP/VRPPD variant; by **ignoring
  routing/timing/deadlines**, the _pure bin-packing core_ is exactly the model
  in the brief (items with wᵢ, heterogeneous bins with capacity D).
  Heterogeneous-capacity bins ($C_j$ varying per truck type) are an easy
  generalization of the brief's constant-C formula — a wrinkle worth flagging in
  the report's "what we generalized" narrative.

### 🟢 Cross-Border E-commerce Logistics Data (China)

- **Source:**
  [Kaggle `zara2099/china-cross-border-logistics-data`](https://www.kaggle.com/datasets/zara2099/china-cross-border-logistics-data)
- **Relates:** 7,000 shipment records with `package_weight_kg` and
  `package_volume_cbm` per shipment.
- **BPP mapping:** cargo use — instant item set ($w_i$ = package weight/volume).
  Weakest of the three causally because it lacks container capacity specs (C
  must be imported from industry standard, e.g. 28.8 m³ 40-ft container) —
  acceptable and citable via brief.

---

## 2. Consolidação de Máquinas Virtuais (Cloud Computing)

### 🟢 Azure Traces for Packing 2020 — _purpose-built for packing research_

- **Source:**
  [`Azure/AzurePublicDataset` → `AzureTracesForPacking2020`](https://github.com/Azure/AzurePublicDataset/blob/master/AzureTracesForPacking2020.md)
  (hosted as GitHub releases) · cite the Azure OSDI'20 paper "Protean: VM
  Allocation Service at Scale".
- **Relates:** packed **VM requests along with their priority**, lifetime, and
  **normalized resources allocated** per VM type — released by Azure
  _specifically to evaluate packing/bin-packing algorithms_. This is today's
  standard: recent packing/consolidation evaluations (e.g., PUVAR 2023; 2025–26
  vector-BP workloads) all benchmark on it.
- **BPP mapping:** items = VM requests ($w_i$ = normalized CPU+RAM demand), bins
  = physical hosts ($C$ = host capacity), objective = minimize the number of
  active hosts. The request **priority** field also opens a richer extension
  (guaranteed vs. best-effort placement precedence) — simulated as 1D first, an
  honest extension rather than a hidden assumption.

### 🟢 Hosted on PlanetLab/CoMon (10-day traces, Mar–Apr 2011)

- **Source:** public workload traces distributed through the CoMon monitoring
  project; **the canonical BPP/VM-consolidation benchmark** in the
  heuristic/meta-heuristic literature from 2011–2022 (e.g., OpenStack Neat /
  CloudSim MBFD evaluations, UP-VMC, AEDQN-VMC). CPU utilization of > 1,000 VMs
  sampled every 5 min; standard practice filters to 5–90% utilization and slices
  per day.
- **Relates:** CPU/RAM demands per VM per day → $w_i$; physical server capacity
  → $C$; minimizing active hosts is classic consolidation as a 1D BPP.
- **BPP mapping:** identical to above. The standard practice in the
  consolidation literature — slicing the traces into one instance per day — maps
  directly onto the project's toy/medium/large bucketing.

### 🟢 Google Borg traces 2011/2019 and Bitbrains Grid Workloads Archive

- **Source:**
  [github.com/google/cluster-data](https://github.com/google/cluster-data)
  (CC-BY) · [Bitbrains / Grid Workloads Archive](https://www.gridworkloads.org/)
  — 1,750 VMs from managed-hosting clusters (fastStorage 1,250 VMs + Rnd 500
  VMs, 30 days, sampled every 5 min).
- **Relates:** real memory/CPU utilization time series; academic
  freely-accessible, widely cited in CloudSim + empirical consolidation papers.
- **BPP mapping:** same as above, with richer multi-dimensional resources
  possible (CPU, memory). Both are real and can anchor the "real data" claim in
  the report. Azure Packing-2020 remains our first pick: normalized resources
  make the 1D reduction clean, and per-VM request sizes fit neatly with the
  plan's "medium bucket ≤ 60 items for exact solver" split.

---

## 3. Backup e Arquivamento de Dados (media/volume allocation)

### 🟢 LANL Anonymous Filesystem Walk Metadata (file sizes truly real)

- **Source:**
  [LANL Storage Data (fsstats 2011/2012 + archive/NFS walks)](https://usrc.lanl.gov/data/storage-data.php),
  released under LA-UR-07-5769.
- **Relates:** a real datacenter file-system walk: **112M+ records with file
  sizes**, create/mod times, UID/GID per file — no fabrication, from Los Alamos
  National Laboratory.
- **BPP mapping:** items = files/datasets ($w_i$ = file size in GB), bins =
  storage volumes ($C$ = media capacity). Industrial grounding for $C$ and size
  limits comes from real deployment literature: the Oklahoma PetaStore reports
  "LTO-5 1.5 TB / LTO-6 2.5 TB tapes, min file 1 GB, max 250 GB, recommended
  pack 10–100 GB" (Calhoun, _J. Comput. Sci._ 2016) — giving industrial
  constraints on both $C$ and admissible $w_i$. The "no file > C" rule adds the
  unsplittable-item edge case the brief's capacity constraint already implies.

### 🟢 SDSS Data Volume Tables (datasets as big items)

- **Source:**
  [`sdss4.org/dr17/data_access/volume/`](https://www.sdss4.org/dr17/data_access/volume/)
  — real published volumes per SAS data product (e.g., `apogee/spectro/redux` 52
  TB, `manga/spectro/analysis` 9.7 TB, `eboss/lss` 1.07 TB...).
- **Relates:** backing up an institution's research data at the level of
  aggregated **projects/data products** (item sizes GB–TB, far better matched to
  the brief's "university backup scenario" than raw small-file walks). SDSS
  publicly documents each product's volume and file count, so item granularity
  can be chosen at either the product level or the file level.

---

## 4. Alocação de Armários e Espaços nos Laboratórios (weakest real-data fit)

### 🟢 Zenodo: Weekly-demand rack-loading generator (Hoare & Beasley catalogue)

- **Source:** [Zenodo record 23104538](https://doi.org/10.5281/zenodo.23104538)
  (Souyri, Lahrichi & Rousseau, 2026) — 105 instances × 104 weeks (qty;
  length,width,height per item); **item dimensions come from the real retail
  stockroom catalogue of Hoare & Beasley (2001), distributed via the
  OR-Library**; quantities synthetic.
- **Relates:** rack-loading in a sterilization/logistics setting — item families
  with mm-accurate dimensions plus weekly demand quantities, packed into racks
  with finite cross-section capacity.
- **BPP mapping:** the closest real checkpoint to "locker/room allocation":
  items = equipment families (usable length per unit), bins = locker/rack bays,
  $C$ = the bay's usable row length. The brief's 1D formulation holds when bays
  are uniform; the item width/height columns additionally allow a 2D extension
  as future work (as the brief itself suggests).

### 🟡 Physical lab-space audit data (you need this for the report narrative)

- **Source:** two real academic audits of lab storage utilization —
  [Kennesaw State DigitalCommons, Precision Lab space study at Siemens Energy](https://digitalcommons.kennesaw.edu/egr_srdsn/27)
  (shelf/cabinet cube dimensions measured in cubic ft; ~10.45% lab-space used
  for storage) and an NTU Biological Sciences lab 5S/space optimization study
  ([Kia Min Wee 2018](http://hdl.handle.net/10356/76414)), plus a national-lab
  facility **equipment measurement survey**
  ([Hebert & Kang 2015 — 361 large equipment pieces located, measured, categorized into 6 groups](https://exa.ai/library/publication/dhbzf10y1bg)).
- **Relates:** these provide the brief's _industrial context_ for the report
  introduction: equipment families (analytical vs. storage vs. process),
  measured cabinet/shelf dimensions and storage volumes of real lab spaces. But
  they are survey-type data (a handful of items per site), not ready-made BPP
  instances.
- **BPP mapping:** the Hebert & Kang measurements supply equipment counts +
  physical categories almost directly; the lab-space audits supply
  $C_{\text{locker}}$ via measured cube volumes. Honest assessment: fit is 🟡 —
  enough to state "real equipment types and locker dimensions from published
  audits," but instances must be aggregated from descriptive statistics rather
  than complete item-level data.

---

## 5. Diagramação e Alocação de Questões em Provas (page-space allocation)

### 🟢 Open exam-question corpora (questions with measured text lengths)

- **Sources:**
  - [HF `datavorous/entrance-exam-dataset`](https://huggingface.co/datasets/datavorous/entrance-exam-dataset)
    — 44.4k real JEE-Advanced [2006–2024] questions with stems, exam/subject
    tags, and per-question metadata.
  - [HF `letmarchezi/ENEM_Brazil_National_High_School_Exam_2022_to_2024`](https://huggingface.co/datasets/letmarchezi/ENEM_Brazil_National_High_School_Exam_2022_to_2024)
    — full official **ENEM 2022–2024 papers** as PDF extracts (Brazilian,
    matches USP context!).
  - [HF `OpenTWBench/tw-exam-bench`](https://huggingface.co/datasets/OpenTWBench/tw-exam-bench)
    — 30 official ROC Taiwan public-service exams (Apache-2.0; official Ministry
    data).
- **Relates:** every question is an item $i$; $w_i$ = **estimated rendered
  height** (derived from question character/token count + option block heights;
  a calibration constant per font size bridges text lengths to print space).
  Bins = exam pages: $C$ = printable content area minus headers/margins. One
  extra integer nuance: a question must fit entirely within a page (no
  fragmentation between pages — the brief explicitly mentions this as a
  secondary goal).
- **BPP mapping:** packing questions into pages while minimizing the page count
  **is the brief's use case verbatim** ("minimizar o número total de páginas
  impressas"), and ENEM is maximally contextual (Brazilian official exams — the
  exact audience of the report). Two caveats to state openly in the report: (a)
  rendered heights must be _derived_ from question text lengths (a calibration
  constant per font size; the exam-length study of Lin, Lu & Lien 2021 — 611
  real items averaging 88.8 words/item — offers published calibration); (b) the
  derived heights should be validated against a sample of real ENEM page layouts
  before the solvers run on them.

---

## 6. Recommended course of action for the group

1. **Primary real dataset:** pick one use case and pair it with its top
   candidate:
   - cargo → `supply-chain-logistics-data` (OrderList → trucks)
   - VM consolidation → `AzureTracesForPacking2020` (purpose-made; also easiest
     framing)
   - backup → LANL filesystem walk + PetaStore industry capacities
   - lab lockers → Zenodo rack-loading (Hoare & Beasley catalogue) + published
     lab audit sizes
   - exam pagination → **ENEM 2022–2024 dataset** (most Brazilian-contextual and
     self-contained to explain)
2. **Keep the synthetic `pick-and-place-binning-dataset`** as the _"controlled
   benchmark"_ (has greedy baselines! clean 1D formula) precisely because every
   real candidate above needs preprocessing.
3. **Hybrid report story (fewest surprises):** Develop and tune on the synthetic
   instances → then apply the pipeline to many real instances (e.g. ENEM
   questions or VM requests via actor A3's preprocessing) as the **validation
   set**, and say so explicitly in the report. This matches Phase 2 of `TODO.md`
   (normalize to common `w_i` / `C` instances) and keeps both solvers +
   heuristic vs `L2` bound comparisons uniform.

**Provenance note:** all links above were verified as publicly available at the
time of writing (Oct 2026); consolidate them into `refs.bib`/bibliografia during
Phase 1 of [`TODO.md`](./TODO.md).
