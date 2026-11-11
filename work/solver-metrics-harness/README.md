---
slug: solver-metrics-harness
status: pending-plan
---

# Goal

Coletar as **quatro métricas de solver** exigidas pelo enunciado (§4.3) para
**toda** instância, em execução reproduzível:

1. status da solução (ótima / factível / infactível),
2. valor da função objetivo,
3. tempo de processamento,
4. gap de otimalidade % (solução inteira vs bound LP).

Escopo: as **61 rotas** de `data/raw/order_large.csv` (61 MILPs independentes do
modelo agregado R1–R10), resolvidas nos **dois solvers** — Gurobi 13.0.3 (licença
acadêmica em `gurobi.lic`) e HiGHS 1.15.1 (`highspy`) — satisfazendo o pareamento
"um comercial + um gratuito" do enunciado. Saída: um CSV por solver (ou um único
CSV com coluna de solver) em `data/`, com parâmetros de execução (limite de
tempo, threads, seed) persistidos junto, para que toda execução seja
reproduzível. Este item é o pré-requisito direto da seção "Solução via solvers"
do relatório.

Contexto de desempenho já medido (não rederivar): `City_48` e `City_54` não
fecham em 120 s com a formulação item a item; com o agregado R1–R10 caem para
5,8 s e 7,1 s. O limite de tempo do harness deve ser fixado aqui e registrado.

# Instructions

# Results

# Assessment
