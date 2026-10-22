# Projeto de Otimização
O Problema do Empacotamento (*Bin Packing*)

Disciplina: SME 0110 - Programação Matemática

## 1 Objetivo

Este trabalho tem como objetivo aprofundar o conhecimento em **otimização inteira**, aplicando os conceitos teóricos na modelagem e solução do **Problema do Empacotamento** (*Bin Packing Problem - BPP*) e suas variantes em contextos práticos e industriais.

Cada grupo deverá selecionar uma aplicação real de empacotamento/alocação de recursos, desenvolver o modelo matemático, resolvê-lo usando um *solver* comercial (Gurobi) e outro livre (SCIP) e, adicionalmente, implementar um método de solução alternativo (heurística ou meta-heurística).

## 2 Grupos

- O trabalho será feito em grupos de 4 ou 5 pessoas.
- No e-disciplinas será incluído um tópico para que os grupos sejam escolhidos.
- Caso alguém não escolha seu grupo até o final do prazo, a escolha será feita pelo professor.

## 3 Estrutura do Projeto

O trabalho será composto de duas implementações (em Python 3 ou C/C++), um relatório técnico descrevendo o problema, a modelagem, as soluções obtidas e as análises, além de duas apresentações durante o semestre. Os códigos, os dados das instâncias de teste e o relatório em PDF devem ser enviados pelo e-disciplinas em um único arquivo compactado (.zip, .rar ou .tar.gz). Apenas o último arquivo enviado será considerado.

### 3.1 Modelagem e Solução Exata

- **Seleção do Problema:** Cada grupo deve escolher um cenário de empacotamento ou alocação de recursos distinto. Exemplos:
  - **Alocação de Cargas em Veículos:** Minimização do número de caminhões ou contêineres necessários para transportar um conjunto de mercadorias com peso/volume limitados.
  - **Consolidação de Máquinas Virtuais (Cloud Computing):** Alocação de servidores virtuais (requisitando CPU e RAM) no menor número possível de servidores físicos ativos.

1

- **Backup e Arquivamento de Dados da Universidade:** Distribuição de arquivos e bases de dados de projetos de pesquisa em mídias de armazenamento/volumes digitais com limite rígido de capacidade (GB/TB).
- **Alocação de Armários e Espaços nos Laboratórios:** Agrupamento de equipamentos, bancadas de teste e insumos dos grupos de pesquisa dentro dos armários/salas de armazenamento do departamento, reduzindo o número de armários ocupados.
- **Diagramação e Alocação de Questões em Provas:** Agrupamento de questões de diferentes tamanhos (número de linhas ou altura visual) em páginas de avaliação com limite de espaço pré-definido, minimizando o número total de páginas impressas (e a fragmentação de questões entre páginas).

• **Modelagem Matemática:** O grupo deve apresentar o modelo completo, incluindo:

- Definição dos conjuntos (itens, caixas/recipientes).
- Variáveis de decisão (binárias para uso da caixa e alocação do item, e contínuas/inteiras se houver custo ou folga).
- Função objetivo (ex: minimizar o número total de caixas utilizadas ou minimizar o custo/desperdício total).
- Restrições de integridade e capacidade (ex: a soma dos tamanhos dos itens em uma caixa não pode exceder sua capacidade máxima).

# Formulação Genérica do Empacotamento Base (Bin Packing)

# Conjuntos e Índices:

- $I = \{1, \dots, n\}$ o conjunto de **itens**;
- $J = \{1, \dots, m\}$ o conjunto de **caixas/recipientes disponíveis** (com $m \geq n$);

# Parâmetros:

- $w_i$ peso ou tamanho do item $i \in I$;
- $C$ capacidade máxima de cada caixa $j \in J$.

# Variáveis de decisão:

- $y_j \in \{0, 1\}$ 1, se a caixa $j$ é utilizada; 0, c.c.
- $x_{ij} \in \{0, 1\}$ 1, se o item $i$ é alocado na caixa $j$; 0, c.c.

