"""
adjacency_matrix.py

Implementação de grafo não-direcionado (com ou sem pesos) usando matriz de adjacência.
"""

from typing import Dict, List, Optional, Tuple

from graph import Graph


class AdjacencyMatrixGraph(Graph):
    """Representação de grafo por matriz de adjacência."""

    def __init__(self, num_vertices: int):
        super().__init__(num_vertices)
        n = num_vertices + 1
        # _matrix[u][v] == 1 se existe aresta {u, v}. Um peso 0.0 é válido,
        # por isso a existência da aresta não pode ser inferida do peso.
        self._matrix: List[bytearray] = [bytearray(n) for _ in range(n)]
        # Pesos só das arestas existentes, com chave (min(u, v), max(u, v)).
        self._weights: Dict[Tuple[int, int], float] = {}

    @staticmethod
    def _key(u: int, v: int) -> Tuple[int, int]:
        return (u, v) if u < v else (v, u)

    def _get_weight(self, u: int, v: int) -> Optional[float]:
        if not self._matrix[u][v]:
            return None
        return self._weights[self._key(u, v)]

    def _set_weight(self, u: int, v: int, weight: float) -> None:
        self._matrix[u][v] = 1
        self._matrix[v][u] = 1
        self._weights[self._key(u, v)] = weight

    def neighbors(self, v: int) -> List[int]:
        self.check_vertex(v)
        row = self._matrix[v]
        return [w for w in range(1, self.num_vertices + 1) if row[w]]

    def weighted_neighbors(self, v: int) -> List[Tuple[int, float]]:
        self.check_vertex(v)
        row = self._matrix[v]
        pesos = self._weights
        return [
            (w, pesos[self._key(v, w)])
            for w in range(1, self.num_vertices + 1)
            if row[w]
        ]
