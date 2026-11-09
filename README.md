# Biblioteca de Grafos: SIN 430 (Teoria dos Grafos)

Biblioteca em Python para grafos **não direcionados**, com ou sem pesos nas arestas, desenvolvida para a disciplina SIN 430 – Teoria dos Grafos. Usa apenas a biblioteca padrão (Python 3.8 ou superior).

## Funcionalidades

**Parte 1**
- Leitura de grafos a partir de arquivo texto.
- Duas representações, à escolha de quem usa: **lista de adjacência** e **matriz de adjacência**.
- Estatísticas: número de vértices e de arestas, grau mínimo, máximo, médio e mediana.
- Buscas em **largura (BFS)** e em **profundidade (DFS)**, com a árvore de busca (pai e nível de cada vértice).
- Distância entre dois vértices (em número de arestas) e diâmetro (exato e aproximado).
- Componentes conexas, em ordem decrescente de tamanho.

**Parte 2**
- Grafos com **pesos** nas arestas (números reais).
- **Dijkstra** em duas versões, escritas a partir de um único laço principal:
  - com **vetor** (mínimo por varredura linear): O(n² + m);
  - com **heap binário com decrease-key**: O((n + m) log n).
- Distância e caminho mínimo de um vértice a todos os outros (árvore de caminhos mínimos).
- Estudos de caso: tempo médio do Dijkstra (vetor × heap) e caminhos mínimos.

## Estrutura do repositório

```
graph.py              classe abstrata Graph: leitura de arquivo, pesos, inserção de arestas
adjacency_list.py     AdjacencyListGraph (dicionário {vizinho: peso} por vértice)
adjacency_matrix.py   AdjacencyMatrixGraph (bytearray de existência + pesos à parte)
graph_search.py       GraphSearch: BFS, DFS, componentes, distância, diâmetro e Dijkstra
statistics_report.py  GraphStatistics: estatísticas e escrita dos resultados
main.py               programa de exemplo (linha de comando)
case_study.py         estudos de caso da Parte 2
grafos/               arquivos de entrada
```

## Formato do arquivo de entrada

A primeira linha tem o número de vértices. Cada linha seguinte é uma aresta, `u v` (sem peso) ou `u v peso` (com peso):

```
5
1 2 0.1
2 5 0.2
5 3 5
4 5 2.3
1 5 1
```

Regras de leitura:
- Os vértices são numerados de **1** a n.
- O arquivo é **todo com pesos ou todo sem pesos**: a primeira aresta define o formato, e misturar os dois gera erro.
- Em grafos sem pesos, cada aresta vale 1,0 (peso unitário).
- Se a mesma aresta aparece mais de uma vez, **vale a de menor peso**.
- Laços (`u u`) são ignorados, com um aviso.
- Pesos negativos são aceitos na leitura, mas o Dijkstra não os suporta: a biblioteca informa que ainda não implementa caminhos mínimos nesse caso.

## Como usar a biblioteca

```python
from adjacency_list import AdjacencyListGraph      # ou AdjacencyMatrixGraph
from graph_search import GraphSearch

grafo = AdjacencyListGraph.from_file("grafos/grafo_W_1.txt")
busca = GraphSearch(grafo)

arvore = busca.dijkstra(10)                    # com heap (padrão)
arvore = busca.dijkstra(10, use_heap=False)    # com vetor
dist, caminho = busca.shortest_path(10, 20)    # distância e caminho de 10 até 20

busca.bfs(1)                   # {'parent': ..., 'level': ...}
busca.dfs(1)
busca.connected_components()
busca.distance(10, 20)         # distância em arestas
busca.diameter()               # exato; diameter_approx() é a versão aproximada
```

Também é possível montar um grafo manualmente:

```python
grafo = AdjacencyListGraph(4)
grafo.add_edge(1, 2, 0.5)
grafo.add_edge(2, 3, 1.5)
```

## Executando pelo terminal

```
python main.py grafos/grafo_1.txt --repr list --saida resultado.txt --busca bfs --inicio 1 --distancia 10 20 --diametro exato
python main.py grafos/grafo_W_1.txt --saida resultado.txt --caminho-minimo 10 20 --dijkstra heap
```

| Opção | Descrição |
|---|---|
| `--repr list\|matrix` | representação do grafo (padrão: `list`) |
| `--saida ARQUIVO` | arquivo de saída com estatísticas e resultados |
| `--busca bfs\|dfs` e `--inicio V` | busca a partir de V (árvore escrita em arquivo próprio) |
| `--distancia U V` | distância em arestas entre U e V |
| `--diametro exato\|aprox` | diâmetro do grafo |
| `--caminho-minimo U V` | distância e caminho mínimo ponderado entre U e V |
| `--dijkstra heap\|vetor` | implementação do Dijkstra (padrão: `heap`) |

## Estudos de caso (Parte 2)

O `case_study.py` mede o tempo médio do Dijkstra com vetor e com heap para `k` origens sorteadas, as mesmas nas duas versões:

```
python case_study.py grafos/grafo_W_1.txt --k 100 --seed 42 --saida resultado_g1
python case_study.py grafos/grafo_W_4.txt --k 2 --seed 42 --saida resultado_g4 --sem-vetor
python case_study.py grafos/grafo_W_4.txt --k 2 --seed 42 --saida resultado_g4_vetor --sem-heap
```

| Opção | Descrição |
|---|---|
| `--k N` | número de origens aleatórias (padrão: 100) |
| `--seed N` | semente do sorteio (padrão: 42) |
| `--saida PASTA` | pasta dos resultados |
| `--sem-vetor` / `--sem-heap` | mede só uma das versões |

Em grafos grandes, o Dijkstra com vetor leva horas por origem, por isso as opções `--sem-vetor` e `--sem-heap` permitem medir cada versão separadamente.

## Decisões de projeto

- **Um único Dijkstra.** As duas versões diferem só em como guardam as distâncias e extraem o mínimo; o laço principal é o mesmo.
- **Heap com decrease-key eficiente.** Um vetor `pos[v]` guarda a posição de cada vértice no heap, e atualizar a chave custa O(log n) sem entradas repetidas.
- **Lista de adjacência com dicionário `{vizinho: peso}`**, em vez de um conjunto de vizinhos: o dicionário entrega vizinho e peso na mesma iteração e evita uma segunda estrutura só para os pesos.
- **Matriz com `bytearray` de existência e pesos à parte**, só para as arestas presentes. O peso 0,0 é válido, então não pode representar "sem aresta".
- **Estudos de caso com lista de adjacência**: na matriz, listar os vizinhos custa O(n), o que anularia a vantagem do heap.

## Complexidade

| Operação | Custo |
|---|---|
| BFS / DFS / componentes (por busca) | O(n + m) |
| Diâmetro exato | O(n · (n + m)) |
| Dijkstra com vetor | O(n² + m) |
| Dijkstra com heap | O((n + m) log n) |

## Autoras

- Laissa Rosa dos Santos
- Ana Flávia Tavares Alves
