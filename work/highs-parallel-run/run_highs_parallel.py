#!/usr/bin/env python3
"""Terceiro braço do benchmark de solvers: HiGHS 1.15.1 com parallel="on".

Modelo e protocolo idênticos aos do benchmark do relatório
(report/sections/solucao-solvers.qmd), com três diferenças declaradas:
  1. HiGHS recebe a opção `parallel="on"` (busca B&B paralela); o protocolo
     original não definia `parallel` (padrão "choose" -> 1 worker).
  2. Execução sequencial (1 processo), não 2 processos × 8 threads: no
     protocolo original cada solve HiGHS usou ~1 worker (~103% CPU), então a
     concorrência entre processos não afetava o tempo por solve; sequencial,
     o horário por instância fica limpo com a busca paralela ativa.
  3. A instância mais dura (City_58_2022-04-06) é resolvida duas vezes para
     medir a variância da busca paralela (possivelmente não determinística).

Saídas:
  data/results/solver_metrics_highs_parallel.csv
  data/results/protocolo_highs_parallel.json
  data/results/logs/HiGHSPAR__<instance>.log   (e __rep para a réplica)
"""
from pathlib import Path

import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import time

import pandas as pd
import pulp

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "data" / "results"
LOGS = RESULT / "logs"

insts = pd.read_csv(ROOT / "data/pre-processed/instances.csv")
grupos_todas = pd.read_csv(ROOT / "data/pre-processed/groups.csv")
trucks = pd.read_csv(ROOT / "data/raw/trucks.csv", comment="#")

tipos = [str(t) for t in sorted(trucks["truck_type"], reverse=True)]
frota_t = trucks.set_index(trucks["truck_type"].astype(str))
VEL = float(trucks["speed_kmh"].iloc[0])  # 40 km/h, uniforme nos quatro tipos
Delta = 4.0


def montar_modelo(inst, grupos):
    """MILP agregado R1–R10 para uma instância (rota × dia).

    Cópia verbatim de report/sections/solucao-solvers.qmd (chunk
    solvers-setup), exceto pela proveniência de `frota_t`/`tipos`/`VEL`.
    """
    G = list(grupos["group"])
    J = list(range(int(inst["m_slots"])))
    d = float(inst["dist_km"])
    t_v = d / VEL
    C = {t: float(frota_t.loc[t, "cost_per_km"]) * d for t in tipos}
    av = dict(zip(grupos["group"], grupos["avail_h"]))
    dl = dict(zip(grupos["group"], grupos["deadline_h"]))
    n_g = dict(zip(grupos["group"], grupos["count"].astype(int)))
    a_g = dict(zip(grupos["group"], grupos["area_m2"]))
    w_g = dict(zip(grupos["group"], grupos["weight_kg"]))

    m = pulp.LpProblem("vsbpp", pulp.LpMinimize)
    z = m.add_variable_dicts("z", (G, J), lowBound=0,
                             upBound=max(n_g.values()), cat="Integer")
    u = m.add_variable_dicts("u", (G, J), cat="Binary")
    y = m.add_variable_dicts("y", (tipos, J), cat="Binary")
    tau = m.add_variable_dicts("tau", (J,), lowBound=0)

    M = max(dl.values()) - min(av.values()) + Delta + t_v

    m += pulp.lpSum(C[t] * y[t][j] for t in tipos for j in J), "custo_frota"

    for g in G:
        m += (pulp.lpSum(z[g][j] for j in J) == n_g[g], f"R1[{g}]")
    for j in J:
        m += (pulp.lpSum(a_g[g] * z[g][j] for g in G)
              <= pulp.lpSum(float(frota_t.loc[t, "area_capacity_m2"]) * y[t][j]
                            for t in tipos), f"R2[{j}]")
        m += (pulp.lpSum(w_g[g] * z[g][j] for g in G)
              <= pulp.lpSum(float(frota_t.loc[t, "weight_capacity_kg"]) * y[t][j]
                            for t in tipos), f"R3[{j}]")
        m += (pulp.lpSum(y[t][j] for t in tipos) <= 1, f"R4[{j}]")
    for g in G:
        for j in J:
            m += (z[g][j] <= n_g[g] * pulp.lpSum(y[t][j] for t in tipos),
                  f"R5[{g},{j}]")
            m += (u[g][j] <= z[g][j], f"R6a[{g},{j}]")
            m += (z[g][j] <= n_g[g] * u[g][j], f"R6b[{g},{j}]")
            m += (tau[j] >= av[g] - M * (1 - u[g][j]), f"R7[{g},{j}]")
            m += (tau[j] <= av[g] + Delta + M * (1 - u[g][j]), f"R8[{g},{j}]")
            m += (tau[j] <= dl[g] - t_v + M * (1 - u[g][j]), f"R9[{g},{j}]")
    for j in J[:-1]:
        m += (pulp.lpSum(y[t][j] for t in tipos)
              >= pulp.lpSum(y[t][j + 1] for t in tipos), f"R10[{j}]")
    return m


