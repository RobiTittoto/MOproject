import random
import matplotlib.pyplot as plt
import networkx as nx
from framework.graph_classes import Graph


def generate_connected_graph(num_nodes: int) -> Graph:
    """
    Generates a connected graph where each node has at least one incoming and one outgoing link.
    The total number of links will be at least num_nodes to ensure connectivity.

    Parameters:
        num_nodes (int): Number of nodes in the graph

    Returns:
        Graph: A randomly generated connected graph instance
    """
    if num_nodes < 2:
        raise ValueError("Number of nodes must be at least 2")

    # Create empty graph
    g = Graph()

    # Add nodes
    nodes = [g.add_node() for _ in range(num_nodes)]

    # Step 1: Create a cycle to ensure each node has at least one incoming and one outgoing link
    # Shuffle the nodes to create a random cycle
    shuffled_nodes = random.sample(nodes, len(nodes))

    for i in range(len(shuffled_nodes)):
        origin = shuffled_nodes[i]
        destination = shuffled_nodes[(i + 1) % len(shuffled_nodes)]

        # Generate random parameters
        mu = random.uniform(10, 30)
        sigma = random.uniform(0.1 * mu, 0.3 * mu)

        g.add_link(origin, destination, mu, sigma)

    # Step 2: Add additional random links to increase connectivity
    # We'll add at least num_nodes//2 more links
    additional_links = max(num_nodes // 2, 1) # max(num_nodes // 2, 1)

    for _ in range(additional_links):
        # Randomly select origin and destination (must be different)
        origin, destination = random.sample(nodes, 2)

        # Generate random parameters
        mu = random.uniform(10, 30)
        sigma = random.uniform(0.1 * mu, 0.3 * mu)

        g.add_link(origin, destination, mu, sigma)

    # Generate correlation coefficients (rho) between links
    for i, link_a in enumerate(g.links):
        for j, link_b in enumerate(g.links):
            if i == j:
                link_a.rho[link_b] = 1.0  # Perfect correlation with itself
            elif j > i:  # Only calculate once per pair
                # Generate random correlation between 0 and 1
                # Using triangular distribution to get more values near 0.5
                rho = random.triangular(0, 1, 0.5)

                # Ensure symmetry (rho_ab = rho_ba)
                link_a.rho[link_b] = rho
                link_b.rho[link_a] = rho

    return g


def draw_graph(graph: Graph):
    """
    Visualizza il grafo utilizzando networkx e matplotlib.

    Args:
        graph (Graph): Il grafo da visualizzare
    """
    # Crea un grafo diretto networkx
    G = nx.DiGraph()

    # Aggiungi nodi
    for node in graph.nodes:
        G.add_node(node.label)

    # Aggiungi archi con attributi
    for link in graph.links:
        G.add_edge(link.origin.label,
                   link.destination.label,
                   label=str(link.label))  # Usiamo il label dell'arco

    # Disegna il grafo
    pos = nx.spring_layout(G)  # Posizionamento dei nodi
    plt.figure(figsize=(10, 8))

    # Disegna nodi
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')

    # Disegna etichette dei nodi
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    # Disegna archi
    edges = G.edges()
    nx.draw_networkx_edges(G, pos, edgelist=edges,
                           arrowstyle='->', arrowsize=20,
                           edge_color='gray')

    # Aggiungi etichette agli archi (solo il numero/label dell'arco)
    edge_labels = nx.get_edge_attributes(G, 'label')

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=12, font_weight='bold')

    plt.title("Grafo Orientato")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

