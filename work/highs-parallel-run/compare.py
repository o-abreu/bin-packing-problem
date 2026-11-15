#!/usr/bin/env python3
"""Validação e comparação do terceiro braço (HiGHS parallel="on") contra os
dois braços do benchmark original (data/results/solver_metrics.csv)."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
antigo = pd.read_csv(ROOT / "data/results/solver_metrics.csv")
novo = pd.read_csv(ROOT / "data/results/solver_metrics_highs_parallel_parcial.csv")

par = novo[novo["solver"] == "HiGHS-parallel"].copy()
rep = novo[novo["instance"].str.contains("_rep", na=False)]
par = par[~par["instance"].str.contains("_rep", na=False)]

hi = antigo[antigo["solver"] == "HiGHS"].set_index("instance")
gu = antigo[antigo["solver"] == "Gurobi"].set_index("instance")
pa = par.set_index("instance")

# --- Validação -------------------------------------------------------------
assert (par["status"] == "Optimal").all(), "status não-ótimo no 3º braço"
d_hi = (pa["objetivo"] - hi["objetivo"]).abs()
d_gu = (pa["objetivo"] - gu["objetivo"]).abs()
tol = 1e-6 * (1 + hi["objetivo"].abs())
print(f"status Optimal: {len(par)}/{len(par)}")
print(f"|obj - HiGHS| máx: {d_hi.max():.3e} (violações: {(d_hi > tol).sum()})")
print(f"|obj - Gurobi| máx: {d_gu.max():.3e} (violações: {(d_gu > tol).sum()})")
fech = par[par["closed"]]
d_cl = (fech["objetivo"] - fech["closed_cost"]).abs()
print(f"fechadas por inspeção: {len(fech)}; |obj - closed_cost| máx: "
      f"{d_cl.max():.3e}" if len(fech) else "fechadas: 0")

# --- Logs ------------------------------------------------------------------
logs = sorted((ROOT / "data/results/logs").glob("HiGHSPAR__*.log"))
on = [p for p in logs if "Parallel search on" in p.read_text(errors="ignore")]
off = [p for p in logs if "Parallel search off" in p.read_text(errors="ignore")]
prep = [p for p in logs if "Parallel search" not in p.read_text(errors="ignore")]
print(f"\nlogs HiGHSPAR: {len(logs)}; 'Parallel search on': {len(on)}; "
      f"'off': {len(off)}; sem mensagem (presolve fechou): {len(prep)}")

# --- Comparação de tempos --------------------------------------------------
c = pa[["tempo_s"]].join(hi[["tempo_s"]], rsuffix="_hi").rename(
    columns={"tempo_s": "t_par", "tempo_s_hi": "t_hi"})
c["razao"] = c["t_hi"] / c["t_par"]
print("\n### instâncias com maior diferença (HiGHS seq vs parallel)")
print(c.sort_values("razao", ascending=False).head(8).to_string(
    float_format=lambda x: f"{x:.2f}"))
print("\n### mais lentas no paralelo")
print(c.sort_values("razao").head(5).to_string(
    float_format=lambda x: f"{x:.2f}"))

dura = "City_58_2022-04-06"
linha_dur = c.loc[dura]
print(f"\n### {dura}: seq {linha_dur['t_hi']:.1f}s | par {linha_dur['t_par']:.1f}s"
      f" | razão {linha_dur['razao']:.2f}×")
print(f"soma sem a dura: seq {hi.drop(index=dura)['tempo_s'].sum():.1f}s | "
      f"par {pa.drop(index=dura)['tempo_s'].sum():.1f}s")

if len(rep):
    r = rep.iloc[0]
    print(f"\n### réplica da dura: obj {r['objetivo']:.3f} "
          f"(1ª: {pa.loc[dura, 'objetivo']:.3f}), "
          f"tempo {r['tempo_s']:.1f}s (1ª: {pa.loc[dura, 'tempo_s']:.1f}s), "
          f"gap {r['gap_pct']:.3f}% (1ª: {pa.loc[dura, 'gap_pct']:.3f}%)")

# réplica vs 1ª execução
