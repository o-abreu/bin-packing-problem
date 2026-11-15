---
slug: solver-metrics-harness
status: done
plan_review_attempts: 1
---

# Goal

Coletar as **quatro métricas de solver** exigidas pelo enunciado (§4.3) para
**toda** instância, em execução reproduzível:

1. status da solução (ótima / factível / infactível),
2. valor da função objetivo,
3. tempo de processamento,
4. gap de otimalidade % (solução inteira vs bound LP).

**Escopo corrigido (2026-11-14):** a versão anterior deste README falava em
"61 rotas ⇒ 61 MILPs", que ficou obsoleta com a decomposição (rota × dia) já
refletida em `data/pre-processed/`: são **111 instâncias**, das quais **44
fechadas por inspeção** (`meta.json`). O benchmark roda as 111 nos **dois
solvers** — Gurobi 13.0.3 (licença acadêmica em `gurobi.lic`) e HiGHS
(`highspy`) — satisfazendo o pareamento "um comercial + um gratuito" do
enunciado. As 44 fechadas também são resolvidas: servem de validação
independente (objetivo esperado = `closed_cost`).

Saída: `data/results/solver_metrics.csv` (uma linha por instância × solver)
com as quatro métricas e os parâmetros de execução persistidos em
`data/results/protocolo.json`, para que toda execução seja reproduzível. Este
item é o pré-requisito direto de `work/solver-section-report/` (seção §3 do
relatório).

Contexto de desempenho já medido (não rederivar): `City_48` e `City_54` não
fecham em 120 s com a formulação item a item; com o agregado R1–R10 caem para
5,8 s e 7,1 s (Gurobi).

# Instructions

## Decisões de projeto (a aprovar pelo usuário)

1. **Escopo = todas as 111 instâncias de `data/pre-processed/instances.csv`**
   nos dois solvers, incluindo as 44 `closed=True` (resolvidas como validação;
   custo trivial, < 0,1 s cada).
2. **Protocolo único para os dois solvers** (ajustado em 2026-11-14 pelo
   usuário): **sem limite de tempo** — ambos resolvem até o fim (ótimo ou
   outro encerramento padrão do solver); `threads=8` (idêntico nos dois,
   para comparação justa), sementes fixadas (Gurobi `Seed=0`, HiGHS
   `random_seed=0`), `msg=False`, sem _warm start_, gap padrão do solver.
   O pior caso sem limite é aberto — mitigado por (i) o desempenho já medido
   do agregado (as piores instâncias fecham em < 8 s no Gurobi) e (ii) o
   progresso incremental do passo 2, observável em arquivo durante a
   execução; se o HiGHS estagnar, o protocolo volta ao usuário.
3. **Cache de execução:** o benchmark roda por chunk `{python}` no render
   (kernel Jupyter do Quarto), mas grava o CSV ao fim do loop; os chunks
   seguintes leem o CSV se ele existir e bater com o protocolo registrado
   (mesmo nº de instâncias e mesmos parâmetros). Primeira renderização
   estimada em minutos (limitada por 60 s/solve); renderizações seguintes,
   instantâneas. Para forçar reexecução: apagar `data/results/solver_metrics.csv`.
   O CSV é commitado — é a fonte de todas as tabelas da seção.
4. **Implementação mora no relatório** (decisão do usuário): as funções de
   construção e resolução do modelo ficam em chunks `{python}` de
   `report/sections/solucao-solvers.qmd`; nenhum script externo.

## Passos

> **Protocolo final (2026-11-14, após três decisões do usuário e duas
> descobertas empíricas):** sem limite de tempo (decisão do usuário,
> reafirmada diante da instância dura), **2 processos paralelos × 8 threads
> por execução** (20 núcleos), sementes fixadas, log de cada solve em
> `data/results/logs/` (não versionado; `.gitignore` atualizado), specs da
> máquina na tabela de protocolo. Histórico: o protocolo original era
> 60 s/8 threads sequencial; o usuário retirou o limite; a primeira
> re-execução paralela (20 processos × 1 thread) revelou que
> `City_58_2022-04-06` (198 pacotes, 11 grupos, 16 slots) não fecha nem no
> Gurobi em 1 thread (> 90 s, _gap_ travado em 2,81%) mas fecha em 1,49 s
> com 8 threads — o paralelismo de heurísticas do Gurobi é decisivo nela —
> e o HiGHS declarou "_Parallel search off_" (busca MIP efetivamente
> sequencial, ~103% de CPU mesmo com `threads=8`). O usuário optou por
> manter o "sem limite" mesmo assim; o pool foi reduzido para 2 × 8
> threads e as tarefas HiGHS ordenadas do menor para o maior porte, para a
> instância dura rodar por último.

