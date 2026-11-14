---
title: "Empacotamento em Frotas Heterogêneas"
sub_title: "Modelagem VSBPP e Solução Exata sobre Dados Reais de Roteirização"
location: "Instituto de Ciências Matemáticas e de Computação - Universidade de São Paulo (ICMC-USP)"
authors:
  - Guilherme de Abreu Barreto
  - Eduarda Almeida Garrett de Carvalho
  - Gabriel Demba
  - Nicholas Eiti Dan
  - Wiltord Nyakeruma Mosingi
date: 2026-11-11
theme:
  override:
    footer:
      style: template
      left: "{location}"
      center: ""
      right: "{current_slide} / {total_slides}"
---

<!-- jump_to_middle -->

INTRODUÇÃO
==========

Contextualização
----------------

<!-- column_layout: [1, 3] -->

<!-- column: 0 -->

# Tema

_Alocação de cargas em veículos_

<!-- pause -->

<!-- column: 1 -->

# Dataset

**Título:** Large-Scale Route Optimization Accelerator

**Autores:** Microsoft, et al.

**Fonte:** https://github.com/microsoft/dstoolkit-route-optimization

> Trata-se de um benchmark para o **Problema do Roteamento de Veículos (Vehicle
> Routing Problem - VRP)**

Adaptação
---------

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

Ao reduzir o número máximo de paradas para `1` o VRP degenera para um
**Problema de Empacotamento com Compartimentos de Tamanho Variável (Variable
Sized Bin Packing Problem - VSBPP)**

<!-- pause -->

> **Projeção da matriz de distâncias**; em preto, as 61 rotas diretas a partir de CD (City_61).

<!-- column: 1 -->

![image:width:100%](assets/fig-rede.png)


<!-- end_slide -->

<!-- jump_to_middle -->

Análise Estatística Exploratória
===

Correspondência entre parâmetros e o vocábulo do VSBPP
---


| Parâmetro          | Correspondência com o VSBPP |
| ------------------ | --------------------------- |
| Pacotes            | Itens                       |
| Frota de caminhões | _Bins_                      |
| Pedidos x Rotas    | Instâncias de VSBPP         |


Pacotes
---

<!-- column_layout: [2, 3] -->

<!-- column: 0 -->

**4.635** unidades, em um total de **235** classes distintas.

<!-- pause -->

# Características

- Área

- Peso

## Herdadas do Pedido

- Disponibilidade

- Prazo de entrega

<!-- column: 1 -->

<!-- pause -->

![image:width:100%](assets/fig-pacotes-corr.png)

> Gráfico Área × peso dos pacotes (escala logarítmica); as retas tracejadas marcam densidades constantes.


Frota
---

<!--pause-->

# 4 variedades de caminhão

O VSBPP difere do BPP clássico ao admitir compartimentos de capacidade variável. O objetivo passa a ser o custo total dos compartimentos usados.

<!-- pause -->

## Características

| Compr. (m) | Área (m²) | Peso (kg) | Custo (US$/km) | Custo/m²  | Custo/kg  | Densidade (kg/m²) |
| ---------: | --------: | --------: | -------------: | ----------------: | ----------------: | ----------------: |
|        7,6 |     16,56 |     8.000 |            5,5 |             0,332 |           0,00069 |               483 |
|        9,6 |     20,93 |    14.000 |            6,5 |             0,311 |           0,00046 |               669 |
|       12,5 |     30,25 |    24.000 |            9,0 |             0,298 |           0,00038 |               793 |
|       16,5 |     40,25 |    27.000 |           10,0 |             0,248 |           0,00037 |               671 |

> **Nota:** as colunas Custo/m² e Custo/kg dividem o custo por km pela referida capacidade **total** do
caminhão.

Área × peso enquanto fatores limitantes
---

<!-- column_layout: [2, 2] -->

<!-- column: 0 -->

![image:width:85%](assets/fig-rotas.png)

<!-- column: 1 -->

> Caminhões por destino, se a frota fosse só de veículos de 16,5 m: limite por área contra limite por peso (eixos log₂). A área de cada ponto é proporcional ao número de destinos com o mesmo par de limites.


