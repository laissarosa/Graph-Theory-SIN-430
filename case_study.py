"""
case_study.py

Estudo de caso da parte 2: tempo médio do Dijkstra (vetor x heap) para k
origens aleatórias. As mesmas k origens são usadas nas duas implementações.
(A parte de distância e caminho mínimo entre vértices está comentada.)

Comandos para os grafos 4 e 5 (k = 2):
    python case_study.py grafos/grafo_W_4.txt --k 2 --seed 42 --saida resultado_g4
    python case_study.py grafos/grafo_W_5.txt --k 2 --seed 42 --saida resultado_g5

Se o vetor demorar demais, meça só o heap (o vetor aparece como n/d):
    python case_study.py grafos/grafo_W_4.txt --k 2 --seed 42 --saida resultado_g4 --sem-vetor
    python case_study.py grafos/grafo_W_5.txt --k 2 --seed 42 --saida resultado_g5 --sem-vetor

Saídas:
    <saida>/resultado_<nome_do_grafo>.txt   tempos e origens do grafo
    <saida>/tempos_medios.txt               tabela comparando os grafos da execução
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
    """Estudo de caso de caminho mínimo sobre um grafo ponderado."""

    # SOURCE = 10
    # TARGETS = (20, 30, 40, 50, 60)

    def __init__(self, graph: Graph, k: int, seed: Optional[int] = None):
        """
        As k origens são sorteadas uma única vez e reutilizadas nas duas
        implementações (vetor e heap), para que a comparação use as mesmas
        entradas.
        """
        self._search = GraphSearch(graph)
        n = graph.num_vertices
        self._sources = random.Random(seed).sample(range(1, n + 1), min(k, n))

    @property
    def sources(self) -> List[int]:
        return list(self._sources)

    # ---- Distância e caminho mínimo entre vértices (comentado) ----
    # def paths_from_source(self) -> List[Tuple[int, Optional[float], Optional[List[int]]]]:
    #     """Linhas (destino, distância, caminho) de SOURCE até cada TARGET."""
    #     tree = self._search.dijkstra(self.SOURCE)
    #     return [(t, tree["dist"].get(t),
    #              GraphSearch.path_from_parents(tree["parent"], t))
    #             for t in self.TARGETS]
    #
    # def paths_table(self) -> str:
    #     linhas = [f"{'destino':>8} {'distância':>12}  caminho"]
    #     for destino, d, caminho in self.paths_from_source():
    #         if d is None:
    #             linhas.append(f"{destino:>8} {'-':>12}  sem caminho")
    #         else:
    #             linhas.append(f"{destino:>8} {d:>12.6g}  {' -> '.join(map(str, caminho))}")
    #     return "\n".join(linhas)

    def _average_time(self, use_heap: bool) -> float:
        """Tempo médio, em segundos por execução, sobre as k origens."""
        inicio = time.perf_counter()
        for s in self._sources:
            self._search.dijkstra(s, use_heap)
        return (time.perf_counter() - inicio) / len(self._sources)

    @staticmethod
    def times_table(rows: List[Tuple[str, Optional[float], float]]) -> str:
        linhas = [f"{'grafo':<24} {'vetor (s)':>12} {'heap (s)':>12}"]
        for nome, tv, th in rows:
            vetor = f"{tv:>12.6f}" if tv is not None else f"{'n/d':>12}"
            linhas.append(f"{nome:<24} {vetor} {th:>12.6f}")
        return "\n".join(linhas)

    @staticmethod
    def _save(path: str, text: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"[salvo] {path}")

    @classmethod
    def main(cls) -> None:
        parser = argparse.ArgumentParser(description="Estudos de caso - parte 2.")
        parser.add_argument("grafos", nargs="+", help="Arquivos de grafos com pesos.")
        parser.add_argument("--k", type=int, default=100, help="Nº de origens aleatórias.")
        parser.add_argument("--seed", type=int, default=42, help="Semente do sorteio (padrão 42).")
        parser.add_argument("--saida", default="resultados",
                            help="Pasta onde os arquivos de resultado serão salvos.")
        parser.add_argument("--sem-vetor", action="store_true",
                            help="Mede só o heap (o vetor aparece como n/d).")
        args = parser.parse_args()

        os.makedirs(args.saida, exist_ok=True)

        tempos = []
        for caminho in args.grafos:
            nome = os.path.splitext(os.path.basename(caminho))[0]
            estudo = cls(AdjacencyListGraph.from_file(caminho), args.k, args.seed)

            # tabela_caminhos = estudo.paths_table()

            # O heap é medido primeiro e impresso na hora; o vetor pode demorar muito.
            th = estudo._average_time(True)
            print(f"[{nome}] heap: {th:.6f} s por execução (k = {len(estudo.sources)})", flush=True)
            tv = None if args.sem_vetor else estudo._average_time(False)
            tempos.append((nome, tv, th))

            relatorio = "\n".join([
                f"=== {nome}: tempo médio por execução de Dijkstra "
                f"(k = {len(estudo.sources)} origens, as mesmas nas duas versões) ===",
                cls.times_table([(nome, tv, th)]),
                "",
                f"Origens sorteadas (seed = {args.seed}):",
                " ".join(map(str, estudo.sources)),
            ])
            print(f"\n{relatorio}")
            cls._save(os.path.join(args.saida, f"resultado_{nome}.txt"), relatorio)

        tabela = cls.times_table(tempos)
        print("\n=== Tempo médio por execução de Dijkstra ===")
        print(tabela)
        cls._save(os.path.join(args.saida, "tempos_medios.txt"),
                  "=== Tempo médio por execução de Dijkstra ===\n" + tabela)


if __name__ == "__main__":
    ShortestPathStudy.main()