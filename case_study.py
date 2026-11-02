"""
case_study.py

Estudos de caso da parte 2:
  1. distância e caminho mínimo de 10 até 20, 30, 40, 50, 60;
  2. tempo médio do Dijkstra (vetor x heap) para k origens aleatórias.

Uso:
    python case_study.py grafos/grafo_W_1.txt grafos/grafo_W_2.txt --k 100 --seed 42
"""

import argparse
import os
import random
import time
from typing import List, Optional, Tuple

from adjacency_list import AdjacencyListGraph
from graph import Graph
from graph_search import GraphSearch


class ShortestPathStudy:
    """Estudos de caso de caminho mínimo sobre um grafo ponderado."""

    SOURCE = 10
    TARGETS = (20, 30, 40, 50, 60)

    def __init__(self, graph: Graph, k: int, k_vector: Optional[int] = None,
                 seed: Optional[int] = None):
        """
        As k origens são sorteadas uma vez e reutilizadas nas duas
        implementações, para que a comparação use as mesmas entradas.
        k_vector (opcional) limita as origens do Dijkstra com vetor, que é
        O(n^2) e pode ser inviável em grafos grandes.
        """
        self._search = GraphSearch(graph)
        n = graph.num_vertices
        self._sources = random.Random(seed).sample(range(1, n + 1), min(k, n))
        self._k_vector = min(k_vector or k, len(self._sources))

    def paths_from_source(self) -> List[Tuple[int, Optional[float], Optional[List[int]]]]:
        """Linhas (destino, distância, caminho) de SOURCE até cada TARGET."""
        tree = self._search.dijkstra(self.SOURCE)
        return [(t, tree["dist"].get(t),
                 GraphSearch.path_from_parents(tree["parent"], t))
                for t in self.TARGETS]

    def paths_table(self) -> str:
        linhas = [f"{'destino':>8} {'distância':>12}  caminho"]
        for destino, d, caminho in self.paths_from_source():
            if d is None:
                linhas.append(f"{destino:>8} {'-':>12}  sem caminho")
            else:
                linhas.append(f"{destino:>8} {d:>12.6g}  {' -> '.join(map(str, caminho))}")
        return "\n".join(linhas)

    def average_times(self) -> Tuple[float, float]:
        """(tempo médio com vetor, tempo médio com heap), em segundos por execução."""
        return (self._average_time(False, self._sources[:self._k_vector]),
                self._average_time(True, self._sources))

    def _average_time(self, use_heap: bool, sources: List[int]) -> float:
        inicio = time.perf_counter()
        for s in sources:
            self._search.dijkstra(s, use_heap)
        return (time.perf_counter() - inicio) / len(sources)

    @staticmethod
    def times_table(rows: List[Tuple[str, float, float]]) -> str:
        linhas = [f"{'grafo':<24} {'vetor (s)':>12} {'heap (s)':>12}"]
        linhas += [f"{nome:<24} {tv:>12.6f} {th:>12.6f}" for nome, tv, th in rows]
        return "\n".join(linhas)

    @classmethod
    def main(cls) -> None:
        parser = argparse.ArgumentParser(description="Estudos de caso - parte 2.")
        parser.add_argument("grafos", nargs="+", help="Arquivos de grafos com pesos.")
        parser.add_argument("--k", type=int, default=100, help="Nº de origens aleatórias.")
        parser.add_argument("--k-vetor", type=int, dest="k_vetor",
                            help="Nº de origens para o Dijkstra com vetor (padrão: k).")
        parser.add_argument("--seed", type=int, help="Semente do sorteio.")
        args = parser.parse_args()

        tempos = []
        for caminho in args.grafos:
            nome = os.path.splitext(os.path.basename(caminho))[0]
            estudo = cls(AdjacencyListGraph.from_file(caminho), args.k, args.k_vetor, args.seed)
            print(f"\n=== {nome}: caminhos mínimos a partir de {cls.SOURCE} ===")
            print(estudo.paths_table())
            tempos.append((nome, *estudo.average_times()))

        print("\n=== Tempo médio por execução de Dijkstra ===")
        print(cls.times_table(tempos))


if __name__ == "__main__":
    ShortestPathStudy.main()
