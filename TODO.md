# TODO — Plano de Trabalho

Plano por fases derivado do enunciado do curso [`Projeto_PM_BCC_2026.md`](./Projeto_PM_BCC_2026.md)
e anotado com as decisões já tomadas neste repositório (ver
[`DATASETS.md`](./DATASETS.md) e o esqueleto [`report.qmd`](./report.qmd)).
Consulte este arquivo antes de começar o trabalho; anote a qual fase uma
mudança pertence nas mensagens de commit.

**Recapitulativo dos entregáveis (do enunciado):** duas implementações (modelo
exato com solver + método alternativo, Python 3), relatório técnico (IEEE, via
`report.qmd`), duas apresentações no semestre e um arquivo único
(.zip/.tar.gz) com código + dados de instâncias + PDF do relatório no
e-disciplinas.

**Avaliação:** NM 3 (modelagem) · NI 4 (2 solvers + 2 métodos alternativos) ·
NR 3 (relatório) · NA 1 (apresentação, individual) · NAAP 1 (avaliação por
pares/própria). Final: $NT = (NM + NI + NR)\cdot\min\{NA, NAAP\}$.

**Pendências de logística do grupo (enunciado §2):** confirmar membros do
grupo (4–5) e registrar o grupo no e-disciplinas antes do prazo.
Responsável: **TODO (grupo)**.

---

## Fase 0 — Escolha do problema & dados ✅ (quase completa)

