# VSBPP de frotas heterogêneas em rotas de distribuição

Trabalho de **SME 0110 — Programação Matemática** (ICMC-USP, 2º semestre de
2026): o problema de empacotamento com caixas de tamanho e custo variáveis
(VSBPP) aplicado a uma frota de caminhões real, resolvido por programação
inteira mista e por um método alternativo.

> **Estado.** Modelagem e pré-processamento fechados; o relatório já traz
> introdução, base de dados, pré-processamento, formulação e declaração de uso
> de IA. A seção de experimentos (solvers) está em desenvolvimento — o rascunho
> legado é `report/sections/experimento.qmd`, ainda não incluído no documento. O
> plano por fases está em [`notes/TODO.md`](./notes/TODO.md) e **tudo o que já
> foi medido** está em [`notes/EXPERIMENTOS.md`](./notes/EXPERIMENTOS.md) — leia
> antes de refazer qualquer número.

## O problema

O enunciado parte do roteamento de veículos (VRP). Impondo **uma única parada
por viagem**, cada rota degenera num VSBPP: os itens são pacotes e as caixas são
caminhões de quatro tipos, cada um com área de piso $A_t$, capacidade de peso
$W_t$ e custo $c_t$ por quilômetro. Como o custo de um caminhão na rota é
$C_t = c_t\,d$, o objetivo é o **custo fixo da frota**, não o número de
veículos.

A instância é **bidimensional**: um caminhão só é viável se respeitar área **e**
peso. Nos dados a área morde primeiro — a densidade mediana dos pacotes (589
kg/m²) fica próxima da razão do caminhão de 16,5 m (671 kg/m²), e a comparação
rota a rota dá 270 caminhões por área contra 226 por peso.

O modelo é o **agregado R1–R10**, descrito em
[`report/sections/metodologia/modelagem-matematica/index.qmd`](./report/sections/metodologia/modelagem-matematica/index.qmd):
a instância é definida sobre **grupos de pacotes idênticos** (mesma área, peso,
disponibilidade e prazo), cada um com multiplicidade $n_g$, e a decisão é
_quantos_ pacotes de cada grupo vão em cada caminhão ($z_{gj}$), mais o tipo do
caminhão ($y_{jt}$) e o instante de partida ($\tau_j$). Essa agregação é o que
torna as instâncias resolvíveis: 4.635 pacotes viram 239 grupos, e nenhuma
instância passa de 11 grupos.

## Dados

