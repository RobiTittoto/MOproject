"""
Questo file definisce un insieme di classi per la modellazione di grafi orientati con proprietà stocastiche.

Classi:

Classe Graph:
    - nodes (list[Node]) -> Lista dei nodi del grafo
    - nodes_number (int) -> Numero totale di nodi
    - link (list[Link]) -> Lista degli archi (link) del grafo
    - link_number (int) -> Numero totale di archi

Classe Link:
    - origin (Node) -> Nodo di origine dell'arco
    - destination (Node) -> Nodo di destinazione dell'arco
    - mu (float) -> Media del tempo stocastico di attraversamento dell'arco
    - sigma (float) -> Deviazione standard del tempo di attraversamento stocastico
    - rho (dict[Link, float]) -> Coefficiente di correlazione con ogni altro arco

Classe Node:
    - label (int) -> Numero nodo
    - input (list[Link]) -> Lista degli archi entranti nel nodo
    - output (list[Link]) -> Lista degli archi uscenti dal nodo
"""
from typing import List, Dict, Optional
import numpy as np

class Node:
    def __init__(self, label: int):
        self.label: int = label
        self.input: List['Link'] = []
        self.output: List['Link'] = []

    def __repr__(self):
        return f"Node({self.label})"


class Link:
    def __init__(self, origin: Node, destination: Node, mu: float, sigma: float, label: int):
        self.origin: Node = origin
        self.destination: Node = destination
        self.mu: float = mu
        self.sigma: float = sigma
        self.rho: Dict['Link', float] = {}
        self.label: int = label

        origin.output.append(self)
        destination.input.append(self)

    def __repr__(self):
        return (f"Link(from=Node({self.origin.label}), "
                f"to=Node({self.destination.label}), mu={self.mu}, sigma={self.sigma})")

class Hyperlink:
    def __init__(self, link_a: Link, link_b: Link, rho: float):
        self.link_a: Link = link_a
        self.link_b: Link = link_b

class Graph:
    def __init__(self):
        self.nodes: List[Node] = []
        self.link: List[Link] = []
    @property
    def nodes_number(self) -> int:
        return len(self.nodes)

    @property
    def link_number(self) -> int:
        return len(self.link)

    def add_node(self) -> Node:
        label = len(self.nodes) + 1  # Inizia da 1
        node = Node(label)
        self.nodes.append(node)
        return node

    def add_link(self, origin: Node, destination: Node, mu: float, sigma: float) -> Link:
        label = len(self.link) + 1
        link = Link(origin, destination, mu, sigma,label)
        self.link.append(link)
        return link

    def get_hyperlink(self):
        hyperlinks = dict()

        for link_a in self.link:
            for link_b in self.link:
                hyperlinks[link_a, link_b] = Hyperlink(link_a, link_b, link_a.rho.get(link_b))

        return hyperlinks

    @classmethod
    def from_incidence_matrix(cls, matrix: List[List[int]],
                              mu_list: Optional[List[float]] = None,
                              sigma_list: Optional[List[float]] = None) -> 'Graph':

        # --- Validazione degli input ---
        if not matrix or not all(isinstance(row, list) for row in matrix):
            raise ValueError("La matrice di incidenza deve essere una lista di liste non vuota.")

        num_nodes = len(matrix)
        num_links = len(matrix[0])

        if any(len(row) != num_links for row in matrix):
            raise ValueError("Tutte le righe della matrice devono avere lo stesso numero di colonne.")

        if mu_list is not None and len(mu_list) != num_links:
            raise ValueError(
                "La lista mu_list deve avere lo stesso numero di elementi degli archi (colonne della matrice).")

        if sigma_list is not None and len(sigma_list) != num_links:
            raise ValueError(
                "La lista sigma_list deve avere lo stesso numero di elementi degli archi (colonne della matrice).")

        for j in range(num_links):
            column = [matrix[i][j] for i in range(num_nodes)]
            if column.count(-1) != 1 or column.count(1) != 1:
                raise ValueError(
                    f"La colonna {j} deve contenere esattamente un -1 e un 1 (origine e destinazione dell'arco).")

        # --- Costruzione del grafo ---
        g = cls()
        nodes = [g.add_node() for _ in range(num_nodes)]

        for j in range(num_links):
            origin_idx = destination_idx = None
            for i in range(num_nodes):
                if matrix[i][j] == -1:
                    origin_idx = i
                elif matrix[i][j] == 1:
                    destination_idx = i

            mu = mu_list[j] if mu_list else 0.0
            sigma = sigma_list[j] if sigma_list else 0.0

            g.add_link(nodes[origin_idx], nodes[destination_idx], mu, sigma)

        return g

    def __repr__(self):
        return f"Graph(nodes={self.nodes_number}, links={self.link_number})"

class Travel:
    def __init__(self, origin: Node, destination: Node):
        self.origin: Node = origin
        self.destination: Node = destination



incidence_matrix = [
    [-1,  0,  0, 0],
    [ 1, -1,  -1, 0],
    [ 0,  1, 1, -1],
    [ 0,  0,  0, 1]
]

mu_list = [1.0, 2.0, 3.0, 4.0]
sigma_list = [0.1, 0.2, 0.3, 0.4]

g = Graph.from_incidence_matrix(incidence_matrix, mu_list, sigma_list)

print(g)
for l in g.link:
    print(l)
