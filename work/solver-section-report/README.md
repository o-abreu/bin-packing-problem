---
slug: solver-section-report
status: done
plan_review_attempts: 1
---

# Goal

Escrever a seção **"Solução via solvers"** (§3 do enunciado) do relatório
`report/main.qmd`, em pt-BR, no formato IEEE. Conteúdo: implementação do modelo
agregado R1–R10 nos dois solvers (Gurobi 13.0.3 e HiGHS), as quatro
métricas por instância (status, objetivo, tempo, gap) e a **análise comparativa
solver-vs-solver** com discussão — apoiada no CSV produzido pelo item
`solver-metrics-harness`. Tabelas e plots são gerados por execução inline
(`output: asis`) a partir do CSV; nenhum número digitado à mão
(`AGENTS.md`: "números do relatório vêm do código").

Convenções a respeitar: renderizar com `devenv shell -- render-report` (Quarto
1.6.43 fixado, `pdflatex`); inclusões resolvidas a partir de `main.qmd`; manter
o vocabulário pacote/caminhão (nada do vocabulário legado de frete); citar via
`refs.bib` verificado.

Depende de: `solver-metrics-harness` (o CSV é a fonte de toda tabela).

# Instructions

O plano detalhado — decisões de projeto, protocolo, passos 1–8 e as evidências
de ambiente verificadas — está centralizado em
`work/solver-metrics-harness/README.md` e cobre **os dois itens**: os passos 1–3
implementam e rodam o benchmark; os passos 4–8 são exatamente a escrita desta
seção (`report/sections/solucao-solvers.qmd`, inclusão em `main.qmd`,
referências, render, persistência). Este README não duplica o plano; na
execução, o resultado desta seção é registrado aqui.

Pontos de estilo específicos da escrita:

- Estrutura da seção: Implementação · Protocolo experimental · Resultados ·
  Discussão.
- Voz impessoal para resultados; primeira pessoa do plural só para decisões
  de autoria; números nunca em negrito; máx. um travessão por sentença;
  estrangeirismos em itálico com glossa só na primeira ocorrência.
- A tabela do protocolo declara `threads=8`, sementes (`Seed=0` /
  `random_seed=0`) e **ausência de limite de tempo** (ajuste pedido pelo
  usuário em 2026-11-14) — o mesmo registrado em
  `data/results/protocolo.json`.
- A discussão deve separar o que o CSV mostra (fato) de interpretação
  (inferência nossa), e registrar que execução com `threads > 1` não garante
  determinismo de solver (heurísticas dependentes de tempo).
- Nota de disponibilidade: a licença Gurobi (`gurobi.lic`) é local e
  gitignored; a reprodução completa exige a licença acadêmica.

# Results

A seção §3 foi escrita em `report/sections/solucao-solvers.qmd`, incluída em
`main.qmd` e renderizada em `report/main.pdf` (13 páginas, seção III
"Solução via solvers"). Estrutura entregue: Implementação (R1–R10 como
código, duas escolhas de codificação justificadas), Protocolo experimental
(tabela com 2 processos × 8 threads, sem limite de tempo, sementes, logs por
execução e a especificação da máquina — Ryzen AI 9 365, 20 núcleos, NixOS
26.11, governador `performance`), Resultados (tabela agregada por solver,
figura tempo × |G|, banner de rascunho removido na versão final) e Discussão
(parity de objetivos, tolerâncias de gap, o contraste arquitetural
City_58 — Gurobi 1,5 s vs HiGHS 36 min, 1.496×, "Parallel search off" —,
comparação caminhão a caminhão das soluções 70/111 idênticas, e a ressalva de
determinismo). Todos os números vêm de `data/results/` via spans `{python}`/
chunks `asis`; nenhuma constante digitada; sem referências a chunks ocultos
(regra nova do AGENTS.md aplicada); vocabulário pacote/caminhão; referências
Gurobi/HiGHS verificadas (DOI Crossref) e sincronizadas com o Zotero
`VRWHXMP6`.

# Assessment

## Verdict
accomplished

## Reasoning
O Goal pedia a seção §3 em pt-BR/IEEE com implementação, as quatro métricas e
a análise comparativa solver-vs-solver apoiada no CSV — e o PDF final mostra
a seção completa com todos os números vindos dos artefatos do
`solver-metrics-harness` (verificação por extração de texto do PDF: 2.180,41
s na tabela, 1.496× na discussão, 44 fechadas, 70/111 idênticas). As
convenções foram respeitadas (pt-BR, voz impessoal, números via `ptbr()`,
sem refs a chunks ocultos, vocabulário pacote/caminhão) e o plano detalhado
centralizado no item irmão foi seguido, com desvios documentados lá.

## Recommended next status
done