Pedidos
---

Agrupamentos de pacotes com os mesmos parâmetros de disponibilidade e prazo.

# Características

- Identificação do pedido

- Identificação dos pacotes contidos no pedido

- Disponibilidade

- Prazo de entrega

Disparidades e comunalidades entre pedidos
---

<!-- column_layout: [2, 1] -->

<!-- column: 0 -->

![image:width:100%](assets/fig-pedidos-volume.png)

<!-- column: 1 -->

<!-- incremental_lists: true -->

- Elevada heterogeneidade no volume de pacotes entre os pedidos

<!-- speaker_note: Distribuição em forma de calda longa com mediana (`10`) abaixo da média e elevado nível de variância (média de `12,7 ± 9,9`). Os `10%` dos pedidos mais volumosos concentram quase `27,5%` dos pacotes, enquanto os 50% dos pedidos menos volumosos juntos concentram `21,6%`. -->

- Elevada homogeneidade dos pacotes de um mesmo pedido

<!-- speaker_note: No máximo `4` variedades por pedido, na esmagadora maioria dos casos (`86.6%`) os pacotes são todos da mesma classe. -->

Disponibilidade dos pedidos
---

<!-- column_layout: [2, 1] -->

<!-- column: 0 -->

![image:width:100%](assets/fig-pedidos-horas.png)

<!-- column: 1 -->

- A grande maioria dos pacotes é liberada em um mesmo horário: `23:59:59`

- Há pouco aprimoramento que pode ser feito com a janela de consolidação (`Δh - 4`) e forte separação na disponibilidade de pacotes entre dias (8 horas sem estarem disponíveis novos pacotes todo dia).

Rotas
---

# Poucos pedidos concentram muitos pacotes, e poucas rotas concentram muitos pedidos

| Demanda | 6 maiores rotas (%) | Rotas até 90% | Gini |
| --------------- | --------------- | --------------- | --------------- |
| Pacotes | 35,3 | 33 | 0,55 |
| Peso | 38,5 | 32 | 0,57 |
| Área | 43,6 | 31 | 0,61 |

<!-- end_slide -->

<!-- jump_to_middle -->

MODELAGEM MATEMÁTICA
===

Conjuntos
---

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

<!-- pause -->

# Grupos de pacotes idênticos

```latex +render
$G = \{1, \dots, \mid G \mid \}$
```

Cada qual com multiplicidade

```latex +render
$n_g \mid n, g \in  Z^*$
```

<!-- column: 1 -->

<!-- pause -->

# Tipos de caminhões disponíveis

```latex +render
$T = \{1, ..., 4\}$
```

# _Slots_ de caminhão disponíveis

```latex +render
$J = \{1, ..., m\}, m \le n \mid n = \sum_g n_g$
```

<!-- end_slide -->

<!-- column_layout: [1, 2] -->

<!-- column: 0 -->

Parâmetros
---

> Consolidação das tabelas IV–VII do relatório: apenas os parâmetros que entram no modelo.

<!-- column: 1 -->

| Parâmetro  | Descrição                  | Coluna               | Unidade |
| ---------- | -------------------------- | -------------------- | ------- |
| `g`        | grupo de pacotes idênticos | derivado             | ---     |
| `a_g`      | área de um pacote          | `Area`               | m²      |
| `w_g`      | peso de um pacote          | `Weight`             | kg      |
| `av_g`     | disponibilidade do grupo   | `Available_Time`     | h       |
| `dl_g`     | prazo do grupo             | `Deadline`           | h       |
| `d`        | distância da rota          | `Distance(M)`        | km      |
| `t`        | índice do tipo de caminhão | `truck_type`         | ---     |
| `A_t`      | capacidade de área         | `area_capacity_m2`   | m²      |
| `W_t`      | capacidade de peso         | `weight_capacity_kg` | kg      |
| `c_t`      | custo por quilômetro       | `cost_per_km`        | US$/km  |
| `v`        | velocidade do caminhão     | `speed_kmh`          | km/h    |
| `C_t`      | custo fixo por viagem      | derivado (`c_t d`)   | US$     |
| `t_viagem` | tempo de viagem            | derivado (`d/v`)     | h       |
| `Δ`        | janela de consolidação     | política (4 h)       | h       |
| `M`        | constante de desativação   | derivado             | h       |