- [x] Escolher o cenário de aplicação (enunciado §3.1): **empacotamento de
      reservas de frete em rotas logísticas reais** — o caso de uso
      "Alocação de Cargas", estendido à variante de custo variável (VSBPP)
      que o enunciado permite explicitamente ("minimizar o custo/desperdício
      total").
- [x] Pesquisar e commitar datasets reais (`data/raw/`, do Kaggle
      `omarstat2/supply-chain-logistics-data` via o espelho
      `Eden1029/SQL_SupplyChainLogistics`); documentar proveniência e esquema
      em [`DATASETS.md`](./DATASETS.md).
- [x] Verificar fatos do dataset (contagens de linhas, cargas por rota,
      transportadora `V44_3` sem tarifas, brackets cotados em lb, pedidos de
      peso zero) — ver fatos dos dados em [`DATASETS.md`](./DATASETS.md);
      não rederive.
- [x] Verificar semântica de faturamento + níveis de serviço contra o paper
      companheiro do repositório de origem (Dzalbs & Kalganova 2020, Fig. 3):
      tarifa $=\max(R\,w,\ f)$ ($R$ = `rate` por kg sobre a **totalidade** do
      peso do carregamento, `minimum cost` = piso de custo) e níveis de
      serviço DTD/DTP/CRF (CRF = frete contratado pelo cliente, $tc = 0$)
      cobrados nos pedidos como *atributo de requisito*. Consequências:
      instâncias escopadas por **(rota × nível de serviço)**; pedidos CRF
      **excluídos** das instâncias de empacotamento (não reatribuídos a
      reservas tarifadas). Registrado em [`DATASETS.md`](./DATASETS.md);
      não rederive.

## Fase 1 — Bibliografia & introdução ✅ / (entradas do bib pendentes de consolidação)

- [x] Referências centrais de BPP/VSBPP verificadas e no `refs.bib`
      (Karp 1972; Garey & Johnson 1979; Friesen & Langston 1986 — **não**
      "Friesen & Kuo"; Kang 2003; Coffman 1997; citação do dataset).
- [ ] Consolidar os links de fontes do DATASETS.md em entradas citáveis no
      `refs.bib` / prosa do relatório (nota de proveniência ao fim do
      [`DATASETS.md`](./DATASETS.md)). *(referências da "Fase 1" deste
      arquivo)*
- [ ] Escrever a **Introdução** completa (enunciado §4.1): contexto de
      consolidação de frete, relevância industrial, breve revisão da
      literatura com citações ABNT/IEEE. Substituir o placeholder de bloco de
      autores no `report.qmd`.

## Fase 2 — Modelagem & engenharia de instâncias (enunciado §3.1, NM)

- [x] Modelo declarado no `report.qmd`: conjuntos ($I$, $K$, $J$), variáveis
      ($x_{ij}$, $y_{jk}$), objetivo $\min \sum_{j,k} f_k y_{jk}$, restrições
      R1–R5 (atribuição, teto do bracket, casamento de faixa, uma classe por
      reserva, nenhum item em reserva fechada).
- [ ] Validar o modelo contra a formulação base genérica do enunciado
      (recuperável com $f_k \equiv 1$) e documentar o que foi generalizado
      (classes, carga mínima faturada, objetivo de custo).
- [ ] **Engenharia de instâncias:** construir o conjunto experimental completo:
  - [ ] Instâncias escopadas por **(rota × nível de serviço)** — apenas
        pacotes tarifados: `PORT04→PORT09`×DTP (6.184 pedidos),
        `PORT04→PORT09`×DTD (2.143), `PORT09→PORT09`×DTP (34). Pedidos CRF
        (854) são **excluídos** (frete contratado pelo cliente, $tc = 0$);
        `PORT05→PORT09` não tem instância tarifada.
  - [ ] Dentro de um pacote tarifado, manter o recorte por cliente das
        instâncias grandes (ex.: lotes de clientes de `PORT04→PORT09`×DTP)
        com compressão de linhas idêntica.
  - [ ] Baldes de tamanho recalculados nos limites das novas instâncias:
        pequena (≤ ~30 itens) exata sem limite de tempo, média (≤ 60) exata
        com limite de tempo, grandes (milhares) apenas heurística.
  - [ ] Persistir as definições de instância (rota, nível de serviço,
        cliente, seed) para que toda execução seja reproduzível.
- [ ] Finalização do pré-processamento: normalização lb→kg (verificar a
      robustez da detecção de brackets em lb), escopo de classes por
      (rota × svc) antes do filtro de classes dominadas, exclusão de pedidos
      CRF, etapa de pós-atribuição de pedidos de peso zero (só pedidos
      tarifados).

## Fase 3 — Soluções exatas (enunciado §3.1 / §4.3, NI-1)

- [x] PuLP + CBC embutido ponta a ponta em uma instância pequena (no
      `report.qmd`).
- [ ] Segundo solver: resolver as mesmas instâncias com **HiGHS** (`highspy`,
      já instalado) e/ou interface SCIP do PuLP — parear com o requisito do
      enunciado "um comercial + um gratuito":
  - [ ] tentar/negociar licença acadêmica do Gurobi e, se indisponível,
        documentar a substituição junto ao professor;
  - [ ] caso contrário, a comparação é CBC vs HiGHS (ambos acessíveis via
        PuLP).
- [ ] Coleta das quatro métricas de solver exigidas para **toda** instância
      (enunciado §4.3): status da solução (ótima/factível/infactível), valor
      da função objetivo, tempo de processamento, gap de otimalidade %
      (solução inteira vs bound LP).
- [ ] Tabela de análise comparativa solver-vs-solver + discussão.
- [ ] Experimentos de escala em instâncias maiores (HiGHS; limites de tempo +
      regras de aceitação de gap fixadas aqui).

## Fase 4 — Método alternativo (enunciado §3.2 / §4.4, NI-2)

- [x] Heurística FFD de baseline em uma instância pequena (`ffd_baseline` no
      `report.qmd`) com lower bound baseado em peso (LB estilo L2).
- [ ] Estender a heurística da contagem simples de reservas para o **objetivo
      de custo**: FFD/BFD respeitando brackets de peso e o mínimo da faixa,
      em ordem de capacidade crescente.
- [ ] Benchmark heurística vs soluções exatas em todas as instâncias da
      Fase 2, mais comparação puramente heurística nos baldes grandes (gap
      para o bound LP).
- [ ] Escolher ≥ uma meta-heurística para instâncias grandes (Simulated
      Annealing ou Tabu é ideal para movimentos de vizinhança no VSBPP:
      relocate/swap/downgrade de classe). Justificar a escolha com referências
      teóricas adicionadas ao `refs.bib` (DOIs verificados — não invente
      nada).

## Fase 5 — Relatório & análise (enunciado §4, NR)

Um `report.qmd` (IEEE, `pdflatex`, Quarto 1.6.43 travado), escrito em
**pt-BR** (como toda a documentação do repositório), ordem estrita de seções
do enunciado:

- [ ] §1 Introdução — narrativa + citações.
- [ ] §2 Modelagem Matemática — conjuntos/parâmetros/variáveis formais +
      raciocínio por trás de cada restrição (R1–R5).
- [ ] §3 Solução via _Solvers_ — implementação e as quatro métricas
      (status, objetivo, tempo, gap); discussão comparativa entre solvers.
      Esta seção e qualquer saída de análise (plots, tabelas) ficam na forma
      de notebook renderizada por `devenv shell -- render-report`.
- [ ] §4 Método de Solução Alternativo — justificativa, implementação,
      resultados, comparação crítica solver-vs-heurística e discussão de
      aplicabilidade.
- [ ] §5 Conclusão — valor para logística/indústria, trabalhos futuros
      (capacidades variáveis — já é o núcleo do nosso modelo!, restrições
      2D/3D, métodos híbridos), reflexão sobre aprendizados/desafios.
- [ ] Preencher os TODOs de título e bloco de autores.
- [ ] Re-renderizar o `report.qmd` ponta a ponta após cada mudança de Quarto
      ou texlive (pacote LaTeX faltando → adicionar exatamente aquele em
      `texlive.withPackages` no `devenv.nix`, conforme `AGENTS.md`; módulo
      Python faltando → `requirements.txt`).

## Fase 6 — Apresentações (NA)

- [ ] **Primeira apresentação (início do semestre):** problema, modelo,
      resultados atuais.
- [ ] **Apresentação final:** resultados completos, comparações, conclusões.
- [ ] Slides derivados do relatório; sucintos, só rascunhos de resultados
      completos.

## Fase 7 — Empacotamento & submissão

- [ ] Arquivo único (.zip ou .tar.gz) com: código + dados de instâncias +
      modelo + scripts de heurística + PDF do relatório + (opcionalmente) o
      HTML congelado do Quarto para tabelas de análise (mantido fora das
      leituras de arquivo único). Só a última submissão conta.
- [ ] Verificar higiene do repositório commitado conforme `AGENTS.md`: sem
      `output/`, sem `.devenv`, sem `report.quarto_ipynb`, sem `__pycache__`
      na submissão.
- [ ] Remover referências do DATASETS.md/relatório a candidatos de dataset
      abandonados antes da submissão.

## Higiene contínua (todas as fases)

- [ ] Comitar mudanças de ambiente (`devenv.*`, `requirements.txt`) junto com
      a mudança de código que as exige.
- [ ] Manter `data/raw/` rastreado — nunca refazer download nem gitignore.
- [ ] Scripts de renderização / edições do relatório mantêm o vocabulário do
      domínio em vista: pedidos / **reservas (bookings)**, nunca "trucks"
      (rota aérea).
