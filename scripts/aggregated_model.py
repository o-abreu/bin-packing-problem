"""Modelo agregado do VSBPP: contagens por grupo de pacotes idênticos.

Formulação apresentada em `report/sections/metodologia/modelagem-matematica.qmd`
(R1–R10): em vez de um binário por pacote, cada grupo g de pacotes idênticos
(mesma área, peso, disponibilidade e prazo) tem

    z_gj  inteiro em {0, ..., n_g}   quantos pacotes de g vão no caminhão j
    u_gj  binário                   1 se ao menos um pacote de g vai em j

mais y_jt (tipo do caminhão) e tau_j (instante de partida). Quando n_g = 1 para
todo g, a formulação coincide com a versão item a item.

Uso:
    devenv shell -- python scripts/aggregated_model.py City_54 City_48
    devenv shell -- python scripts/aggregated_model.py --all --time-limit 60
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import highspy

sys.path.insert(0, str(Path(__file__).parent))
from symmetry_benchmark import (DELTA_H, SCALE, SPEED_KMH, TRUCKS, real_lane,
                                solve as solve_item)

ORDERS = Path("data/raw/order_large.csv")
DISTANCES = Path("data/raw/distance.csv")


def group_packages(a, w, av, dl):
    """Colapsa pacotes idênticos em grupos; devolve (a, w, av, dl, multiplicidade)."""
    chave = list(zip(a, w, av, dl))
    membros = {}
    for k, t in enumerate(chave):
        membros.setdefault(t, []).append(k)
    grupos = list(membros.keys())
    return (np.array([g[0] for g in grupos]), np.array([g[1] for g in grupos]),
            np.array([g[2] for g in grupos]), np.array([g[3] for g in grupos]),
            np.array([len(v) for v in membros.values()]))


def solve_agg(a, w, av, dl, dist_km, time_limit=120.0, m=None, threads=1, gap=None):
    """Resolve o modelo agregado e devolve status, objetivo, nós, tempo e tamanho."""
    a, w = np.asarray(a, float) * SCALE, np.asarray(w, float) * SCALE
    av, dl = np.asarray(av, float), np.asarray(dl, float)
    a, w, av, dl, cont = group_packages(a, w, av, dl)
    G, T = len(cont), len(TRUCKS)
    n = int(cont.sum())
    m = m or n

    A = np.array([t[0] for t in TRUCKS])
    W = np.array([t[1] for t in TRUCKS])
    C = np.array([t[2] * dist_km for t in TRUCKS])
    t_trip = dist_km / SPEED_KMH
    M = float(dl.max() - av.min() + t_trip + DELTA_H + 1.0)

    iz = lambda g, j: g * m + j                    # z_gj (inteiro)
    iu = lambda g, j: G * m + g * m + j            # u_gj (binário)
    iy = lambda j, t: 2 * G * m + j * T + t        # y_jt (binário)
    it = lambda j: 2 * G * m + m * T + j           # tau_j (contínuo)
    nvar = 2 * G * m + m * T + m

    cost = np.zeros(nvar)
    for j in range(m):
        for t in range(T):
            cost[iy(j, t)] = C[t]

    lo, hi, idx, val = [], [], [], []

    def row(lower, upper, entries):
        lo.append(lower)
        hi.append(upper)
        idx.append([k for k, _ in entries])
        val.append([v for _, v in entries])

    for g in range(G):                                                  # R1
        row(float(cont[g]), float(cont[g]), [(iz(g, j), 1.0) for j in range(m)])
    for j in range(m):
        row(-np.inf, 0.0, [(iz(g, j), a[g]) for g in range(G)]           # R2
            + [(iy(j, t), -A[t]) for t in range(T)])
        row(-np.inf, 0.0, [(iz(g, j), w[g]) for g in range(G)]           # R3
            + [(iy(j, t), -W[t]) for t in range(T)])
        row(-np.inf, 1.0, [(iy(j, t), 1.0) for t in range(T)])           # R4
    for g in range(G):
        for j in range(m):
            row(-np.inf, 0.0, [(iz(g, j), 1.0)]                          # R5
                + [(iy(j, t), -float(cont[g])) for t in range(T)])
            row(-np.inf, 0.0, [(iu(g, j), 1.0), (iz(g, j), -1.0)])       # R6
            row(-np.inf, 0.0, [(iz(g, j), 1.0), (iu(g, j), -float(cont[g]))])
            row(-np.inf, M - av[g], [(iu(g, j), M), (it(j), -1.0)])      # R7
            row(-np.inf, av[g] + DELTA_H + M,
                [(it(j), 1.0), (iu(g, j), M)])                           # R8
            row(-np.inf, dl[g] - t_trip + M,
                [(it(j), 1.0), (iu(g, j), M)])                           # R9
    for j in range(m - 1):                                              # R10
        row(0.0, np.inf, [(iy(j, t), 1.0) for t in range(T)]
            + [(iy(j + 1, t), -1.0) for t in range(T)])

    lower = np.zeros(nvar)
    upper = np.concatenate([np.repeat(cont, m).astype(float),
                            np.ones(G * m + m * T), np.full(m, np.inf)])

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", time_limit)
    h.setOptionValue("threads", threads)
    if gap is not None:
        h.setOptionValue("mip_rel_gap", gap)
    h.addVars(nvar, lower, upper)
    h.changeColsCost(nvar, np.arange(nvar, dtype=np.int32), cost)
    inteiras = np.concatenate([np.arange(2 * G * m),
                               np.arange(2 * G * m, 2 * G * m + m * T)])
    h.changeColsIntegrality(len(inteiras), inteiras.astype(np.int32),
                            np.full(len(inteiras),
                                    int(highspy.HighsVarType.kInteger),
                                    dtype=np.uint8))
    starts = np.cumsum([0] + [len(r) for r in idx]).astype(np.int32)
    h.addRows(len(lo), np.array(lo, float), np.array(hi, float),
              sum(len(r) for r in idx), starts,
              np.array([k for r in idx for k in r], dtype=np.int32),
              np.array([v for r in val for v in r], float))
    h.changeObjectiveSense(highspy.ObjSense.kMinimize)

    t0 = time.perf_counter()
    h.run()
    dt = time.perf_counter() - t0
    info = h.getInfo()
    return dict(status=h.modelStatusToString(h.getModelStatus()),
                obj=info.objective_function_value, nodes=info.mip_node_count,
                time=dt, grupos=G, n=n, m=m, vars=nvar,
                linhas=h.getNumRow(), gap=info.mip_gap)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rotas", nargs="*", help="destinos (ex.: City_54)")
    ap.add_argument("--all", action="store_true", help="todas as rotas de order_large.csv")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--compare", action="store_true",
                    help="também resolve o modelo item a item e compara o objetivo")
    args = ap.parse_args(argv)

    import pandas as pd
    if args.all:
        rotas = sorted(pd.read_csv(ORDERS)["Destination"].unique())
    else:
        rotas = args.rotas or ["City_54", "City_48"]

    print(f"{'rota':9s} {'n':>4s} {'G':>3s} {'m':>4s} {'vars':>6s} {'linhas':>7s} "
          f"{'obj':>12s} {'nos':>7s} {'tempo':>7s}  status")
    for rota in rotas:
        inst = real_lane(rota, path=str(ORDERS))
        r = solve_agg(*inst, time_limit=args.time_limit)
        marca = "" if r["status"] == "Optimal" else f"  [{r['status']}]"
        print(f"{rota:9s} {r['n']:4d} {r['grupos']:3d} {r['m']:4d} {r['vars']:6d} "
              f"{r['linhas']:7d} {r['obj']:12.2f} {r['nodes']:7d} {r['time']:6.1f}s{marca}")
        if args.compare:
            it = solve_item(*inst, variant="r9r10", pkg_order=True, threads=1,
                            time_limit=args.time_limit)
            print(f"{'':9s} item a item: obj={it['obj']:.2f} nos={it['nodes']} "
                  f"t={it['time']:.1f}s [{it['status']}]")


if __name__ == "__main__":
    main()