1. **Chunk de setup e modelo** em `report/sections/solucao-solvers.qmd`
   (novo arquivo; `label: solvers-setup`, `include: false`): carrega
   `data/pre-processed/instances.csv` e `groups.csv` (a frota já está no
   `trucks` do setup de `main.qmd`); define:
   - `montar_modelo(inst, grupos, Delta=4)` — o agregado R1–R10 exatamente
     como declarado em `restricoes.qmd`: $z_{gj}$ inteiro (ub global
     $\max_g n_g$, valido pois R1 já implica $z_{gj} \le n_g$),
     $u_{gj}, y_{jt}$ binários, $\tau_j$ contínuo ≥ 0; $M = \max_g dl_g -
     \min_g av_g$ da instância; $t_{\text{viagem}} = d/v$ com $v = 40$ km/h
     (uniforme nos 4 tipos — verificado em `data/raw/trucks.csv`); $C_t =
     c_t\,d$.
   - `resolver(modelo, solver)` — wrapper de `m.solve(...)` que devolve um
     dict com status, objetivo, `best_bound`, gap %, `time`, `cpu_time`,
     `num_variables`, `num_constraints` do `LpSolveStats`.
   - API PuLP 4.2 (núcleo Rust, sem `LpVariable` construtor público — ver
     Evidências): `m.add_variable(name, lowBound=, upBound=, cat=)` e
     `m.add_variable_dicts(name, (iteráveis, ...), cat=)`.
2. **Chunk de benchmark** (`label: solvers-benchmark`): checa o cache; se
   ausente, loop 111 × 2 com
   `pulp.GUROBI(msg=False, timeLimit=60, threads=8, Seed=0)` e
   `pulp.HiGHS(msg=False, timeLimit=60, threads=8, random_seed=0)`;
   acumula em memória e grava atomicamente `data/results/solver_metrics.csv`
   (colunas: `solver, instance, status, objective, best_bound, gap_pct,
   time_s, cpu_time_s, n_vars, n_constrs`; quando `has_solution=False` —
   p. ex. encerramento sem incumbente — `objective`/`best_bound`/
   `gap_pct` ficam vazios e `status` registra o motivo). **Progresso
   incremental:** cada linha resolvida é acrescida a
   `data/results/.partial.csv` (arquivo temporário, observável com `tail`
   durante a execução longa) e renomeado atomicamente para o CSV definitivo
   ao fim do loop. +
   `data/results/protocolo.json` (parâmetros do protocolo, versões de
   python/pulp/highspy/gurobipy, carimbo de data/hora e **sha256 de
   `instances.csv` e `groups.csv`**). O cache hit exige paridade completa:
   nº de instâncias, parâmetros **e** os hashes dos dois arquivos de
   entrada — qualquer edição silenciosa nos dados invalida o CSV.
3. **Chunk de validação** (`label: solvers-validacao`):
   (a) as 44 fechadas: `objective == closed_cost` (tol. 1e-6);
   (b) Gurobi vs HiGHS: objetivos iguais (tol. relativa 1e-4) onde ambos
   `Optimal` — linhas sem incumbente ficam fora das comparações de objetivo,
   mas entram na contagem do agregado;
   (c) `objective ≤ ub_cost` (o teto de custo do pré-processamento);
   (d) nenhum status `Infeasible`.
   Qualquer falha **interrompe o render com erro explícito** (nada de
   engolir divergência).
4. **Tabelas e figuras** (chunks `output: asis` ou matplotlib): tabela do
   protocolo; tabela agregada por solver (n ótimos / no limite de tempo,
   tempo média/mediana/p90/máximo, gap máximo); figura de tempo por solver
   contra o porte da instância (escala log); tabela das piores instâncias.
   Todo número via `ptbr()` a partir do CSV — nenhum número digitado à mão
   (`AGENTS.md`).
