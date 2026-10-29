"""Experimento de simetria entre pacotes (R11) sobre o modelo VSBPP do relatório.

O modelo R1–R10 ainda deixa simetria entre pacotes *idênticos* em (área, peso,
disponibilidade, prazo): trocar dois desses pacotes de caminhão produz outro
vetor viável, de mesmo custo. A restrição candidata é a ordenação lexicográfica

    R11:  sum_j j x_ij  <=  sum_j j x_{i'j}   para todo par consecutivo i < i'
          de pacotes idênticos

que fixa que o pacote de menor índice ocupa um slot de índice menor ou igual.

Duas partes:

1. `check_validity` — enumeração exaustiva em instâncias minúsculas com pacotes
   repetidos: verifica que o ótimo com R9–R11 é igual ao ótimo sem nenhuma
   quebra de simetria (i.e., que R11 não exclui solução ótima alguma).
2. `bench` — MILP (HiGHS) em instâncias com pacotes repetidos: R1–R10 vs.
   R1–R11, comparando objetivo, nós de branch-and-bound e tempo.

Uso (dentro do ambiente do projeto):

    devenv shell -- python scripts/package_symmetry_benchmark.py
"""
import itertools

import numpy as np
import pandas as pd

from symmetry_benchmark import (DELTA_H, SCALE, SPEED_KMH, TRUCKS, _identical_pairs,
                                real_lane, solve, synthetic)


# --------------------------------------------------------------------------- #
# 1. Validação por enumeração exaustiva
# --------------------------------------------------------------------------- #
def brute_force(a, w, av, dl, dist_km, break_symmetry):
    """Ótimo por enumeração de todas as atribuições pacote -> slot (n pequeno)."""
    a = np.asarray(a, float) * SCALE
    w = np.asarray(w, float) * SCALE
    n = len(a)
    t_trip = dist_km / SPEED_KMH
    C = np.array([t[2] * dist_km for t in TRUCKS])
    best = np.inf
    for assign in itertools.product(range(n), repeat=n):  # slot de cada pacote
        loads_a, loads_w, slots = {}, {}, {}
        for i, j in enumerate(assign):
            loads_a[j] = loads_a.get(j, 0.0) + a[i]
            loads_w[j] = loads_w.get(j, 0.0) + w[i]
            slots.setdefault(j, []).append(i)
        total = 0.0
        ok = True
        for j, items in slots.items():
            types = [t for t in range(len(TRUCKS))
                     if loads_a[j] <= TRUCKS[t][0] + 1e-9
                     and loads_w[j] <= TRUCKS[t][1] + 1e-9]
            if not types:                                  # R2-R3
                ok = False
                break
            total += C[min(types, key=lambda t: C[t])]      # função objetivo
            # viabilidade temporal (R6-R8)
            if max(av[i] for i in items) - min(av[i] for i in items) > DELTA_H + 1e-9:
                ok = False
                break
            if max(av[i] for i in items) + t_trip > min(dl[i] for i in items) + 1e-9:
                ok = False
                break
        if not ok or total >= best:
            continue
        if break_symmetry:
            # R9: pacote i não pode ir para slot j > i
            if any(j > i for i, j in enumerate(assign)):
                continue
            # R10: os slots abertos ocupam o prefixo {0..o-1}
            o = len(slots)
            if set(slots) != set(range(o)):
                continue
            # R11: pacotes idênticos em ordem de slot
            for i, ip in _identical_pairs(a, w, av, dl):
                if assign[i] > assign[ip]:
                    break
            else:
                best = total
            continue
        best = total
    return best


def check_validity(trials=30, n=5, seed=0):
    """Compara ótimo irrestrito e ótimo canônico em instâncias minúsculas com repetições."""
    rng = np.random.default_rng(seed)
    pior = 0.0
    for k in range(trials):
        types = rng.integers(2, 4)                       # 2 ou 3 tipos de pacote
        base_a = rng.uniform(1.0, 8.0, types)
        base_w = base_a * rng.uniform(400.0, 1200.0, types)
        base_av = rng.uniform(0.0, 6.0, types)
        base_dl = base_av + 30.0 + rng.uniform(0.0, 20.0, types)
        idx = rng.integers(0, types, n)
        a, w = base_a[idx] / SCALE, base_w[idx] / SCALE
        av, dl, dist = base_av[idx], base_dl[idx], 2400.0
        free = brute_force(a, w, av, dl, dist, break_symmetry=False)
        canon = brute_force(a, w, av, dl, dist, break_symmetry=True)
        pior = max(pior, abs(free - canon))
        if abs(free - canon) > 1e-6:
            print(f"  DIVERGENCIA no caso {k}: irrestrito={free:.2f} canonico={canon:.2f}")
    return pior


# --------------------------------------------------------------------------- #
# 2. Experimento de desempenho
# --------------------------------------------------------------------------- #
def synthetic_with_duplicates(n_types=5, copies=4, seed=0, dist_km=2444.3):
    """Tipos de pacote amostrados das distribuições do dataset, cada um repetido."""
    rng = np.random.default_rng(seed)
    area = rng.uniform(0.64, 9.72, n_types)
    weight = np.minimum(area * rng.uniform(300.0, 1500.0, n_types), 3130.0)
    av = rng.uniform(0, 48, n_types)
    dl = av + dist_km / SPEED_KMH + rng.uniform(2, 60, n_types)
    rep = np.repeat(np.arange(n_types), copies)
    return area[rep] / SCALE, weight[rep] / SCALE, av[rep], dl[rep], dist_km


def real_lane_subset(destination="City_18", n=20, path="data/raw/order_large.csv"):
    """Subamostra de uma rota real, preservando os pacotes repetidos do dataset."""
    a, w, av, dl, dist = real_lane(destination, path=path)
    keep = np.arange(min(n, len(a)))
    return a[keep], w[keep], av[keep], dl[keep], dist


if __name__ == "__main__":
    print("Validação por enumeração exaustiva (instâncias minúsculas com repetições):")
    for trials, n in ((60, 5), (10, 6)):
        gap = check_validity(trials=trials, n=n)
        print(f"  n={n}, {trials} instâncias -> maior desvio entre ótimo irrestrito e ótimo com R9-R11: {gap:.2e}")
    print()

    cases = [
        ("real City_18 (subamostra 20)", real_lane_subset("City_18", 20)),
        ("sintética 5 tipos x 4", synthetic_with_duplicates(5, 4)),
        ("sintética 4 tipos x 5", synthetic_with_duplicates(4, 5, seed=1)),
        ("sintética 20 distintos", synthetic(20)),
    ]
    print(f"{'instância':30s} {'variante':9s} {'objetivo':>11s} {'nós':>7s} {'tempo (s)':>9s}")
    for name, inst in cases:
        for label, kw in (("R1-R10", dict(variant="r9r10")),
                          ("R1-R11", dict(variant="r9r10", pkg_order=True))):
            r = solve(*inst, time_limit=120.0, **kw)
            print(f"{name:30s} {label:9s} {r['obj']:11.2f} {r['nodes']:7d} {r['time']:9.3f}")
        print()
