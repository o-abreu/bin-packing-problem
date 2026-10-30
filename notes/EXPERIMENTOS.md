# Experimentos — Registro de resultados

Documento de trabalho companheiro do relatório ([`report/main.qmd`](../report/main.qmd),
seção de modelagem em [`report/sections/metodologia/modelagem-matematica.qmd`](../report/sections/metodologia/modelagem-matematica.qmd)).
Registra **o que já foi medido**, com os números, o protocolo e as ressalvas — para
que nenhum resultado precise ser rederivado. Toda a prosa está em pt-BR; os
caminhos de código, em inglês.

**Última atualização:** 29 out. 2026 · **Máquina:** 20 CPUs, 30 GB RAM ·
**Solvers:** HiGHS 1.15.1 (`highspy`), Gurobi **indisponível** (sem licença).

---

## 1. Modelo em teste

VSBPP fixo-charge bidimensional, formulação R1–R10 de
`report/sections/metodologia/modelagem-matematica.qmd`:

| id | restrição |
| --- | --- |
| R1 | atribuição completa: $\sum_j x_{ij} = 1$ |
| R2 | capacidade de área: $\sum_i a_i x_{ij} \le \sum_t A_t y_{jt}$ |
| R3 | capacidade de peso: $\sum_i w_i x_{ij} \le \sum_t W_t y_{jt}$ |
| R4 | um tipo por caminhão: $\sum_t y_{jt} \le 1$ |
| R5 | vínculo: $x_{ij} \le \sum_t y_{jt}$ |
| R6 | partida após disponibilidade: $\tau_j \ge av_i - M(1-x_{ij})$ |
| R7 | janela de consolidação: $\tau_j \le av_i + \Delta + M(1-x_{ij})$ **(sinal corrigido)** |
| R8 | chegada no prazo: $\tau_j \le dl_i - t_{\text{viagem}} + M(1-x_{ij})$ |
| R9 | quebra: $x_{ij} = 0$ para $j > i$ |
| R10 | caminhões abertos ocupam prefixo: $\sum_t y_{jt} \ge \sum_t y_{j+1,t}$ |
| R11 | ordenação de pacotes idênticos: $\sum_j j\,x_{ij} \le \sum_j j\,x_{i'j}$ (ver §4) |

> Nota histórica: a R7 estava impressa com $-M(1-x_{ij})$ e tornava **infactível**
> toda instância em que um caminhão não contém todos os pacotes. Corrigida para
> $+M(1-x_{ij})$; ver §3, primeira linha.

## 2. Instância e scripts

`data/raw/order_large.csv`: 4 635 pacotes, **61 rotas** (`City_61 → d`), viagens
diretas ⇒ **61 MILPs independentes**. `counts`: 1–468 pacotes por rota
(mediana 49); grupos de pacotes idênticos (área, peso, disponibilidade, prazo)
1–20 por rota (**mediana 3**).

| script | o que mede |
| --- | --- |
| `scripts/symmetry_benchmark.py` | R1–R8 vs R1–R9 vs R1–R10 (nós, tempo, objetivo) |
| `scripts/package_symmetry_benchmark.py` | R11: validação por enumeração exaustiva + benchmark |

```bash
devenv shell -- python scripts/symmetry_benchmark.py
devenv shell -- python scripts/package_symmetry_benchmark.py
```

Ambos imprimem tabela markdown; parâmetros: `time_limit`, `threads`, `gap`
(`solve(...)` em `scripts/symmetry_benchmark.py`).

---

## 3. Quebra de simetria de slots (R9, R10)

Instâncias sintéticas com pacotes **distintos**, $|J| = |I|$, HiGHS padrão,
5 sementes. Objetivo idêntico nas três variantes em todos os casos.

### $n = 12$

| variante | nós (5 sementes) | mediana |
| --- | --- | --- |
| sem quebra (R1–R8) | 971, 186, 134, 259, 137 | 186 |
| R9 | 13, 0, 1, 1, 1 | 1 |
| **R9–R10** | **1, 1, 1, 1, 1** | **1** |

### $n = 20$

| variante | nós (5 sementes) | mediana | tempo |
| --- | --- | --- | --- |
| sem quebra | 2 109 · 9 395\* · 11 192\* · 13 478\* · 12 619\* | — | 4 de 5 estouraram 60 s |
| R9 | 5 247 · 1 414 · 1 663 · 878 · 5 879 | 1 663 | ≤ 18,6 s |
| **R9–R10** | **335 · 25 · 70 · 3 · 1 961** | **70** | ≤ 8,2 s |

\* limite de tempo (60 s) atingido — o valor é o que foi explorado até o limite.

**Achados.**

1. **R9 isolada pode piorar** o limitante (5 247 vs 2 109 nós na semente 0):
   fixar $x_{ij}=0$ restringe a relaxação e enfraquece o bound de LP.
2. O ganho real vem do **par R9–R10**: mediana 1 663 → 70 nós ($n=20$); $n=12$
   fecha no nó raiz.
3. Instância real de 5 pacotes (`City_54`, `order_small`): 1 nó nas três
   variantes, objetivo 29 331,91 (= 9,6 m + 7,6 m, conferido à mão). O efeito é
   nulo quando a prova não ramifica.

### 3.1 Contribuição marginal de cada quebra (R9 vs R10)

Variante **R10 sozinha** (prefixo sem a ordenação de pacotes), 20 s de limite,
`symmetry_benchmark.solve(..., variant="r10")`:

| $n$ | semente | sem quebra | R9 | **R10** | R9–R10 |
| --- | --- | --- | --- | --- | --- |
| 12 | 0 | 971 | 13 | 1 083 | **1** |
| 12 | 1 | 186 | 0 | 312 | **1** |
| 12 | 2 | 134 | 1 | 87 | **1** |
| 12 | 4 | 137 | 1 | 154 | **1** |
| 20 | 0 | 2 109 (10,9 s) | 5 247 | 6 941\* | **335 (1,7 s)** |
| 20 | 1 | 2 421\* | 1 414 | 12 114 | **25 (1,9 s)** |
| 20 | 3 | 3 127\* | 878 | 5 578 | **3 (1,8 s)** |

\* limite de tempo atingido (valores não comparáveis entre variantes nesse caso).

**Conclusões.**

1. **R10 não é redundante nem implicada por R9.** Contraexemplos explícitos:
   $\{1,2\}$ no slot 1 e $\{3\}$ no slot 3 (slot 2 vazio) satisfaz R9 e viola
   R10; $\{2\}$ no slot 1 e $\{1\}$ no slot 2 satisfaz R10 e viola R9.
2. **R10 é inócua quanto ao ótimo**: enumeração exaustiva em 40 instâncias com
   $n=5$ e pacotes distintos — desvio 0,00 entre o ótimo irrestrito e o ótimo
   com R9–R10.
3. **R10 não é inócua quanto ao esforço**: isolada chega a ser pior que não
   quebrar simetria (6 941 nós com limite vs 2 109 nós sem quebra, $n=20$,
   semente 0). Só o par rende.
4. Em rotas reais difíceis (`City_48`, `City_54`), **todas** as variantes
   estouram o limite de 30 s — contagem de nós sob limite não é comparável;
   a evidência limpa vem das sintéticas que fecham.

---

## 4. Simetria entre pacotes (R11) — avaliada, **não** incorporada

$$\sum_{j \in J} j\,x_{ij} \;\le\; \sum_{j \in J} j\,x_{i'j}
\quad \text{para pares consecutivos } i<i' \text{ de pacotes idênticos.}$$

**Validade (enumeração exaustiva).** 60 instâncias com $n=5$ e 10 com $n=6$,
com pacotes repetidos: desvio máximo entre o ótimo irrestrito e o ótimo com
R9–R11 = **0,00**.

**Desempenho (sintéticas com cópias, 5 sementes).**

| grupos | R1–R10 (nós) | R1–R11 (nós) |
| --- | --- | --- |
| 5 tipos × 4 cópias | 38 · 1 495 · 617 · 3 · 21 909 | **9 · 333 · 148 · 1 · 2 178** |
| 4 tipos × 5 cópias | 55 · 15 992 · 194 · 3 · 729 | **20 · 808 · 27 · 1 · 40** |
| 20 pacotes distintos | 335 | 335 (vacuamente inócua ✓) |

**Subamostras reais ($n=30$ e $n=40$).** Nós caem em algumas rotas
(`City_37` 65→11; `City_58` 231→19), mas **não há mudança ou há piora** em
outras (`City_18` 13→26) e o tempo frequentemente **aumenta** (0,2 s → 2,3 s):
as linhas extras pesam no pré-processamento de modelos pequenos.

**Decisão (29 out. 2026, revista):** R11 **integra o modelo** e é aplicada em
todas as instâncias, inclusive nas pequenas — o argumento adotado é que uma
instância que resolve no nó raiz não tem tempo de prova a economizar, e nas
maiores o corte de nós domina. O custo de montagem das linhas extras (visível
nos runs reais de $n=30$–$40$) fica registrado como ressalva.

---

## 5. Paralelismo entre rotas — primeiro benchmark

37 rotas com $n \le 60$, modelo R1–R10, `ProcessPoolExecutor`.

| configuração | tempo | speedup |
| --- | --- | --- |
| A) sequencial, `threads=1` | 192,0 s | — |
| **B) 20 processos × 1 thread** | **60,2 s** | **3,2×** |
| C) sequencial, `threads=auto` | 191,7 s | 1,0× |

