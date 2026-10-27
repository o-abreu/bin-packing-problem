# Pesquisa de Datasets — Candidatos Reais por Caso de Uso

Documento companheiro do [`TODO.md`](./TODO.md) (Fase 2) e do enunciado
[`Projeto_PM_BCC_2026.md`](./Projeto_PM_BCC_2026.md). Cada dataset candidato é
mapeado na **formulação genérica de BPP** do enunciado: itens $I$ com tamanhos
$w_i$, caixas $J$ com capacidade $C$, decisão $x_{ij}$, $y_j$, objetivo
$\min \sum_j y_j$.

Os cinco casos de uso nomeados no enunciado foram usados como palavras-chave:
**(1)** carga/veículos · **(2)** consolidação de VMs · **(3)** backup/arquivamento ·
**(4)** armários de laboratório · **(5)** diagramação de provas.

**Legenda de adequação:**

🟢 forte (mapeamento 1:1, dados reais)

🟡 moderado (precisa de pré-processamento/derivação)

🔴 fraco (apenas ilustrativo).

---

## 0. Referência sintética — _Pick and Place Binning Dataset_ (default atual)

|             |                                                                                                                                                           |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fonte**   | [Kaggle `panavraaj/pick-and-place-binning-dataset`](https://www.kaggle.com/datasets/panavraaj/pick-and-place-binning-dataset)                             |
| **Tipo**    | Sintético, licença MIT, usabilidade 7.5, ~188 MB (JSON)                                                                                                   |
| **Conteúdo** | Instâncias de binning em 6 tamanhos (3/5/10/40/100/200 objetos): `objects` (tamanhos), `bins` (capacidades), baselines pré-computados `greedy_sequence` + `greedy_cost` |

**Relação com o caso de uso (carga/alocação):** substituto genérico. Objetos =
pacotes ($w_i$), caixas = capacidade de caminhão/contêiner ($C$). As baselines
`greedy_cost` embutidas tornam o dataset valioso para a **seção de método
alternativo** do relatório (toda instância tem uma referência greedy
documentada a ser batida, e torna os ótimos do MILP diretamente
comparáveis). Ressalva: **nenhuma distribuição real de demanda/peso** —
gerador sintético, então o relatório deve ser honesto em dizer que as
instâncias refletem um gerador sintético, não dados de campo. Qualquer um dos
datasets reais abaixo pode substituí-lo como a "afirmação de dado real", ou
eles podem ser combinados (benchmark de baseline greedy + instâncias reais
como validação).

---

## 1. Alocação de Cargas em Veículos (truck/container loading)

### 🟢 Supply Chain Logistics Optimization Dataset — _benchmark real de pesquisa_

- **Fonte:**
  [Kaggle `omarstat2/supply-chain-logistics-data`](https://www.kaggle.com/datasets/omarstat2/supply-chain-logistics-data)
  (originária de pesquisa na Brunel University London)
- **Relaciona:** `OrderList` — **9.215 pedidos reais de clientes** com pesos,
  unidades, datas de envio e portos; `FreightRates` codifica **brackets de
  peso** (min/max por faixa tarifária); `WhCapacities` — 19 limites de
  throughput diário.
- **Mapeamento BPP:** itens $i$ = linhas de pedido, $w_i$ = `Weight` da
  `OrderList`; caixas = caminhões/contêineres, $C$ = limite do bracket de peso
  escolhido; objetivo = mínimo de caminhões por balde de data de envio.
  Opcionalmente estender para minimização de custo (min Σcᵢⱼxᵢⱼ) se pedirem
  metas de tarifa — ponte natural para a variante "minimizar custo/desperdício"
  que o enunciado permite explicitamente.
- **Semântica de faturamento do `FreightRates` — verificada contra o repositório
  de origem (2026-10).** Fonte autoritativa: o paper companheiro do dataset
  (Dzalbs & Kalganova 2020, *Computers & Industrial Engineering* 147, 106610,
  DOI 10.1016/j.cie.2020.106610 — citado pelo registro figshare
  `10.17633/rd.brunel.7558679.v2`; cópia green OA em arXiv:2001.08102), cujo
  pseudo código da Figura 3 define o custo de transporte $tc_{kpj}$ de um
  carregamento de peso $w$ numa linha como:
  1. serviço `CRF` → $tc = 0$ (o cliente contrata o próprio frete).
  2. modo `GROUND` → parcela proporcional da tarifa de carga completa $R$
     cobrada pela transportadora (rate $R$ = "the freight rate (dollars per
     kilogram) for given weight gap based on total weight for the line").
  3. Caso contrário $tc = \max(R \cdot w,\; M)$, onde $M$ = `minimum cost` e
     $R$ = `rate` ($/kg) da **faixa de peso contendo $w$** (faixa selecionada
     pelo peso total da linha; o paper: "The freight rate is determined based
     on total weight on any given line and the corresponding weight band in
     the freight rate table").

  → **O `rate` por kg é cobrado sobre a *totalidade* do peso do carregamento;
  o `minimum cost` é um piso de custo, não um limiar de peso faturável.** Não
  há cobrança sobre o excesso acima de `minm_wgh_qty`.
  → Implicação para o modelo: o custo verdadeiro por reserva é o
  piecewise-linear $\max(R_k\, w,\, f_k)$; o objetivo do MILP $\sum f_k
  y_{jk}$ mantém apenas o termo de taxa fixa (o rate por kg é o "refinamento"
  documentado no relatório) e subestima custos nas rotas onde $R_k w > f_k$.
- **Níveis de serviço (`svc_cd`) — verificados contra o paper companheiro
  (texto do §4, 2026-10).** O paper define níveis de serviço exigidos pelo
  cliente: **DTD (Door to Door)**, **DTP (Door to Port)**, **CRF (Customer
  Referred Freight)**, e afirma que o cliente decide o nível de serviço
  requerido — de modo que `svc_cd` em um pedido é um *atributo de
  requisito*, não uma decisão de otimização. Uma reserva (carrier ×
  `svc_cd` × bracket) só pode atender pedidos que exijam o **mesmo** nível de
  serviço (carregamentos door-to-door e door-to-port não podem ser
  consolidados — obrigações de entrega distintas).
- **Decomposição em instâncias (fiel ao paper, decidido 2026-10).** Os
  empacotamentos são escopados **por rota *e* nível de serviço**, e pedidos
  CRF são *excluídos* das instâncias de empacotamento: a regra 1 da Figura 3
  define $tc = 0$ para CRF (o cliente contrata o próprio frete; a empresa só
  incorre em custo de armazém), logo não há reserva de transportadora a
  fazer — isso substitui a suposição antiga de que o solver "reatribuiria" os
  pedidos CRF/`V44_3` sem tarifa. Instâncias tarifadas resultantes:
  | Instância (rota × svc) | Pedidos tarifados | Linhas em FreightRates |
  |---|---|---|
  | `PORT04→PORT09` × DTP | 6.184 | 10 |
  | `PORT04→PORT09` × DTD | 2.143 | 221 |
  | `PORT09→PORT09` × DTP | 34 | ~10 |
  | (CRF: 714 + 1 + 139 = 854 pedidos) | excluídos | 0 linhas |
  O único pedido de `PORT05→PORT09` é CRF, então não há instância tarifada.

### 🟢 Large-Scale Route Optimization (Microsoft solution accelerator)

- **Fonte:**
  [Kaggle `mexwell/large-scale-route-optimization`](https://www.kaggle.com/datasets/mexwell/large-scale-route-optimization)
- **Relaciona:** alocação item→caminhão; itens carregam `Area (m²)` e
  `Weight (kg)`; 3 tipos de caminhão com capacidade nas duas dimensões (16.5
  m: 10.000 kg / 16.1×2.5 m², 12.5 m: 5.000 kg / 12.1×2.5 m², 9.6 m: 2.000 kg
  / 9.1×2.3 m²).
- **Mapeamento BPP:** formalmente uma variante VRP/VRPPD; **ignorando
  roteirização/prazos/deadlines**, o _núcleo puro de bin packing_ é exatamente
  o modelo do enunciado (itens com wᵢ, caixas heterogêneas com capacidade D).
  Caixas de capacidade heterogênea ($C_j$ variando por tipo de caminhão) são
  uma generalização fácil da fórmula de C constante do enunciado — um detalhe
  que vale sinalizar na narrativa "o que generalizamos" do relatório.

### 🟢 Cross-Border E-commerce Logistics Data (China)

- **Fonte:**
  [Kaggle `zara2099/china-cross-border-logistics-data`](https://www.kaggle.com/datasets/zara2099/china-cross-border-logistics-data)
- **Relaciona:** 7.000 registros de envio com `package_weight_kg` e
  `package_volume_cbm` por envio.
- **Mapeamento BPP:** uso de carga — conjunto de itens instantâneo ($w_i$ =
  peso/volume do pacote). O mais fraco dos três causalmente porque faltam
  especificações de capacidade de contêiner (C precisa ser importado de
  padrão da indústria, p.ex. contêiner 40' de 28.8 m³) — aceitável e citável
  via enunciado.

---

## 2. Consolidação de Máquinas Virtuais (Cloud Computing)

### 🟢 Azure Traces for Packing 2020 — _feito sob medida para pesquisa em packing_

- **Fonte:**
  [`Azure/AzurePublicDataset` → `AzureTracesForPacking2020`](https://github.com/Azure/AzurePublicDataset/blob/master/AzureTracesForPacking2020.md)
  (hospedado como GitHub releases) · citar o paper de OSDI'20 "Protean: VM
  Allocation Service at Scale".
- **Relaciona:** requisições de **VM empacotadas com prioridade**, tempo de
  vida e **recursos normalizados alocados** por tipo de VM — lançado pela
  Azure _especificamente para avaliar algoritmos de packing/bin-packing_. É o
  padrão atual: avaliações recentes de packing/consolidação (p.ex. PUVAR
  2023; workloads vector-BP 2025–26) todas fazem benchmark sobre ele.
- **Mapeamento BPP:** itens = requisições de VM ($w_i$ = demanda normalizada
  CPU+RAM), caixas = hosts físicos ($C$ = capacidade do host), objetivo =
  minimizar hosts ativos. O campo de **prioridade** da requisição também abre
  uma extensão mais rica (precedência guaranteed vs. best-effort) — simulado
  primeiro em 1D, uma extensão honesta em vez de suposição oculta.

### 🟢 Hospedado em PlanetLab/CoMon (traces de 10 dias, mar–abr 2011)

- **Fonte:** traces públicos de workload distribuídos pelo projeto de
  monitoramento CoMon; **o benchmark canônico de BPP/consolidação de VM** na
  literatura de heurísticas/meta-heurísticas de 2011–2022 (p.ex. avaliações
  OpenStack Neat / CloudSim MBFD, UP-VMC, AEDQN-VMC). Utilização de CPU de
  > 1.000 VMs amostrada a cada 5 min; prática padrão filtra para 5–90% de
  utilização e fatia por dia.
- **Relaciona:** demanda CPU/RAM por VM por dia → $w_i$; capacidade do
  servidor físico → $C$; minimizar hosts ativos é consolidação clássica como
  BPP 1D.
- **Mapeamento BPP:** idêntico ao acima. A prática padrão na literatura de
  consolidação — fatiar os traces em uma instância por dia — mapeia
  diretamente para o baldes toy/médio/grande do projeto.

### 🟢 Google Borg traces 2011/2019 e Bitbrains Grid Workloads Archive

- **Fonte:**
  [github.com/google/cluster-data](https://github.com/google/cluster-data)
  (CC-BY) · [Bitbrains / Grid Workloads Archive](https://www.gridworkloads.org/)
  — 1.750 VMs de clusters de hospedagem gerenciada (fastStorage 1.250 VMs +
  Rnd 500 VMs, 30 dias, amostrados a cada 5 min).
- **Relaciona:** séries temporais reais de utilização de memória/CPU;
  academicamente de acesso livre, amplamente citado em papers de CloudSim +
  consolidação empírica.
- **Mapeamento BPP:** mesmo de acima, com recursos multidimensionais mais
  ricos possíveis (CPU, memória). Ambos são reais e podem ancorar a alegação
  de "dados reais" no relatório. Azure Packing-2020 continua sendo nossa
  primeira escolha: recursos normalizados tornam a redução 1D limpa, e os
  tamanhos de requisição por VM encaixam bem no recorte "balde médio ≤ 60
  itens para solver exato" do plano.

---

## 3. Backup e Arquivamento de Dados (media/volume allocation)

### 🟢 LANL Anonymous Filesystem Walk Metadata (tamanhos de arquivo verdadeiramente reais)

- **Fonte:**
  [LANL Storage Data (fsstats 2011/2012 + archive/NFS walks)](https://usrc.lanl.gov/data/storage-data.php),
  liberado sob LA-UR-07-5769.
- **Relaciona:** um walk real de sistema de arquivos de datacenter:
  **112M+ registros com tamanhos de arquivo**, create/mod times, UID/GID por
  arquivo — sem fabricação, do Los Alamos National Laboratory.
- **Mapeamento BPP:** itens = arquivos/datasets ($w_i$ = tamanho do arquivo em
  GB), caixas = volumes de armazenamento ($C$ = capacidade da mídia). O
  embasamento industrial para $C$ e limites de tamanho vem da literatura de
  deploy real: o Oklahoma PetaStore reporta "fitas LTO-5 1.5 TB / LTO-6 2.5
  TB, arquivo mínimo 1 GB, máximo 250 GB, pacote recomendado 10–100 GB"
  (Calhoun, _J. Comput. Sci._ 2016) — dando restrições industriais tanto para
  $C$ quanto para $w_i$ admissíveis. A regra "nenhum arquivo > C" acrescenta o
  caso de borda do item insplittable que a restrição de capacidade do
  enunciado já implica.

### 🟢 Tabelas de Volume de Dados do SDSS (datasets como itens grandes)

- **Fonte:**
  [`sdss4.org/dr17/data_access/volume/`](https://www.sdss4.org/dr17/data_access/volume/)
  — volumes reais publicados por produto de dados do SAS (p.ex.,
  `apogee/spectro/redux` 52 TB, `manga/spectro/analysis` 9.7 TB, `eboss/lss`
  1.07 TB...).
- **Relaciona:** backup dos dados de pesquisa de uma instituição no nível de
  **projetos/produtos de dados** agregados (tamanhos de itens GB–TB, muito
  melhor encaixado no "cenário de backup universitário" do enunciado do que
  walks de arquivos pequenos). O SDSS documenta publicamente o volume e a
  contagem de arquivos de cada produto, então a granularidade do item pode
  ser escolhida tanto no nível de produto quanto no nível de arquivo.

---

## 4. Alocação de Armários e Espaços nos Laboratórios (pior adequação de dado real)

### 🟢 Zenodo: gerador de rack-loading com demanda semanal (catálogo Hoare & Beasley)

- **Fonte:** [Zenodo record 23104538](https://doi.org/10.5281/zenodo.23104538)
  (Souyri, Lahrichi & Rousseau, 2026) — 105 instâncias × 104 semanas (qty;
  length,width,height por item); **as dimensões dos itens vêm do catálogo real
  de estoque de loja de varejo de Hoare & Beasley (2001), distribuído pela
  OR-Library**; quantidades sintéticas.
- **Relaciona:** rack-loading num contexto de esterilização/logística —
  famílias de itens com dimensões precisas em mm mais quantidades de demanda
  semanal, empacotadas em racks com capacidade finita de seção transversal.
- **Mapeamento BPP:** o checkpoint real mais próximo de "alocação de
  armário/sala": itens = famílias de equipamentos (comprimento utilizável por
  unidade), caixas = baias de armário/rack, $C$ = comprimento de fileira
  utilizável da baia. A formulação 1D do enunciado vale quando as baias são
  uniformes; as colunas de largura/altura dos itens permitem ainda uma
  extensão 2D como trabalho futuro (como o próprio enunciado sugere).

### 🟡 Dados de auditoria de espaço físico de laboratório (necessários para a narrativa do relatório)

- **Fonte:** duas auditorias acadêmicas reais de utilização de armazenamento
  em lab —
  [Kennesaw State DigitalCommons, estudo de lab space na Siemens Energy](https://digitalcommons.kennesaw.edu/egr_srdsn/27)
  (dimensões de cubo de prateleira/armário medidas em pés cúbicos; ~10.45% do
  espaço do lab usado para estocagem) e um estudo de 5S/otimização de espaço
  do laboratório de Ciências Biológicas da NTU
  ([Kia Min Wee 2018](http://hdl.handle.net/10356/76414)), mais um
  levantamento de medição de **equipamentos** de facility de laboratório
  nacional
  ([Hebert & Kang 2015 — 361 equipamentos grandes localizados, medidos,
  categorizados em 6 grupos](https://exa.ai/library/publication/dhbzf10y1bg)).
- **Relaciona:** estes dão o _contexto industrial_ do enunciado para a
  introdução do relatório: famílias de equipamentos (analítico vs. estocagem
  vs. processos), dimensões medidas de armários/prateleiras e volumes de
  estocagem de espaços reais de lab. Mas são dados de levantamento (poucos
  itens por site), não instâncias de BPP prontas.
- **Mapeamento BPP:** as medidas de Hebert & Kang fornecem contagens de
  equipamentos + categorias físicas quase diretamente; as auditorias de
  lab-space fornecem $C_{\text{armário}}$ via volumes cúbicos medidos.
  Avaliação honesta: adequação 🟡 — o suficiente para afirmar "tipos reais de
  equipamentos e dimensões de armários de auditorias publicadas", mas as
  instâncias teriam de ser agregadas de estatísticas descritivas, não de
  dados completos no nível de item.

---

## 5. Diagramação e Alocação de Questões em Provas (alocação de espaço de página)

### 🟢 Corpora abertos de questões de prova (questões com comprimentos de texto medidos)

- **Fontes:**
  - [HF `datavorous/entrance-exam-dataset`](https://huggingface.co/datasets/datavorous/entrance-exam-dataset)
    — 44.4k questões reais do JEE-Advanced [2006–2024] com enunciados, tags de
    prova/disciplina e metadados por questão.
  - [HF `letmarchezi/ENEM_Brazil_National_High_School_Exam_2022_to_2024`](https://huggingface.co/datasets/letmarchezi/ENEM_Brazil_National_High_School_Exam_2022_to_2024)
    — provas completas oficiais do **ENEM 2022–2024** como extratos de PDF
    (brasileiro, casa com o contexto USP!).
  - [HF `OpenTWBench/tw-exam-bench`](https://huggingface.co/datasets/OpenTWBench/tw-exam-bench)
    — 30 provas oficiais de serviço público de Taiwan (Apache-2.0; dados do
    ministério oficial).
- **Relaciona:** cada questão é um item $i$; $w_i$ = **altura renderizada
  estimada** (derivada da contagem de caracteres/tokens do enunciado + alturas
  dos blocos de alternativas; uma constante de calibração por tamanho de
  fonte conecta comprimentos de texto ao espaço impresso). Caixas = páginas
  da prova: $C$ = área de conteúdo impressa menos cabeçalhos/margens. Uma
  nuance inteira extra: uma questão deve caber inteira na página (sem
  fragmentação entre páginas — o enunciado menciona isso explicitamente como
  objetivo secundário).
- **Mapeamento BPP:** empacotar questões em páginas minimizando a contagem de
  páginas **é o caso de uso do enunciado à letra** ("minimizar o número total
  de páginas impressas"), e o ENEM é maximamente contextual (provas oficiais
  brasileiras — exatamente o público do relatório). Duas ressalvas a serem
  dadas abertamente no relatório: (a) as alturas renderizadas devem ser
  _derivadas_ dos comprimentos de texto das questões (uma constante de
  calibração por tamanho de fonte; o estudo de comprimento de provas de Lin,
  Lu & Lien 2021 — 611 itens reais com média de 88.8 palavras/item — oferece
  calibração publicada); (b) as alturas derivadas devem ser validadas contra
  uma amostra de layouts reais de páginas do ENEM antes de rodar os solvers.

---

## 6. Conduta recomendada para o grupo

1. **Dataset real primário:** escolher um caso de uso e pareá-lo com seu
   melhor candidato:
   - carga → `supply-chain-logistics-data` (OrderList → caminhões)
   - consolidação de VMs → `AzureTracesForPacking2020` (feito para isso;
     também o enquadramento mais fácil)
   - backup → walk de sistema de arquivos do LANL + capacidades industriais
     do PetaStore
   - armários de lab → Zenodo rack-loading (catálogo Hoare & Beasley) +
     tamanhos de auditorias de lab publicadas
   - paginação de provas → **dataset ENEM 2022–2024** (o mais contextual
     brasileiro e autocontido de explicar)
2. **Manter o `pick-and-place-binning-dataset` sintético** como _"benchmark
   controlado"_ (tem baselines greedy! fórmula 1D limpa) justamente porque
   todo candidato real acima precisa de pré-processamento.
3. **Narrativa híbrida do relatório (menos surpresas):** desenvolver e calibrar
   nas instâncias sintéticas → depois aplicar o pipeline em muitas instâncias
   reais (p.ex. questões do ENEM ou requisições de VM via o pré-processamento
   do ator A3) como **conjunto de validação**, e dizer isso explicitamente no
   relatório. Combina com a Fase 2 do `TODO.md` (normalizar para instâncias
   com `w_i` / `C` comuns) e mantém as comparações de ambos os solvers +
   heurística vs bound `L2` uniformes.

**Nota de proveniência:** todos os links acima foram verificados como
publicamente disponíveis no momento da escrita (out 2026); consolide-os em
`refs.bib`/bibliografia durante a Fase 1 do [`TODO.md`](./TODO.md).