5. **Prosa** (pt-BR, estilo do `AGENTS.md`): seção `# Solução via solvers`
   com subseções Implementação / Protocolo experimental / Resultados /
   Discussão; incluir em `main.qmd` após `metodologia/index.qmd`. Vocabulário
   pacote/caminhão; nada do legado de frete; voz impessoal, número nunca em
   negrito.
6. **Referências**: conferir se `refs.bib` tem entradas para Gurobi e HiGHS;
   se faltarem, localizar DOI verificável (skill `paper-lookup`) e
   sincronizar com a coleção Zotero `VRWHXMP6`.
7. **Render e verificação**: `devenv shell -- render-report`; conferir
   `report/main.pdf` (tabelas, figuras, paginação) e checar cada afirmação
   numérica da seção contra o CSV.
8. **Persistência**: commits **separados** na branch
   `feat/solver-benchmark`: (i) `data/results/*` + `work/`, (ii)
   `report/sections/solucao-solvers.qmd` + `main.qmd` + `refs.bib` +
   `report/main.pdf`. Reportar os hashes. Atualizar também
   `work/solver-section-report/README.md` (ver plano espelho lá) e os
   statuses no `project.md`.

# Evidências verificadas (2026-11-14, shell do devenv)

- `pulp.listSolvers(onlyAvailable=True)` → `['GUROBI', 'GUROBI_CMD',
  'HiGHS']`; python 3.12.15; pulp 4.2.0; gurobipy 13.0.3 (licença acadêmica
  válida até 2027-10-29, carregada com sucesso); 20 núcleos.
- API PuLP 4.2 (núcleo Rust): `LpVariable` não tem construtor público;
  variáveis só via `LpProblem.add_variable()` / `add_variable_dicts/dict/
  matrix`. `m.solve(solver)` devolve `LpSolveStats` com campos `solver,
  status, has_solution, time, cpu_time, objective, best_bound, num_variables,
  num_constraints, is_mip, solver_options, logs`; `LpSolveStatus.Optimal ==
  1`, `TimeLimit == -4`.
- Toy solve executado nos dois: HiGHS Optimal obj 10.0 (0,0015 s); Gurobi
  Optimal obj 10.0 (0,0035 s, gap 0,0000%).
- Assinaturas: `pulp.GUROBI(mip, msg, timeLimit, gapRel, gapAbs, warmStart,
  logPath, env, ..., **solverParams)`; `pulp.HiGHS(mip, msg, callbackTuple,
  gapAbs, gapRel, threads, timeLimit, logPath, warmStart, **solverParams)`.
- `data/pre-processed/`: `meta.json` → 111 instâncias, 239 grupos, 4.635
  pacotes, 44 fechadas; `instances.csv` → 111 linhas com `n_packages,
  n_groups, area_total, weight_total, dist_km, m_slots, ub_cost, lb_area,
  types_allowed, closed, closed_cost`; `groups.csv` → 239 linhas com
  `area_m2, weight_kg, avail_h, deadline_h, count` por instância;
  `speed_kmh = 40` para os quatro tipos.

# Review Notes

_(2026-11-14, após o loop de revisão)_ Aprovado: os seis critérios passam —
passos nomeiam ferramenta/arquivo/artefato específicos, a API PuLP 4.2 e o
licenciamento Gurobi foram verificados por execução nesta sessão, as
dependências (CSV → validação → tabelas → prosa → render → commits) seguem
ordem e o escopo cobre o Goal. As duas lacunas do pass 1 (hash de cache,
linhas sem incumbente) foram incorporadas nos passos 2–3.

# Results

## Summary

