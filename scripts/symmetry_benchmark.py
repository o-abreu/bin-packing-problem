"""Experimento de simetria do modelo VSBPP de `report/sections/modelagem-matematica.qmd`.

Compara três variantes do MILP sobre as mesmas instâncias:

  nosym   -- R1..R8 (nenhuma quebra de simetria)
  r9      -- R1..R9 (ordenação dos slots abertos pelo menor índice de pacote)
  r9r10   -- R1..R10 (R9 + caminhões abertos ocupam um prefixo de J)

Métricas: valor ótimo, nós de branch-and-bound e tempo de prova do HiGHS.
O ótimo é idêntico nas três variantes; o que muda é o esforço de prova.

Uso (dentro do ambiente do projeto):

    devenv shell -- python scripts/symmetry_benchmark.py
"""
import time

import highspy
import numpy as np
import pandas as pd

# Frota transcrita de data/raw/trucks.csv: (área m2, peso kg, custo por km)
TRUCKS = [
    (40.25, 27000.0, 10.0),
    (30.25, 24000.0, 9.0),
    (20.93, 14000.0, 6.5),
    (16.56, 8000.0, 5.5),
]
SPEED_KMH = 40.0
DELTA_H = 4.0
SCALE = 1.0 / 10000.0  # Area e Weight do dataset são escalados por 1e4


def _identical_pairs(a, w, av, dl):
    """Pares consecutivos (i, i') de pacotes idênticos em área, peso, disponibilidade e prazo."""
    groups = {}
    for i in range(len(a)):
        groups.setdefault((a[i], w[i], av[i], dl[i]), []).append(i)
    pairs = []
    for idx in groups.values():
        idx.sort()
        pairs.extend(zip(idx[:-1], idx[1:]))
    return pairs


def solve(a, w, av, dl, dist_km, variant, m=None, time_limit=120.0, pkg_order=False):
    """Monta e resolve o MILP; devolve status, objetivo, nós e tempo.

    `pkg_order=True` acrescenta R11 (ordenação lexicográfica entre pacotes
    idênticos), que só faz sentido se houver pacotes repetidos.
    """
    n, T = len(a), len(TRUCKS)
    m = m or n
    a = np.asarray(a, float) * SCALE
    w = np.asarray(w, float) * SCALE
    A = np.array([t[0] for t in TRUCKS])
    W = np.array([t[1] for t in TRUCKS])
    C = np.array([t[2] * dist_km for t in TRUCKS])
    t_trip = dist_km / SPEED_KMH
    M = float(dl.max() - av.min() + t_trip + DELTA_H + 1.0)

    ix = lambda i, j: i * m + j          # x_ij
    iy = lambda j, t: n * m + j * T + t  # y_jt
    it = lambda j: n * m + m * T + j     # tau_j
    nvar = n * m + m * T + m

    cost = np.zeros(nvar)
    for j in range(m):
        for t in range(T):
            cost[iy(j, t)] = C[t]
    lb = np.zeros(nvar)
    ub = np.concatenate([np.ones(n * m + m * T), np.full(m, np.inf)])
    if variant != "nosym":                # R9: x_ij = 0 para j > i
        for i in range(n):
            for j in range(i + 1, m):
                ub[ix(i, j)] = 0.0

    lo, hi, idx, val = [], [], [], []

    def row(lower, upper, entries):
        lo.append(lower)
        hi.append(upper)
        idx.append([k for k, _ in entries])
        val.append([v for _, v in entries])

    for i in range(n):                                                  # R1
        row(1.0, 1.0, [(ix(i, j), 1.0) for j in range(m)])
    for j in range(m):
        row(-np.inf, 0.0, [(ix(i, j), a[i]) for i in range(n)]          # R2
            + [(iy(j, t), -A[t]) for t in range(T)])
        row(-np.inf, 0.0, [(ix(i, j), w[i]) for i in range(n)]          # R3
            + [(iy(j, t), -W[t]) for t in range(T)])
        row(-np.inf, 1.0, [(iy(j, t), 1.0) for t in range(T)])          # R4
    for i in range(n):
        for j in range(m):
            row(-np.inf, 0.0, [(ix(i, j), 1.0)]                         # R5
                + [(iy(j, t), -1.0) for t in range(T)])
            row(-np.inf, M - av[i], [(ix(i, j), M), (it(j), -1.0)])     # R6
            row(-np.inf, av[i] + DELTA_H + M,
                [(it(j), 1.0), (ix(i, j), M)])                          # R7
            row(-np.inf, dl[i] - t_trip + M,
                [(it(j), 1.0), (ix(i, j), M)])                          # R8
    if variant == "r9r10":
        for j in range(m - 1):                                          # R10
            row(0.0, np.inf, [(iy(j, t), 1.0) for t in range(T)]
                + [(iy(j + 1, t), -1.0) for t in range(T)])
    if pkg_order:                                                       # R11
        for (i, ip) in _identical_pairs(a, w, av, dl):
            row(-np.inf, 0.0, [(ix(i, j), float(j + 1)) for j in range(m)]
                + [(ix(ip, j), -float(j + 1)) for j in range(m)])

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", time_limit)
    h.addVars(nvar, lb, ub)
    h.changeColsCost(nvar, np.arange(nvar, dtype=np.int32), cost)
    h.changeColsIntegrality(
        n * m + m * T,
        np.arange(n * m + m * T, dtype=np.int32),
        np.full(n * m + m * T, int(highspy.HighsVarType.kInteger), dtype=np.uint8),
    )
    starts = np.cumsum([0] + [len(r) for r in idx]).astype(np.int32)
    h.addRows(len(lo), np.array(lo, float), np.array(hi, float),
              sum(len(r) for r in idx), starts,
              np.array([k for r in idx for k in r], dtype=np.int32),
              np.array([v for r in val for v in r], float))
    h.changeObjectiveSense(highspy.ObjSense.kMinimize)

    t0 = time.perf_counter()
    h.run()
    elapsed = time.perf_counter() - t0
    info = h.getInfo()
    return dict(
        status=h.modelStatusToString(h.getModelStatus()),
        obj=info.objective_function_value,
        nodes=info.mip_node_count,
        time=elapsed,
    )


