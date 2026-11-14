# Este código supõe que você tenha uma licença do gurobi configurada em sua
# máquina

from datetime import datetime
import json
from typing import Any, Hashable
import gurobipy as gp
import pandas as pd
from numpy import floor
from pathlib import Path
import time
import multiprocessing as mp
import tqdm

# ===== Inicialização dos dados =====

data_path = Path(__file__).parent.parent.parent / "data"

groups_path = data_path / "pre-processed" / "groups.csv"
instances_path = data_path / "pre-processed" / "instances.csv"
trucks_path = data_path / "raw" / "trucks.csv"
order_large_path = data_path / "raw" / "order_large.csv"

log_path = (
    Path(__file__).parent
    / f"gurobi_log_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv"
)
sol_path = (
    Path(__file__).parent
    / f"gurobi_sol_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jsonl"
)

groups_csv = pd.read_csv(groups_path)
instances_csv = pd.read_csv(instances_path, index_col="instance")
trucks_csv = pd.read_csv(trucks_path, comment="#")

# groups_by_instance = groups_csv.groupby("instance")
groups_by_instance = groups_csv.groupby("instance", sort=False)

sorted_groups = sorted(
    groups_by_instance,
    key=lambda kv: kv[1]["count"].sum(),
    reverse=True,
)

num_groups: int = len(groups_csv)
num_instances: int = len(instances_csv)
num_trucks: int = len(trucks_csv)

_ENV: gp.Env | None = None
"Ambiente do Gurobi (um por processo)"

EPS: float = 1e-9
"Tolerância para comparações de ponto flutuante"

# Apesar de haver vários problemas paralelos, queremos poucos workers, uma vez
# pela assimetria da carga de trabalho por instância,
NWORKERS: int = 4
"Número de processos paralelos"

TIME_LIMIT = 600

# ===== Instanciação dos parâmetros =====

A = trucks_csv["area_capacity_m2"].astype(float)
"A[t]: Capacidade de área do caminhão do tipo t"

W = trucks_csv["weight_capacity_kg"].astype(float)
"W[t]: Capacidade de peso do caminhão do tipo t"

c = trucks_csv["cost_per_km"].astype(float)
"c[t]: Custo por kilômetro do caminhão do tipo t"


v: float = 40
"Velocidade dos caminhões"

Δ = 4
"Janela de consilidação"


def calc_UB() -> float:
    return Δ


# ===== Solução ótima por rota =====


