---
slug: highs-parallel-run
status: done
---

# Goal

Resposta à pergunta aberta da revisão do §Solução via solvers: o HiGHS 1.15.1
declarou "_Parallel search off_" em 66 dos 111 logs do benchmark (§3), porque a
busca MIP paralela é controlada pela opção `parallel` (padrão `"choose"`), que o
protocolo nunca definiu — `threads=8` só dimensiona o pool. Este item executou um
**terceiro braço do benchmark**: as mesmas 111 instâncias, mesmo modelo R1–R10,
HiGHS com `parallel="on"` e `threads=8`, para medir o efeito real da busca
paralela. Resultado incorporado ao relatório (Tabela X e Fig. 12 em
`report/sections/solucao-solvers.qmd`).

# Protocolo (idêntico ao do relatório, salvo o indicado)

- Modelo: agregado R1–R10, montado pela mesma lógica de
  `report/sections/solucao-solvers.qmd` (função copiada verbatim no script
  `run_highs_parallel.py`).
- Solver: `pulp.HiGHS(msg=True, threads=8, random_seed=0, logPath=...,
  parallel="on", log_to_console=0)` (PuLP 4.2 encaminha kwargs extras a
  `setOptionValue` — verificado no fonte de `createAndConfigureSolver`).
- Sem limite de tempo, sem warm start, gap padrão.
- **Diferença declarada:** execução **sequencial** (1 processo), enquanto o
  benchmark do relatório usou 2 processos × 8 threads. Justificativa: no
  protocolo original cada solve HiGHS consumiu ~103% de CPU (1 worker), então
  a concorrência entre processos não afetou o tempo por solve; sequencial, o
  horário por instância fica limpo mesmo com a busca paralela consumindo até
  14 workers. A ordem é a mesma do relatório: instâncias do menor para o maior
  porte (`m_slots`, `n_packages`), a mais dura por último.
- Logs por solve em `data/results/logs/HiGHSPAR__<instância>.log`
  (diretório gitignored); o log confirma `Thread count 8 (of 20 threads).
  Using 14 max workers. Parallel search on` em todos os solves que entraram
  na busca (ex.: `HiGHSPAR__City_3_2022-04-06.log`).

# Results

## Desfecho: aborto manual na instância dura

- **108/111 instâncias completadas** (todas `Optimal`, objetivos idênticos ao
  braço sequencial; 44 fechadas por inspeção incluídas). As 3 pendentes são as
  maiores na ordem de execução: `City_37_2022-04-06`, `City_58_2022-04-05`,
  `City_58_2022-04-06`.
- **`City_58_2022-04-06` não fecha com a busca paralela.** Abortada
  manualmente (SIGTERM) após **8.914,3 s** no relógio do solver (wall ≈ 8.925 s;
  nascimento do log 15:24:56 → kill 17:53:41), **4,1×** o braço sequencial
  (2.180,4 s), com _gap_ dual estático em **2,81%**, **48,9%** da árvore
  explorada e o limitante dual parado em 151.763,558 nos últimos **5.709 s
  (1 h 35 min)**, ainda que ~7,1 milhões de nós tenham sido processados no
  período. Evidência: últimas linhas de
  `data/results/logs/HiGHSPAR__City_58_2022-04-06.log` (não versionado) e
  registro versionado em `data/results/aborto_highs_parallel.json`.
- A réplica planejada da instância dura não chegou a rodar.

## Comparação nas 64 instâncias não-triviais completadas

(`compare.py`, sobre `solver_metrics_highs_parallel_parcial.csv`):

| métrica | sequencial | parallel=on |
|---|---:|---:|
| ótimos | 64/64 | 64/64 |
| tempo total (s) | 50,3 | 60,9 |
| mediano (s) | 0,02 | 0,02 |
| máximo (s) | 24,03 (City_58_2022-04-07) | 31,06 (City_19_2022-04-05) |
| _gap_ máx (%) | 8,3 × 10⁻³ | 8,7 × 10⁻³ |

- Paralelo mais rápido em **49/64**; razão sequencial/paralelo de mediana
  **1,04**; pior caso do paralelo: `City_19_2022-04-05` (15,0 → 31,1 s).
- `parallel="on"` **não** salvou a instância dura — ao contrário, destruiu o
  progresso do limitante: conclusão do experimento é que a diferença de tempo
  do benchmark original reflete a configuração padrão do HiGHS 1.15 (e a
  arquitetura dos dois solvers), e a busca paralela do HiGHS 1.15, ainda
  recente, não é vantajosa nestas instâncias.
- Reportado no relatório: parágrafo de descoberta/protocolo, Tabela X
  (`tab-solvers-paralelo`) e Fig. 12 (`fig-solvers-paralelo`) em
  `report/sections/solucao-solvers.qmd`; os parágrafos que atribuíam a busca
  em 1 thread "por construção" foram corrigidos.

# Dados versionados

- `data/results/solver_metrics_highs_parallel_parcial.csv` (108 linhas)
- `data/results/protocolo_highs_parallel_parcial.json` (parâmetros, hashes,
  versões, máquina)
- `data/results/aborto_highs_parallel.json` (registro do aborto)