def real_lane(destination="City_54", path="data/raw/order_small.csv"):
    """Instância real de um CSV de pedidos para uma rota (horas a partir do menor Available_Time)."""
    orders = pd.read_csv(path)
    lane = orders[orders.Destination == destination]
    origin = pd.to_datetime(orders.Available_Time).min()
    av = ((pd.to_datetime(lane.Available_Time) - origin).dt.total_seconds() / 3600).values
    dl = ((pd.to_datetime(lane.Deadline) - origin).dt.total_seconds() / 3600).values
    dist = pd.read_csv("data/raw/distance.csv")
    d = dist[(dist.Source == "City_61") & (dist.Destination == destination)].iloc[0]
    return lane.Area.values, lane.Weight.values, av, dl, d["Distance(M)"] / 1000.0


def synthetic(n, seed=0, dist_km=2444.3):
    """Instância sintética com pacotes distintos, amostrados das distribuições do dataset."""
    rng = np.random.default_rng(seed)
    area = rng.uniform(0.64, 9.72, n)                 # m2 observados em order_large.csv
    weight = np.minimum(area * rng.uniform(300.0, 1500.0, n), 3130.0)
    av = rng.uniform(0, 48, n)
    dl = av + dist_km / SPEED_KMH + rng.uniform(2, 60, n)
    return area / SCALE, weight / SCALE, av, dl, dist_km


if __name__ == "__main__":
    cases = [
        ("real City_54 (5 pacotes)", real_lane("City_54")),
        ("sintética n=12", synthetic(12)),
        ("sintética n=20", synthetic(20)),
    ]
    print(f"{'instância':26s} {'variante':6s} {'objetivo':>12s} {'nós':>8s} {'tempo (s)':>9s}")
    for name, inst in cases:
        for variant in ("nosym", "r9", "r9r10"):
            r = solve(*inst, variant=variant)
            print(f"{name:26s} {variant:6s} {r['obj']:12.2f} {r['nodes']:8d} {r['time']:9.3f}")
        print()
