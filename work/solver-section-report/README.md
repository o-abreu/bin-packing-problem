---
slug: solver-section-report
status: pending-plan
---

# Goal

Escrever a seção **"Solução via solvers"** (§3 do enunciado) do relatório
`report/main.qmd`, em pt-BR, no formato IEEE. Conteúdo: implementação do modelo
agregado R1–R10 nos dois solvers (Gurobi 13.0.3 e HiGHS 1.15.1), as quatro
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

# Results

# Assessment