O modelo básico busca minimizar o total de caixas utilizadas:

$$\min \sum_{j \in J} y_j$$

sujeito a:

$$\sum_{j \in J} x_{ij} = 1, \quad \forall i \in I \text{ (Cada item deve ser empacotado em exatamente uma caixa)}$$

2

$$\sum_{i \in I} w_i x_{ij} \leq C y_j, \quad \forall j \in J \text{ (Respeito à capacidade máxima da caixa)}$$

$$x_{ij} \in \{0, 1\}, \quad \forall i \in I, \forall j \in J$$

$$y_j \in \{0, 1\}, \quad \forall j \in J$$

### 3.2 Desenvolvimento de um Método de Solução Alternativo

- **Escolha do Método:** Implementar uma heurística de empacotamento (ex: *First-Fit Decreasing*, *Best-Fit Decreasing*) ou meta-heurística (ex: Algoritmos Genéticos, Simulated Annealing, Busca Tabu) para resolver o problema de forma eficiente em instâncias de grande porte.
- **Implementação e Análise:** Executar o método proposto, analisar a qualidade das soluções obtidas e comparar com a solução ótima (ou *bound* inferior), discutindo diferenças e tempo computacional.

## 4 Estrutura do Relatório Final

O relatório final deverá ser estruturado nas seguintes seções, seguindo rigorosamente a ordem e os requisitos descritos abaixo:

1. **Introdução:** Apresente o problema de forma clara, contextualizando sua aplicação prática e relevância industrial/computacional. A introdução deve ser fundamentada em uma breve revisão da literatura, com referências a trabalhos correlatos e aplicações similares no formato ABNT ou IEEE.
2. **Modelagem Matemática:** Detalhe a formulação matemática proposta para a variação escolhida do problema. Defina formalmente os conjuntos, parâmetros e as variáveis de decisão. Explique o propósito e a lógica por trás da função objetivo e de cada uma das restrições do modelo.
3. **Solução via *Solvers* de Otimização:** Descreva a implementação computacional do modelo. Apresente e analise os resultados obtidos com os *solvers* (um comercial e um gratuito), incluindo as seguintes métricas:
   - Status da solução (ótima, factível, infactível).
   - Valor da função objetivo (número de caixas/custo total).
   - Tempo de processamento.
   - *Gap* de otimalidade (diferença percentual entre a melhor solução inteira e o *bound* do problema relaxado).

Realize uma análise comparativa, discutindo as diferenças de desempenho e de solução entre os *solvers*.

4. **Método de Solução Alternativo:** Apresente um método de solução alternativo (por exemplo, uma heurística clássica como FFD/BFD ou uma meta-heurística), justificando a escolha com base em referencial teórico. Descreva sua implementação e os resultados obtidos. Compare-os com a abordagem via *solvers*, realizando uma análise crítica sobre as diferenças, vantagens e a aplicabilidade de cada método.

3

5. **Conclusão:** Sintetizar as principais conclusões do trabalho. Discuta como a aplicação desenvolvida pode beneficiar a logística/indústria e aponte direções para trabalhos futuros (por exemplo, caixas com capacidades distintas, restrições 2D/3D ou abordagens híbridas). Por fim, apresente uma reflexão sobre os aprendizados e os desafios encontrados ao longo do desenvolvimento do projeto.

## Avaliação

O trabalho vale **10 pontos**, distribuídos da seguinte forma:

- **Modelagem Matemática (NM):** 3 pontos.
- **Implementação (NI):** 4 pontos (2 pontos *solver*, 2 pontos método alternativo).
- **Relatório (NR):** 3 pontos.
- **Apresentação (NA):** 1 ponto, nota individual.
- **Autoavaliação e Avaliação de Pares (NAAP):** 1 ponto, nota individual.

A nota final será:

$$NT = (NM + NI + NR) \cdot \min\{NA, NAAP\}$$

**Atenção:** Trabalhos iguais ou muito semelhantes entre grupos diferentes receberão nota zero.

4