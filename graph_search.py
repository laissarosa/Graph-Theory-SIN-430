"""
graph_search.py

Classe GraphSearch: todas as buscas e algoritmos construídos sobre elas
(BFS, DFS, Dijkstra, componentes conexas, distância e diâmetro). Recebe um
Graph e usa apenas a sua interface pública, então funciona com qualquer
representação.
"""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from graph import Graph


class GraphSearch:
    """Buscas e caminhos mínimos sobre um Graph."""

    INF = float("inf")

    def __init__(self, graph: Graph):
        self._graph = graph

    # ---- Buscas sem pesos ----

    def bfs(self, start: int) -> Dict:
        """
        Busca em largura (ignora pesos). Retorna {'parent': ..., 'level': ...}
        apenas com os vértices alcançáveis de start (pai da raiz = None).
        """
        g = self._graph
        g.check_vertex(start)
        parent: Dict[int, Optional[int]] = {start: None}
        level: Dict[int, int] = {start: 0}
        queue = deque([start])

        while queue:
            u = queue.popleft()
            for w in g.neighbors(u):
                if w not in level:
                    level[w] = level[u] + 1
                    parent[w] = u
                    queue.append(w)

        return {"parent": parent, "level": level}

    def dfs(self, start: int) -> Dict:
        """Busca em profundidade iterativa (evita o limite de recursão do Python)."""
        g = self._graph
        g.check_vertex(start)
        parent: Dict[int, Optional[int]] = {start: None}
        level: Dict[int, int] = {start: 0}
        visited: Set[int] = set()
        stack = [start]

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            for w in g.neighbors(u):
                if w not in parent:
                    parent[w] = u
                    level[w] = level[u] + 1
                if w not in visited:
                    stack.append(w)

        return {"parent": parent, "level": level}

    # ---- Algoritmos construídos sobre a BFS ----

    def connected_components(self) -> List[List[int]]:
        """Componentes conexas, da maior para a menor."""
        visited: Set[int] = set()
        components: List[List[int]] = []

        for v in range(1, self._graph.num_vertices + 1):
            if v not in visited:
                component = list(self.bfs(v)["level"])
                visited.update(component)
                components.append(component)

        components.sort(key=len, reverse=True)
        return components

    def distance(self, u: int, v: int) -> Optional[int]:
        """Distância em número de arestas (BFS, ignora pesos); None se não há caminho."""
        self._graph.check_vertex(u)
        self._graph.check_vertex(v)
        return self.bfs(u)["level"].get(v)

    def diameter(self) -> int:
        """Diâmetro exato: maior distância (em arestas) entre vértices conectados."""
        return max(max(self.bfs(v)["level"].values())
                   for v in range(1, self._graph.num_vertices + 1))

    def diameter_approx(self) -> int:
        """Diâmetro aproximado com duas BFS (limite inferior do valor exato)."""
        nivel_a = self.bfs(1)["level"]
        a = max(nivel_a, key=nivel_a.get)
        return max(self.bfs(a)["level"].values())

    # ---- Caminhos mínimos ponderados ----

    def dijkstra(self, start: int, use_heap: bool = True) -> Dict:
        """
        Dijkstra a partir de start, com heap (use_heap=True) ou com vetor.
        O laço principal é o mesmo nos dois casos.

        Retorna {'dist': {v: distância}, 'parent': {v: pai}} apenas com os
        vértices alcançáveis (a árvore de caminhos mínimos).
        Lança ValueError se houver peso negativo.
        """
        g = self._graph
        g.check_vertex(start)
        if g.has_negative_weight:
            raise ValueError(
                "O grafo possui arestas com peso negativo: a biblioteca ainda "
                "não implementa caminhos mínimos nesse caso."
            )

        n = g.num_vertices
        dist: List[float] = [self.INF] * (n + 1)  # índice 0 não é usado
        parent: List[Optional[int]] = [None] * (n + 1)

        if use_heap:
            heap: List[int] = []
            pos: List[int] = [-1] * (n + 1)
            pop_min = lambda: self._heap_pop(dist, heap, pos)
            decrease = lambda v, d: self._heap_decrease(dist, heap, pos, v, d)
        else:
            done: List[bool] = [False] * (n + 1)
            pop_min = lambda: self._vector_pop(dist, done)
            decrease = dist.__setitem__

        decrease(start, 0.0)
        while (item := pop_min()) is not None:
            u, d = item
            for w, peso in g.weighted_neighbors(u):
                nova = d + peso
                if nova < dist[w]:
                    decrease(w, nova)
                    parent[w] = u

        alcancaveis = {v: d for v, d in enumerate(dist) if d < self.INF}
        return {"dist": alcancaveis, "parent": {v: parent[v] for v in alcancaveis}}

    def shortest_path(self, u: int, v: int, use_heap: bool = True) -> Tuple[Optional[float], Optional[List[int]]]:
        self._graph.check_vertex(v)
        tree = self.dijkstra(u, use_heap)
        if v not in tree["dist"]:
            return None, None
        return tree["dist"][v], self.path_from_parents(tree["parent"], v)

    @staticmethod
    def path_from_parents(parent: Dict[int, Optional[int]],
                          target: int) -> Optional[List[int]]:
        """Reconstrói o caminho raiz -> target a partir do mapa de pais."""
        if target not in parent:
            return None
        caminho: List[int] = []
        atual: Optional[int] = target
        while atual is not None:
            caminho.append(atual)
            atual = parent[atual]
        caminho.reverse()
        return caminho

    # ---- Dijkstra com vetor: mínimo por varredura linear ----

    @staticmethod
    def _vector_pop(dist: List[float], done: List[bool]) -> Optional[Tuple[int, float]]:
        """Remove e devolve (v, dist) do vértice não finalizado de menor estimativa."""
        melhor, u = GraphSearch.INF, -1
        for v in range(1, len(dist)):
            if not done[v] and dist[v] < melhor:
                melhor, u = dist[v], v
        if u == -1:  # os restantes são inalcançáveis
            return None
        done[u] = True
        return u, melhor

    # ---- Dijkstra com heap: heap binário com decrease-key ----
    # heap guarda vértices; pos[v] é a posição de v no heap (-1 se ausente).
    # Com pos, diminuir a chave de v custa O(log n), sem entradas repetidas.

    @staticmethod
    def _heap_decrease(dist: List[float], heap: List[int], pos: List[int], v: int, new_dist: float) -> None:
        dist[v] = new_dist
        if pos[v] == -1:  # ainda não está no heap: insere no fim
            heap.append(v)
            pos[v] = len(heap) - 1
        GraphSearch._sift_up(dist, heap, pos, pos[v])

    @staticmethod
    def _heap_pop(dist: List[float], heap: List[int], pos: List[int]) -> Optional[Tuple[int, float]]:
        if not heap:
            return None
        topo = heap[0]
        ultimo = heap.pop()
        pos[topo] = -1
        if heap:
            heap[0] = ultimo
            pos[ultimo] = 0
            GraphSearch._sift_down(dist, heap, pos, 0)
        return topo, dist[topo]

    @staticmethod
    def _sift_up(dist: List[float], heap: List[int], pos: List[int], i: int) -> None:
        v = heap[i]
        dv = dist[v]
        while i > 0:
            pai = (i - 1) // 2
            vp = heap[pai]
            if dist[vp] <= dv:
                break
            heap[i] = vp
            pos[vp] = i
            i = pai
        heap[i] = v
        pos[v] = i

    @staticmethod
    def _sift_down(dist: List[float], heap: List[int], pos: List[int], i: int) -> None:
        tamanho = len(heap)
        v = heap[i]
        dv = dist[v]
        while True:
            filho = 2 * i + 1
            if filho >= tamanho:
                break
            if filho + 1 < tamanho and dist[heap[filho + 1]] < dist[heap[filho]]:
                filho += 1
            vf = heap[filho]
            if dist[vf] >= dv:
                break
            heap[i] = vf
            pos[vf] = i
            i = filho
        heap[i] = v
        pos[v] = i