def highs_par(log=None):
    """HiGHS com busca MIP paralela: a única diferença de protocolo."""
    return pulp.HiGHS(msg=True, threads=8, random_seed=0, logPath=log,
                      parallel="on", log_to_console=0)


def resolver(modelo, log):
    st = modelo.solve(highs_par(log))
    objetivo = st.objective if st.has_solution else None
    bound = st.best_bound if st.has_solution else None
    gap = (100 * (objetivo - bound) / abs(objetivo)
           if objetivo is not None and bound is not None else None)
    return {
        "status": st.status.name,
        "tem_solucao": st.has_solution,
        "objetivo": objetivo,
        "bound": bound,
        "gap_pct": gap,
        "tempo_s": st.time,
        "cpu_s": st.cpu_time,
    }


def sha256_arq(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()[:16]


def specs_maquina():
    cpuinfo = Path("/proc/cpuinfo").read_text()
    modelo_cpu = next(l.split(":", 1)[1].strip() for l in cpuinfo.splitlines()
                      if l.startswith("model name"))
    mem_kib = int(next(l.split(":", 1)[1].replace("kB", "").strip()
                       for l in Path("/proc/meminfo").read_text().splitlines()
                       if l.startswith("MemTotal")))
    so = next(l.split("=", 1)[1].strip().strip('"')
              for l in Path("/etc/os-release").read_text().splitlines()
              if l.startswith("PRETTY_NAME"))
    return {"cpu": modelo_cpu, "nucleos": os.cpu_count(),
            "mem_gib": round(mem_kib / 2**20), "so": so}


def resolver_inst(inst, grupos, sufixo_log=""):
    modelo = montar_modelo(inst, grupos)
    log = str(LOGS / f"HiGHSPAR__{inst['instance']}{sufixo_log}.log")
    t0 = time.perf_counter()
    registro = resolver(modelo, log)
    registro["wall_s"] = time.perf_counter() - t0
    registro.update({
        "solver": "HiGHS-parallel",
        "instance": inst["instance"],
        "n_groups": int(inst["n_groups"]),
        "m_slots": int(inst["m_slots"]),
        "closed": bool(inst["closed"]),
        "closed_cost": (None if pd.isna(inst["closed_cost"])
                        else float(inst["closed_cost"])),
    })
    return registro


def principal():
    RESULT.mkdir(exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    csv_final = RESULT / "solver_metrics_highs_parallel.csv"
    csv_parcial = RESULT / ".partial_highs_parallel.csv"
    json_protocolo = RESULT / "protocolo_highs_parallel.json"

    protocolo = {
        "parametros": {"processos": 1, "threads": 8, "semente": 0,
                       "limite_tempo_s": None, "warm_start": False,
                       "gap": "padrao", "Delta_h": Delta,
                       "parallel": "on"},
        "versoes": {"python": platform.python_version(),
                    "pulp": pulp.__version__,
                    "highspy": importlib.metadata.version("highspy")},
        "maquina": specs_maquina(),
        "hashes": {"instances.csv": sha256_arq(ROOT / "data/pre-processed/instances.csv"),
                   "groups.csv": sha256_arq(ROOT / "data/pre-processed/groups.csv")},
        "instancias": len(insts),
        "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    json_protocolo.write_text(json.dumps(protocolo, indent=2, ensure_ascii=False))
    print("Protocolo:", json.dumps(protocolo, ensure_ascii=False), flush=True)

    # Mesma ordem do relatório: menor porte primeiro, a dura por último.
    ordenadas = sorted(insts.itertuples(),
                       key=lambda i: (i.m_slots, i.n_packages))
    linhas = []
    for k, inst in enumerate(ordenadas, 1):
        grupos = grupos_todas[grupos_todas["instance"] == inst.instance]
        reg = resolver_inst(inst._asdict(), grupos)
        linhas.append(reg)
        print(f"[{k}/{len(ordenadas)}] {reg['instance']}: "
              f"{reg['status']} obj={reg['objetivo']} "
              f"tempo={reg['tempo_s']:.2f}s cpu={reg['cpu_s']:.2f}s", flush=True)
        tmp = csv_parcial.with_suffix(".tmp")
        pd.DataFrame(linhas).to_csv(tmp, index=False)
        tmp.replace(csv_parcial)

    # Réplica da instância dura (variância da busca paralela).
    dura = next(i for i in ordenadas if i.instance == "City_58_2022-04-06")
    grupos = grupos_todas[grupos_todas["instance"] == dura.instance]
    rep = resolver_inst(dura._asdict(), grupos, sufixo_log="__rep")
    linhas.append(rep)
    print(f"[replica] {rep['instance']}: {rep['status']} "
          f"obj={rep['objetivo']} tempo={rep['tempo_s']:.2f}s", flush=True)

    pd.DataFrame(linhas).to_csv(csv_final, index=False)
    csv_parcial.unlink(missing_ok=True)
    print(f"OK -> {csv_final}", flush=True)


if __name__ == "__main__":
    principal()