Ótimos idênticos (soma 861 890,55; desvio 0,00); 46 092 nós de B&B somados.

**Por que só 3,2× em 20 núcleos:** a cauda. Distribuição de tempo por rota:

| rota | $n$ | grupos | nós | tempo |
| --- | --- | --- | --- | --- |
| `City_48` | 37 | 9 | 23 563 | 60,0 s (limite) |
| `City_54` | 59 | 3 | 13 153 | 60,0 s (limite) |
| `City_5` | 49 | 4 | 3 347 | 26,2 s |
| `City_14` | 35 | 3 | 5 290 | 13,0 s |
| `City_15` | 52 | 2 | 1 | 8,4 s |

**6 rotas concentram 90% do tempo**; o makespan é a rota mais difícil, então o
speedup máximo possível é $192/\text{(tempo da rota mais difícil)}$. Com 120 s de
limite, `City_48` (55 840 nós) e `City_54` (44 231 nós) **não fecham**; com R11
caem para 18 156 e 2 024 nós, mas ainda estouram o limite.

**Consequência:** o gargalo é a formulação, não o número de núcleos.

---

## 6. Potencial de pré-processamento (medido, ainda não implementado)

| ideia | efeito medido |
| --- | --- |
| **P1. Agregar pacotes idênticos** (variáveis de contagem $z_{gj}$ + binário $w_{gj}$) | $x_{ij}$: 795 137 → **3 329** em todas as rotas (239×); `City_54`: 59 pacotes → 3 grupos; `City_58`: 468 → 20 |
| **P2. Teto de slots** $m=\min\{n,\lfloor \mathrm{UB}/(c_{\min} d)\rfloor\}$ | `City_48`: $n^2=1\,369$ → 72; `City_17`: 46 656 → 30 |
| **P3. Filtro de tipos por rota** | nenhum par domina na frota global; checar por rota |
| **P4. Fechamento por inspeção** | **9 de 61** rotas resolvidas sem MILP (carga cabe em 7,6 m + janela ok) |
| **P6. Triagem de inviabilidade** | 0 itens inviáveis por janela/peso/área (resultado a reportar) |

