# Goal

Resolver o problema de empacotamento com caixas de tamanho e custo variáveis
(**VSBPP**) aplicado a uma frota de caminhões real, como trabalho de
**SME 0110 — Programação Matemática** (ICMC-USP, 2º semestre de 2026). O
enunciado parte do roteamento de veículos (VRP); impondo uma única parada por
viagem, cada rota degenera num VSBPP: os itens são pacotes e as caixas são
caminhões de quatro tipos, cada um com área de piso $A_t$, capacidade de peso
$W_t$ e custo $c_t$ por quilômetro. Como o custo de um caminhão na rota é
$C_t = c_t\,d$, o objetivo é o **custo fixo da frota**, não o número de
veículos.

A instância é **bidimensional** (um caminhão só é viável se respeitar área **e**
peso) e o modelo oficial é o **agregado R1–R10** de
`report/sections/metodologia/modelagem-matematica/index.qmd`: a instância é
definida sobre **grupos de pacotes idênticos** (mesma área, peso,
disponibilidade e prazo), cada um com multiplicidade $n_g$, e a decisão é
_quantos_ pacotes de cada grupo vão em cada caminhão ($z_{gj}$), mais o tipo do
caminhão ($y_{jt}$) e o instante de partida ($\tau_j$). Essa agregação é o que
torna as instâncias resolvíveis: 4.635 pacotes viram 239 grupos e nenhuma
instância passa de 11 grupos.

O entregável é `report/main.qmd` — artigo IEEE em duas colunas, em pt-BR,
renderizado com `devenv shell -- render-report` — mais duas implementações
Python (modelo exato com solver + método alternativo) e as apresentações do
semestre. O estado do relatório: Introdução ✅ · Modelagem Matemática ✅ ·
Solução via _solvers_ ⬜ · Método de Solução Alternativo ⬜ · Conclusão ⬜.

# Background

- **Dados:** Kaggle
  [`mexwell/large-scale-route-optimization`](https://www.kaggle.com/datasets/mexwell/large-scale-route-optimization)
  (MIT), espelho do acelerador
  [`dstoolkit-route-optimization`](https://github.com/microsoft/dstoolkit-route-optimization)
  da Microsoft — _benchmark_ "inspirado num cenário real" de um cliente de
  manufatura, não dados brutos de empresa. `data/raw/order_large.csv`: 4.635
  pacotes, 365 pedidos, 61 rotas (⇒ 61 MILPs independentes). `Area`/`Weight`
  escalados por $10^4$. Proveniência, licença e disponibilidade: seção III do
  relatório (`report/sections/disponibilidade.qmd`). Os arquivos brutos são
  versionados e nunca re-baixados.
- **O que já foi medido** (registro histórico: o log de experimentos em
  `notes/` foi removido em nov/2026 e permanece recuperável no histórico do
  git — não refazer números à toa): formulação agregada vs item a item
  (derruba a cauda: `City_54` 120 s → 7,1 s), quebra de simetria R9–R10 (o
  ganho vem do **par**; R11, do modelo item a item, ficou histórico — o
  agregado não tem índice de item), paralelismo entre rotas (3,2× em 20
  núcleos — o gargalo é a formulação, não os núcleos), potencial de
  pré-processamento (teto de slots por **custo**, não por contagem de FFD; 44
  de 111 instâncias fechadas por inspeção).
- **Solvers disponíveis (verificado em nov/2026):** HiGHS 1.15.1 (`highspy`) e
  Gurobi 13.0.3 com licença acadêmica em `gurobi.lic` (ignorado pelo git,
  apontado por `GRB_LICENSE_FILE` no `devenv.nix`);
  `pulp.listSolvers(onlyAvailable=True)` → `['GUROBI', 'GUROBI_CMD', 'HiGHS']`.
- **Ambiente:** declarativo via devenv + direnv; nada de instalação imperativa
  (deps Python → `requirements.txt`, ferramentas → `devenv.nix`). Quarto 1.6.43
  fixado por `nixpkgs-quarto`; `pdf-engine` = `pdflatex`. Detalhes em
  `AGENTS.md`.
- **Vocabulário do domínio** (parte do modelo): itens são **pacotes**, caixas
  são **caminhões**; o vocabulário de frete (pedidos, reservas, tarifas)
  pertence ao estudo de caso legado e não deve vazar para o modelo novo.
- **Logística do grupo** (responsabilidade dos integrantes, não do agente):
  registrar o grupo no e-disciplinas; duas apresentações no semestre.

# Completed Work

_(nenhum item registrado ainda — o pré-projeto (modelagem e pré-processamento)
foi concluído antes deste arquivo existir; o registro está no histórico do git
e no `report/main.qmd`)_

# Pending Work

- [solver-metrics-harness](work/solver-metrics-harness/README.md) (status: pending-plan) — coletar as quatro métricas de solver (status, objetivo, tempo, gap) por instância em CSV, para as 61 rotas, nos dois solvers
- [solver-section-report](work/solver-section-report/README.md) (status: pending-plan) — escrever a seção "Solução via solvers" (§3) do relatório com tabela comparativa e discussão
- [alternative-method](work/alternative-method/README.md) (status: pending-plan) — heurística construtiva ciente de custo + meta-heurística para instâncias grandes, benchmark vs exato, alimenta o §4 do relatório
- [conclusion-section](work/conclusion-section/README.md) (status: pending-plan) — escrever a §5 Conclusão e fechar o relatório
