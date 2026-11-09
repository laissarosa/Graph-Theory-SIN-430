"""
statistics_report.py

Cálculo e escrita das estatísticas de um grafo (graus, pesos, componentes
conexas), além da escrita em arquivo dos resultados de consultas pontuais
(distância, diâmetro, caminho mínimo), dos tempos de execução e da árvore de
busca.
"""

from statistics import median
from typing import Dict, List, Optional

from graph import Graph


class GraphStatistics:
    """
    Estatísticas de um Graph e escrita do relatório. As componentes conexas
    são calculadas por GraphSearch.connected_components() e recebidas prontas.
    """

    def __init__(self, graph: Graph, components: List[List[int]]):
        self.graph = graph
        self._components = components
        self._degrees: List[int] = [self.degree(v) for v in range(1, graph.num_vertices + 1)]

    # ---- Estatísticas de grau ----

    def degree(self, v: int) -> int:
        """Grau do vértice v (número de vizinhos)."""
        return len(self.graph.neighbors(v))

    @property
    def num_vertices(self) -> int:
        return self.graph.num_vertices

    @property
    def num_edges(self) -> int:
        return self.graph.num_edges

    @property
    def min_degree(self) -> int:
        return min(self._degrees, default=0)

    @property
    def max_degree(self) -> int:
        return max(self._degrees, default=0)

    @property
    def avg_degree(self) -> float:
        return sum(self._degrees) / len(self._degrees) if self._degrees else 0.0

    @property
    def median_degree(self) -> float:
        return median(self._degrees) if self._degrees else 0.0

    # ---- Estatísticas de peso ----

    @property
    def min_weight(self) -> Optional[float]:
        return min((w for _, _, w in self.graph.edges()), default=None)

    @property
    def max_weight(self) -> Optional[float]:
        return max((w for _, _, w in self.graph.edges()), default=None)

    # ---- Componentes conexas ----

    @property
    def num_components(self) -> int:
        return len(self._components)

    @property
    def components(self) -> List[List[int]]:
        """Vértices de cada componente, em ordem decrescente de tamanho."""
        return self._components

    @property
    def component_sizes(self) -> List[int]:
        return [len(c) for c in self._components]

    # ---- Relatório de estatísticas ----

    def as_text(self) -> str:
        """Relatório de estatísticas formatado."""
        lines = [
            f"Número de vértices: {self.num_vertices}",
            f"Número de arestas: {self.num_edges}",
            f"Grau mínimo: {self.min_degree}",
            f"Grau máximo: {self.max_degree}",
            f"Grau médio: {self.avg_degree:.4f}",
            f"Mediana de grau: {self.median_degree}",
        ]
        if self.graph.is_weighted:
            lines.append(f"Grafo com pesos: sim (peso mínimo: {self.min_weight}, "
                         f"peso máximo: {self.max_weight})")
            if self.graph.has_negative_weight:
                lines.append("Aviso: há arestas com peso negativo (Dijkstra não aplicável).")
        lines += ["", f"Número de componentes conexas: {self.num_components}"]
        for i, componente in enumerate(self.components, start=1):
            vertices = ", ".join(str(v) for v in sorted(componente))
            lines.append(f"  Componente {i}: {len(componente)} vértice(s) — [{vertices}]")
        lines.append("")
        return "\n".join(lines)

    def write_to_file(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.as_text())

    # ---- Resultados de consultas, acrescentados ao arquivo de saída ----

    def write_distance_report(self, u: int, v: int, d: Optional[int], filepath: str) -> None:
        """Acrescenta a distância (em arestas) entre u e v."""
        if d is None:
            texto = f"Não há caminho entre {u} e {v} (vértices em componentes diferentes).\n"
        else:
            texto = f"Distância entre {u} e {v}: {d}\n"
        self._append(filepath, "\n" + texto)

    def shortest_path_text(self, u: int, v: int, d: Optional[float],
                           caminho: Optional[List[int]]) -> str:
        """Formata a distância e o caminho mínimo ponderado entre u e v."""
        if d is None:
            return f"Não há caminho entre {u} e {v} (vértices em componentes diferentes).\n"
        return (f"Distância mínima ponderada entre {u} e {v}: {d:.6g}\n"
                f"Caminho mínimo: {' -> '.join(map(str, caminho))}\n")

    def write_shortest_path_report(self, u: int, v: int, d: Optional[float],
                                   caminho: Optional[List[int]], filepath: str) -> None:
        """Acrescenta a distância e o caminho mínimo ponderado entre u e v."""
        self._append(filepath, "\n" + self.shortest_path_text(u, v, d, caminho))

    def write_diameter_report(self, diametro: int, tipo: str, filepath: str) -> None:
        """Acrescenta o diâmetro ('exato' ou 'aprox')."""
        self._append(filepath, f"\nDiâmetro ({tipo}): {diametro}\n")

    def write_time(self, filepath: str, descricao: str, segundos: float) -> None:
        """Acrescenta uma linha com o tempo de execução de uma operação."""
        self._append(filepath, f"{descricao}: {segundos:.6f} segundos\n")

    # ---- Árvore de busca (arquivo separado, formato tabular) ----

    @staticmethod
    def write_search_tree(result: Dict, filepath: str) -> None:
        """Escreve a árvore de busca (BFS/DFS): vértice, pai e nível."""
        parent, level = result["parent"], result["level"]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("vertice pai nivel\n")
            for v in sorted(parent):
                pai = "-" if parent[v] is None else parent[v]
                f.write(f"{v} {pai} {level[v]}\n")

    @staticmethod
    def _append(filepath: str, texto: str) -> None:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(texto)
