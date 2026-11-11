---
slug: alternative-method
status: pending-plan
---

# Goal

Implementar e avaliar o **método de solução alternativo** (§3.2/§4.4 do
enunciado, componente NI-2 da nota): uma alternativa não-exata ao MILP
agregado R1–R10, em Python 3, comparável às soluções exatas.

Duas camadas:

1. **Heurística construtiva ciente de custo** para o objetivo de custo fixo da
   frota: FFD/BFD em ordem de capacidade crescente, respeitando as duas
   capacidades (área **e** peso) e a janela de disponibilidade/prazo. Ponto de
   partida já existente: `ffd_baseline` no relatório (contagem simples + LB
   estilo L2), a estender de contagem de caminhões para custo.
2. **Meta-heurística para instâncias grandes** (Simulated Annealing ou Tabu —
   movimentos de vizinhança relocate/swap/downgrade de tipo são os candidatos
   naturais no VSBPP), justificada com referências teóricas com DOIs
   verificados em `refs.bib` — nunca inventar referência.

Avaliação: benchmark heurística vs soluções exatas nas instâncias que fecham
(CSV do item `solver-metrics-harness`), e gap contra o bound LP nas grandes;
resultados escritos na seção "Método de Solução Alternativo" (§4) do relatório,
com discussão de aplicabilidade.

Ressalva já medida (não rederivar; registro no histórico do git): usar o número
de caminhões da FFD como teto é **inválido** para objetivo de custo — o teto
válido é o de custo, $m \le \lfloor \mathrm{UB}/(c_{\min}d) \rfloor$.

Depende de: `solver-metrics-harness` (para o benchmark vs exato); pode começar
pela heurística construtiva em paralelo.

# Instructions

# Results

# Assessment