Variáveis de decisão
---

<!-- column_layout: [3, 2] -->

<!-- column: 0 -->

<!-- pause -->

# Quantos pacotes do grupo `g` viajam no caminhão `j`

```latex +render
$z_{gj} \in \{ 0, 1, \dots, n_g \}$
```

<!-- pause -->

# Se ao menos um pacote do grupo `g` viaja no caminhão `j`

```latex +render
$u_{gj} \in \{0, 1\}$
```

<!-- column: 1 -->

<!-- pause -->

# Se o caminhão `j` é do tipo `t`

```latex +render
$y_{jt} \in \{ 0, 1 \}$
```

<!-- pause -->

# O instante de partida do caminhão `j`

```latex +render
$\tau_j \ge 0$
```

Função objetivo
---

```latex +render
$\min \sum_{j \in J} \sum_{t \in T} C_t \times y_{jt}$
```

Restrições (R1-R4)
---

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

# R1 - Atribuição completa dos pacotes

```latex +render
$\sum_{j \in J} = n_g, \forall g \in G$
```

# R2 - Capacidade de área

```latex +render
$\sum_{g \in G} a_g z_{gj} \le \sum_{t \in T} A_t y_{jt},\ \forall j \in J$
```

<!-- column: 1 -->

# R3 - Capacidade de carga

```latex +render
$\sum_{g \in G} w_g z_{gj} \le \sum_{t \in T} W_t y_{jt}\ \forall j \in J$
```

# R4 - Um tipo por caminhão

```latex +render
$\sum_{t \in T} y_{jt} \le 1,\ \forall j \in J$
```

Restrições (R5-R8)
---

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

# R5 - Vínculo entre grupo de pacotes e caminhões

```latex +render
$z_{gj} \le n_g \sum_{t \in T} y_{jt},\ \forall g \in G, j \in J$
```

# R6 - Ocupação do grupo em cada caminhão

```latex +render
$u_{gj} \le z_{gj} \le n_g u_{gj},\ \forall g \in G,\ j \in J$
```

<!-- column: 1 -->

# R7 - Partida após disponibilidade

```latex +render
$\tau_j \ge av_g - M(1 - u_{gj}),\ \forall g \in G,\ j \in J$
```

# R8 - Janela de consolidação

```latex +render
$\tau_j \le av_g + \Delta + M (1 - u_{gj})\ \forall g \in G,\ j \in J$
```

Restrições (R9-R10)
---

# R9 - Chegada dentro do prazo

```latex +render
$\tau_j \le dl_g - t_{viagem} + M(1 - u_{gj})\ \forall g \in G,\ j \in J$
```

# R10 - Quebra de simetria

```latex +render
$\sum_{t \in T} y_{jt} \ge \sum_{t \in T} y_{y + 1, t}\ \forall j \in \{1, \dots, m - 1\}$
```

<!-- end_slide -->

<!-- jump_to_middle -->

SOLUÇÃO EXATA
===

Pré-processamento
---

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

<!-- pause -->

# Recorte

Separamos os pedidos em função da rota e o dia de disponibilidade em instâncias separadas de VSBPP.

<!-- pause -->

# Normalização

Para cada instância:

1. Converte-se as _timestamps_ para uma contagem de horas à partir da origem da instância

1. Agrupa-se os pacotes idênticos e os ordena em função de da maior área; e peso em caso de empate

<!-- column: 1 -->

<!-- pause -->

# Redução do modelo

Para cada instância:

1. **Filtro de tipos:** Admite-se apenas caminhões capazes de carregar o menor pacote disponível.

1. **Teto de slots:** Utiliza-se a heurística _First Fit Decreasing (FFD)_ para calcular um teto de caminhões a serem utilizados na solução ótima.

1. **Fechamento por inspeção:** Quando a carga inteira cabe em um único caminhão e a janela de tempo permite, é esta a solução ótima e não há MILP a se resolver.
