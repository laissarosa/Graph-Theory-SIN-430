"""
graph.py

Classe abstrata Graph: estrutura de um grafo não-direcionado, opcionalmente
ponderado. Concentra o que independe da representação (leitura de arquivo,
validações, pesos, inserção de arestas, listagem de arestas). As subclasses
implementam apenas _get_weight, _set_weight, neighbors e weighted_neighbors. Os algoritmos ficam em
graph_search.py e as estatísticas em statistics_report.py.

Arestas sem peso explícito recebem peso 1.0.
"""

import math
from abc import ABC, abstractmethod
from typing import Iterator, List, Optional, Tuple


class Graph(ABC):
    """
    Vértices numerados de 1 a num_vertices, como no arquivo de entrada.

    is_weighted         -> True se alguma aresta foi inserida com peso explícito.
    has_negative_weight -> True se alguma aresta tem peso negativo.
    """

    def __init__(self, num_vertices: int):
        if num_vertices < 0:
            raise ValueError("Número de vértices não pode ser negativo.")
        self.num_vertices = num_vertices
        self.num_edges = 0
        self.is_weighted = False
        self.has_negative_weight = False

    # ---- Interface das representações concretas ----

    @abstractmethod
    def _get_weight(self, u: int, v: int) -> Optional[float]:
        """Peso da aresta {u, v}, ou None se ela não existe."""
        raise NotImplementedError

    @abstractmethod
    def _set_weight(self, u: int, v: int, weight: float) -> None:
        """Grava a aresta {u, v} com o peso dado (cria ou substitui)."""
        raise NotImplementedError

    @abstractmethod
    def neighbors(self, v: int) -> List[int]:
        """Vizinhos do vértice v."""
        raise NotImplementedError

    @abstractmethod
    def weighted_neighbors(self, v: int) -> List[Tuple[int, float]]:
        """Pares (vizinho, peso da aresta) do vértice v."""
        raise NotImplementedError

    # ---- Inserção de arestas (regra única para todas as representações) ----

    def add_edge(self, u: int, v: int, weight: Optional[float] = None) -> None:
        """
        Insere a aresta {u, v}. Se ela já existe, vale o menor peso
        (aresta sem peso conta como 1.0).
        """
        self.check_vertex(u)
        self.check_vertex(v)
        if u == v:
            raise ValueError("Laços (self-loops) não são permitidos.")
        atual = self._get_weight(u, v)
        candidato = 1.0 if weight is None else float(weight)
        if atual is not None and not candidato < atual:
            return
        peso = self._register_weight(weight)
        if atual is None:
            self.num_edges += 1
        self._set_weight(u, v, peso)

    def has_vertex(self, v: int) -> bool:
        return 1 <= v <= self.num_vertices

    def check_vertex(self, v: int) -> None:
        if not self.has_vertex(v):
            raise ValueError(f"Vértice {v} fora do intervalo [1, {self.num_vertices}].")

    def _register_weight(self, weight: Optional[float]) -> float:
        """Valida o peso, atualiza is_weighted/has_negative_weight e o devolve."""
        if weight is None:
            return 1.0
        weight = float(weight)
        if not math.isfinite(weight):
            raise ValueError("Peso de aresta deve ser um número real finito.")
        self.is_weighted = True
        if weight < 0:
            self.has_negative_weight = True
        return weight

    # ---- Construtor alternativo ----

    @classmethod
    def from_file(cls, filepath: str) -> "Graph":
        """
        Lê um grafo de arquivo texto e devolve uma instância da classe
        concreta que chamou o método (ex.: AdjacencyListGraph.from_file(...)).

        Formato: linha 1 = número de vértices; demais linhas = "u v" ou
        "u v peso" (peso: ponto flutuante qualquer). Laços são ignorados.
        Se a mesma aresta aparece mais de uma vez, vale o menor peso
        (aresta sem peso conta como 1.0).
        """
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = (line.strip() for line in f)
            lines = (line for line in raw_lines if line)

            try:
                num_vertices = int(next(lines))
            except StopIteration:
                raise ValueError("Arquivo de entrada vazio.")

            graph = cls(num_vertices)
            self_loops = 0

            for line_num, line in enumerate(lines, start=2):
                parts = line.split()
                if len(parts) not in (2, 3):
                    raise ValueError(
                        f"Linha {line_num} inválida: esperado 'u v' ou 'u v peso', "
                        f"obtido {line!r}."
                    )
                u, v = int(parts[0]), int(parts[1])
                peso = float(parts[2]) if len(parts) == 3 else None
                if u == v:
                    self_loops += 1
                    continue
                graph.add_edge(u, v, peso)

            if self_loops:
                print(f"Aviso: {self_loops} laço(s) em {filepath!r} foram ignorados.")

        return graph

    def edges(self) -> Iterator[Tuple[int, int, float]]:
        """Gera cada aresta uma única vez, como (u, v, peso) com u < v."""
        for u in range(1, self.num_vertices + 1):
            for v, peso in self.weighted_neighbors(u):
                if u < v:
                    yield (u, v, peso)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(num_vertices={self.num_vertices}, "
                f"num_edges={self.num_edges})")