def solve_routing(
    t: tuple[Hashable, pd.DataFrame],
) -> tuple[str, float, list[dict[str, Any]]]:
    global _ENV

    inst_name = str(t[0])
    groups = t[1].reset_index(drop=True)
    "DataFrame com os grupos da instância"

    inst = instances_csv.loc[inst_name]

    assert isinstance(inst, pd.Series), f"instância inválida: {inst_name}"

    dist: float = float(inst["dist_km"])
    "Distância da instância"

    num_groups = len(groups)

    ng = groups["count"].astype(int)
    "ng[g]: Multiplicidade do grupo g"

    a: pd.Series = groups["area_m2"].astype(float)
    "a[g]: Area de um pacote do grupo g (da instância)"

    w: pd.Series = groups["weight_kg"].astype(float)
    "w[g]: Peso de um pacote do grupo g (da instância)"

    av: pd.Series = groups["avail_h"].astype(float)
    "av[g]: Disponibilidade dos pacotes do grupo g (da instância)"

    dl: pd.Series = groups["deadline_h"].astype(float)
    "dl[g]: Prazo dos pacotes do grupo g (da instância)"

    C: pd.Series = c * dist
    "C[t]: Custo fixo de um caminhão do tipo t"

    t_viagem: float = dist / v
    "Tempo de viagem da rota"

    M: float = max(dl) - min(av) + t_viagem + Δ
    "Constante de desativação"

    m: int = int(inst["m_slots"])
    "_Slots_ de caminhões considerados"

    G = range(num_groups)
    T = range(num_trucks)
    J = range(m)

    # NOTA: Poderia usar o corte sobre os caminhões, mas como o número de
    # caminhões é pequeno, não vale a pena

    opt_value: float = 0

    with gp.Model(env=_ENV, name=f"bpp-empacotamento-{inst_name}") as model:
        model.Params.TimeLimit = TIME_LIMIT
        model.Params.Cutoff = float(inst["ub_cost"]) * 1.1

        z = model.addVars(  # pyright: ignore[reportCallIssue]
            num_groups,
            m,
            ub={(g, j): ng[g] for g in G for j in J},  # pyright: ignore[reportArgumentType]
            vtype=gp.GRB.INTEGER,
            name="z",
        )
        "z[g,j]: # de pacotes do grupo g que viajam no caminhão j"

        u = model.addVars(
            num_groups,
            m,
            vtype=gp.GRB.BINARY,
            name="u",
        )
        "u[g,j]: 1 se pelo menos um pacote do grupo g viaja no caminhão j; 0 c.c."

        y = model.addVars(m, num_trucks, vtype=gp.GRB.BINARY, name="y")
        "y[j,t]: 1 se o caminhão j é do tipo t; 0 c.c."

        τ = model.addVars(m, vtype=gp.GRB.CONTINUOUS, name="tau")
        "τ[j]: Instante de partida do caminhão j"

        model.setObjective(
            gp.quicksum(C[t] * y[j, t] for t in T for j in J), sense=gp.GRB.MINIMIZE
        )

        # Restrição de atribuição completa
        model.addConstrs(
            (gp.quicksum(z[g, j] for j in J) == ng[g] for g in G), name="R1"
        )

        # Restrição de capacidade de área
        model.addConstrs(
            (
                gp.quicksum(a[g] * z[g, j] for g in G)
                <= gp.quicksum(A[t] * y[j, t] for t in T)
                for j in J
            ),
            name="R2",
        )

        # Restrição de capacidade de peso
        model.addConstrs(
            (
                gp.quicksum(w[g] * z[g, j] for g in G)
                <= gp.quicksum(W[t] * y[j, t] for t in T)
                for j in J
            ),
            name="R3",
        )

        # Restrição de tipo do caminhão
        model.addConstrs((gp.quicksum(y[j, t] for t in T) <= 1 for j in J), name="R4")

        # Restrição de Vínculo grupo-caminhão
        model.addConstrs(
            (z[g, j] <= ng[g] * gp.quicksum(y[j, t] for t in T) for g in G for j in J),
            name="R5",
        )

        # Restrição de ocupação de grupo
        model.addConstrs((u[g, j] <= z[g, j] for g in G for j in J), name="R6.1")

        model.addConstrs(
            (z[g, j] <= ng[g] * u[g, j] for g in G for j in J), name="R6.2"
        )

        # Partida após disponibilidade
        model.addConstrs(
            (τ[j] >= av[g] - M * (1 - u[g, j]) for g in G for j in J), name="R7"
        )

        # Janela de consideração
        model.addConstrs(
            (τ[j] <= av[g] + Δ + M * (1 - u[g, j]) for g in G for j in J), name="R8"
        )

        # Chegada dentro do prazo
        model.addConstrs(
            (τ[j] <= dl[g] - t_viagem + M * (1 - u[g, j]) for g in G for j in J),
            name="R9",
        )

        # Quebra de simetria
        model.addConstrs(
            (
                gp.quicksum(y[j, t] for t in T) >= gp.quicksum(y[j + 1, t] for t in T)
                for j in range(m - 1)
            ),
            name="R10",
        )

        # 1% de tolerância -- acelerar teste
        # model.params.MIPGap = 0.01

        model.optimize()

        if model.Status != gp.GRB.OPTIMAL:
            print("Alguma coisa aconteceu, status é", model.Status)
            raise ValueError(f"Instância {inst_name} não foi resolvida com sucesso")

        obj = model.getObjective()
        opt_value = obj.getValue()
        solution_values = [
            {
                "instance": inst_name,
                "variable": variable.VarName,
                "value": variable.X,
            }
            for variable in model.getVars()
            if not variable.VarName.startswith("u")
        ]

    return inst_name, opt_value, solution_values


def _initialize_env() -> None:
    global _ENV

    env = gp.Env(empty=True, params={"OutputFlag": 0})
    env.start()
    _ENV = env


def main():
    time_start: float = time.perf_counter()
    valor_total: float = 0.0

    # 1 Env por processo
    with mp.Pool(NWORKERS, initializer=_initialize_env) as pool:
        results = list(
            tqdm.tqdm(
                pool.imap_unordered(solve_routing, sorted_groups),
                total=num_instances,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                desc="Resolvendo instâncias",
            )
        )
        valor_total = sum(result[1] for result in results)

    with sol_path.open("w", encoding="utf-8") as solutions_file:
        for inst_name, objective, variable_values in results:
            solution = {
                "instance": inst_name,
                "objective_usd": objective,
                "variables": {
                    variable_value["variable"]: variable_value["value"]
                    for variable_value in variable_values
                },
            }
            solutions_file.write(json.dumps(solution) + "\n")

    time_end: float = time.perf_counter()
    time_elapsed: float = time_end - time_start

    pd.DataFrame(
        [
            {
                "status": "OPTIMAL",
                "valor_total_usd": valor_total,
                "time_elapsed_s": time_elapsed,
                "workers": NWORKERS,
            }
        ]
    ).to_csv(log_path, index=False)

    print(f"Tempo total (incluindo inicialização): {time_elapsed}s")

    print(f"valor_total = US$ {valor_total}")


if __name__ == "__main__":
    main()
