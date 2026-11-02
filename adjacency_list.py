"""
adjacency_list.py

Implementação de grafo não-direcionado (com ou sem pesos) usando lista de adjacência.
"""

from typing import Dict, List, Optional, Tuple

from graph import Graph


class AdjacencyListGraph(Graph):
    """
    Lista em que cada posição contém um dicionário {vizinho: peso}.
    O dicionário garante a unicidade das arestas e guarda o peso de cada uma.
    """

    def __init__(self, num_vertices: int):
        super().__init__(num_vertices)
        # Índice 0 não é usado: vértices vão de 1 a num_vertices.
        self._adj: List[Dict[int, float]] = [dict() for _ in range(num_vertices + 1)]

    def _get_weight(self, u: int, v: int) -> Optional[float]:
        return self._adj[u].get(v)

    def _set_weight(self, u: int, v: int, weight: float) -> None:
        self._adj[u][v] = weight
        self._adj[v][u] = weight

    def neighbors(self, v: int) -> List[int]:
        self.check_vertex(v)
        return list(self._adj[v])

    def weighted_neighbors(self, v: int) -> List[Tuple[int, float]]:
        self.check_vertex(v)
        return list(self._adj[v].items())