Fonte:
[Large-Scale Route Optimization](https://www.kaggle.com/datasets/mexwell/large-scale-route-optimization)
(MIT), espelho dos dados de amostra do acelerador da Microsoft
([`dstoolkit-route-optimization`](https://github.com/microsoft/dstoolkit-route-optimization)).
É um _benchmark_ "inspirado num cenário real" de um cliente de manufatura — não
são dados brutos de empresa.

| arquivo                    | o que é                                                               |
| -------------------------- | --------------------------------------------------------------------- |
| `data/raw/order_large.csv` | 4.635 pacotes, 365 pedidos, 61 rotas — a instância principal          |
| `data/raw/order_small.csv` | 10 pacotes em 2 rotas — caso de teste mínimo                          |
| `data/raw/distance.csv`    | matriz de distâncias **em metros** (apesar do nome `Distance(M)`)     |
| `data/raw/trucks.csv`      | frota, transcrita de `src/core/structure.py` do repositório de origem |
| `data/pre-processed/`      | instâncias e grupos gerados — versionados, regeneráveis em ~0,2 s     |

`Area` e `Weight` vêm escaladas por $10^4$ (divida por 10.000 para m² e kg). Os
arquivos brutos são **versionados e nunca re-baixados**. Proveniência, licença e
anotações coluna a coluna: [`notes/DATASETS.md`](./notes/DATASETS.md).

O conjunto de tarifas de frete usado no início do projeto foi **descartado**
como instância primária (o `minimum cost` fica abaixo do preço implícito em 78%
das classes) e permanece apenas como estudo de caso de dados inconsistentes.

## Relatório

O entregável é `report/main.qmd`: artigo IEEE em duas colunas, escrito em pt-BR,
montado a partir de arquivos incluídos.

```
report/
├── main.qmd                       # front matter + inclusões
├── refs.bib                       # Referências bibliográficas
├── _extensions/ieee/              # formato de periódico vendorizado
└── sections/
    ├── introducao.qmd             # I. Introdução
    ├── metodologia/
    │   ├── index.qmd              # II. Metodologia (inclui os três abaixo)
    │   ├── base-de-dados/
    │   │   ├── index.qmd          #   A. Base de dados + setup compartilhado
    │   │   ├── frota.qmd          #     1) Frota (tabela + densidade)
    │   │   ├── pacotes.qmd        #     2) Pacotes (distribuições e correlação)
    │   │   ├── pedidos.qmd        #     3) Pedidos (volume, tempo, janela)
    │   │   └── rotas.qmd          #     4) Rotas (rede e limites por área/peso)
    │   ├── pre-processamento/
    │   │   ├── index.qmd          #   C. Pré-processamento (código executado)
    │   │   ├── normalizacao.qmd   #     1) Normalização e recorte
    │   │   ├── reducao.qmd        #     2) Redução do modelo
    │   │   └── custo.qmd          #     3) Custo do pré-processamento
    │   └── modelagem-matematica/
    │       ├── index.qmd          #   D. Modelagem (chunk de tamanhos + inclusões)
    │       ├── conjuntos.qmd      #     1) Conjuntos (grupos, slots, simetria)
    │       ├── parametros.qmd     #     2) Parâmetros (tabelas III–VI)
    │       ├── variaveis.qmd      #     3) Variáveis de decisão
    │       ├── objetivo.qmd       #     4) Função objetivo
    │       ├── restricoes.qmd     #     5) Restrições R1–R10
    │       ├── sumario.qmd        #     6) Sumário do modelo
    │       └── complexidade.qmd   #     7) Complexidade computacional
    ├── disponibilidade.qmd        # III. Disponibilidade de dados e código
    ├── declaracao-uso-ia.qmd      # IV. Declaração de uso de IA
    └── experimento.qmd            # rascunho legado — NÃO incluído
```

Os caminhos das inclusões são resolvidos **a partir de `main.qmd`**, mesmo
quando aninhados — por isso `metodologia/index.qmd` escreve
`sections/metodologia/base-de-dados/index.qmd`, e não um caminho relativo a si.

```sh
devenv shell -- render-report      # report/main.qmd -> report/main.pdf
```

O PDF é gerado ao lado da fonte, em `report/main.pdf`, tanto por esse script
quanto pelo `:QuartoPreview` do Neovim — é o único local do relatório
renderizado, e ele é versionado (é o entregável). Não passe `--output-dir`: o
Quarto resolve esse caminho em relação ao arquivo de entrada, o que já produziu
uma segunda cópia em `report/output/`. Os intermediários `report/main_files/`
são ignorados pelo git.

**Situação das seções exigidas pelo enunciado (§4):** Introdução ✅ · Modelagem
Matemática ✅ · Solução via _solvers_ ⬜ (Gurobi e HiGHS já instalados; falta o
harness e a coleta das quatro métricas) · Método de Solução Alternativo ⬜ ·
Conclusão ⬜.

## Ambiente

Tudo é declarativo, via [devenv](https://devenv.sh) + direnv. **Nada de
`pip install` ou downloads avulsos**: dependências Python vão para
`requirements.txt` e ferramentas de sistema para `devenv.nix`.

```sh
direnv allow                     # ou: devenv shell
devenv shell -- render-report    # gera o PDF
devenv shell -- python scripts/aggregated_model.py City_54
```

- **Quarto 1.6.43**, fixado pelo input `nixpkgs-quarto`. Um _wrapper_ em
  `devenv.nix` fixa `QUARTO_PYTHON` no interpretador do venv — sem ele, o Quarto
  cai no `python3` do `PATH` e os chunks falham com `ModuleNotFoundError: yaml`.
- **pdflatex** com TeX Live do flake (IEEEtran, orcidlink, physics, mhchem). O
  Quarto só aceita pdflatex/xelatex/lualatex/latexmk — `tectonic` quebra o
  template.
- **Python 3.12** em `.devenv/state/venv`, com `pulp`, `highspy`, `gurobipy`,
  `pandas`, `matplotlib`, `pyarrow`, `ipykernel`/`nbclient`/`nbformat`.
- **Solvers:** HiGHS (`highspy`) e CBC (via PuLP) de fábrica; **Gurobi 13.0.3**
  (`pkgs.gurobi` + `gurobipy==13.0.3`) com licença acadêmica em `gurobi.lic` na
  raiz — arquivo **ignorado pelo git** e apontado por `GRB_LICENSE_FILE` no
  `devenv.nix`. Sem a licença, o Gurobi cai na versão restrita (2.000
  variáveis/restrições), insuficiente para as instâncias.

## Scripts

Todos rodam no venv do projeto e imprimem tabelas prontas para o relatório.

| script                                  | o que mede                                                                         |
| --------------------------------------- | ---------------------------------------------------------------------------------- |
| `scripts/aggregated_model.py`           | modelo agregado R1–R10: objetivo, nós e tempo por instância (`--all`, `--compare`) |
| `scripts/symmetry_benchmark.py`         | quebra de simetria no modelo item a item (R1–R8 vs R9 vs R10 vs R9–R10)            |
| `scripts/package_symmetry_benchmark.py` | ordenação de pacotes idênticos (R11), com validação por enumeração exaustiva       |

```sh
devenv shell -- python scripts/aggregated_model.py City_54 City_48 --compare
devenv shell -- python scripts/symmetry_benchmark.py
devenv shell -- python scripts/package_symmetry_benchmark.py
```

## Estrutura do repositório

```
data/raw/           # dataset publicado (MIT) — versionado, nunca re-baixado
data/pre-processed/ # instâncias e grupos gerados pelo pré-processamento
notes/              # DATASETS.md, TODO.md, EXPERIMENTOS.md
report/             # fontes Quarto do artigo (ver acima)
scripts/            # harnesses de experimento
AGENTS.md           # orientação para agentes de código
devenv.nix/.yaml    # ambiente declarativo; requirements.txt para o venv
pyrightconfig.json  # checagem de tipos (basedpyright)
```

## Convenções

- **Nada de instalação imperativa.** Faltou um módulo? `requirements.txt`.
  Faltou um programa? `devenv.nix`.
- **Números do relatório vêm do código**, não de digitação: o pré-processamento
  e as tabelas usam execução inline/`output: asis`.

## Licença

Trabalho acadêmico — direitos reservados aos integrantes do grupo até a entrega.
O conjunto de dados é MIT; proveniência em
[`notes/DATASETS.md`](./notes/DATASETS.md).