**Ressalva importante (P2):** usar o *número de caminhões da FFD* como teto é
**inválido** para objetivo de custo — o ótimo pode usar mais caminhões menores e
sair mais barato. O teto válido é o de **custo**: todo caminhão custa ao menos
$c_{\min}d$, logo $m \le \lfloor \mathrm{UB}/(c_{\min}d) \rfloor$.

Outros fatos úteis: janela de disponibilidade mediana de 24 h por rota (máx.
56 h) contra $\Delta = 4$ h ⇒ consolidação ampla é impossível; LB de frota por
área soma 270 caminhões e por peso 226.

---

## 7. Glossário

- **LB (lower bound):** valor que nenhuma solução viável pode bater. Ex.:
  $\mathrm{LB}_{\text{área}} = \lceil \sum_i a_i / A_{\max} \rceil$; ou o ótimo
  da relaxação linear do MILP. Serve para **provar otimalidade** (quando
  $\mathrm{LB} = \mathrm{UB}$) e para cortar nós.
- **UB (upper bound):** valor de uma solução viável conhecida (ex.: FFD). Todo
  UB é atingível; todo LB é inatingível-para-menos.
- **gap:** $(\mathrm{UB}-\mathrm{LB})/|\mathrm{UB}|$; 0 ⇒ prova de otimalidade.
- **LPT:** *Longest Processing Time first* — escalonamento que ordena as tarefas
  por duração decrescente e aloca cada uma ao recurso menos carregado
  [Graham 1969]; usado aqui para distribuir rotas entre processos.

---

## 8. Pendências

1. **P1 (agregação) como formulação oficial** do experimento? Recomendação:
   sim — é o que derruba a cauda; manter o modelo item-a-item como referência
   de validação (mesmo ótimo nas instâncias pequenas).
2. **Gurobi:** sem `gurobi`/`gurobipy` nem `~/gurobi.lic` (`GRB_LICENSE_FILE`
   vazio). Licença acadêmica; sem ela, pareamento "comercial + livre" do
   enunciado (§4.3) cai para HiGHS vs CBC (já previsto no `TODO.md`).
3. Coletar as quatro métricas por instância (status, objetivo, tempo, gap) em
   CSV, para as 61 rotas, nos dois solvers.