O benchmark foi executado por completo: **222 execuções (111 instâncias × 2
solvers), todas com status ótimo**, em execução paralela (2 processos × 8
threads) e sem limite de tempo, em 2026-11-14. Gurobi fecha o lote em 4,4 s
totais; o HiGHS leva ~36 min, quase todo o tempo na instância
`City_58_2022-04-06` (2.180 s contra 1,46 s do Gurobi — razão de 1.496×, a
busca MIP do HiGHS ser sequencial). As quatro métricas (status, objetivo,
tempo, gap) estão em `data/results/solver_metrics.csv`, com a estrutura de
solução dos dois solvers em `solucao_caminhoes.csv`/`solucao_grupos.csv` e o
protocolo completo (parâmetros, versões, specs da máquina, hashes de entrada)
em `protocolo.json`. Validação (a)–(e) toda verde: fechadas por inspeção
reproduzem `closed_cost` com diferença máxima 0,0; paridade de objetivos
2·10⁻¹⁴; nenhuma execução acima de `ub_cost` nem infactível; soluções dos
dois solvers idênticas caminhão a caminhão em 70/111 instâncias, mesma frota
com atribuição distinta em 35, frota de composição diferente a custo igual em
6. A seção §3 do relatório (`report/sections/solucao-solvers.qmd`) está
escrita e renderizada em `report/main.pdf`.

## Artifacts

- `data/results/solver_metrics.csv` — 222 linhas (instância × solver) com as
  quatro métricas
- `data/results/solucao_caminhoes.csv` — 310 caminhões abertos: tipo, partida
  (τ), ocupação de área/peso, custo, manifestas de grupos (coluna `solver`)
- `data/results/solucao_grupos.csv` — 497 atribuições classe → caminhão
- `data/results/protocolo.json` — parâmetros, versões, specs da máquina
  (governador `performance`), hashes SHA-256 das entradas
- `data/results/logs/` — 222 logs de execução (não versionados)
- `report/sections/solucao-solvers.qmd` + `report/main.pdf` — seção §3

## Step-by-step

1–3 (implementação, benchmark, validação) executados conforme o plano; quatro
desvios/evoluções documentados: (i) protocolo alterado por decisão do usuário
de 60 s → sem limite de tempo (reafirmado duas vezes); (ii) a primeira
re-execução paralela (20 processos × 1 thread) revelou que `City_58` não
fecha em 1 thread em nenhum dos solvers (Gurobi > 90 s com gap travado em
2,81%; HiGHS idem) mas o Gurobi fecha em 1,46 s com 8 threads — o protocolo
foi reduzido a 2 processos × 8 threads e as tarefas HiGHS ordenadas da mais
leve para a mais pesada; (iii) o usuário pediu extração de solução integrada
ao benchmark para os dois solvers, com comparação estrutural (check (e));
(iv) modo rascunho via `BENCHMARK_RASCUNHO=1` para renderizar o PDF com
números parciais marcados durante a execução longa. Observação registrada: o
log do HiGHS exibe um aviso interno numérico (`HighsSearch::selectBranching
Candidate Error fracval`) durante a busca na instância dura, sem abortar a
execução, que terminou ótima; a referência HiGHS (Huangfu & Hall 2018, DOI
10.1007/s12532-017-0130-5) e o manual Gurobi foram adicionados a `refs.bib` e
sincronizados com a coleção Zotero `VRWHXMP6`. O `main.pdf` final é
renderizado do cache completo (222/222).

## Artifacts

_(a lista de artefatos está no bloco de marcadores da seção Results, acima.)_

# Assessment

## Verdict
accomplished

## Reasoning
O Goal pedia as quatro métricas de solver para toda instância, de forma
reproduzível, nos dois solvers — e o disco mostra exatamente isso:
`data/results/solver_metrics.csv` com 222 linhas (111 instâncias × 2 solvers,
todas `Optimal`), `protocolo.json` com parâmetros/versões/specs da máquina e
hashes SHA-256 das entradas, e 222 logs em `data/results/logs/`. A
reprodutibilidade está mecanizada (cache por hash + parâmetros; sementes
fixadas). Verificação por execução nesta sessão: City_58 Gurobi 1,46 s /
HiGHS 2.180,4 s, paridade de objetivos 2·10⁻¹⁴, fechadas reproduzem
`closed_cost` com diferença 0,0 — tudo consistente com o CSV. Os desvios do
plano (sem limite de tempo, 2×8 threads, extração de solução integrada, modo
rascunho) estão documentados em Results com a cadeia de decisões do usuário.
Nota menor: os artefatos vivem em `data/results/`, não em
`work/<slug>/data/` — desvio deliberado, previsto no plano (o CSV é a fonte
das tabelas do relatório e mora junto dos demais dados do projeto).

## Recommended next status
done
