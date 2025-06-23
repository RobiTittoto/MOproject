import random
from creazione_problema import Graph, Node, Link
import numpy as np

from m_v_problem import modello


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
    additional_links = max(num_nodes // 2, 1)

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


import matplotlib.pyplot as plt
import networkx as nx
from creazione_problema import Graph, Node, Link


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
                   mu=f"{link.mu:.1f}",
                   sigma=f"{link.sigma:.1f}")

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

    # Aggiungi etichette agli archi (mu ± sigma)
    edge_labels = {}
    for (u, v, d) in G.edges(data=True):
        edge_labels[(u, v)] = f"μ={d['mu']}\nσ={d['sigma']}"

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=9, label_pos=0.3)

    plt.title("Grafo Orientato con Proprietà Stocastiche")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main(num_nodes):
    # Example usage
    #num_nodes = int(input("Enter the number of nodes (minimum 2): "))

    # Generate random connected graph
    random_graph = generate_connected_graph(num_nodes)

    # Print graph information
    print(f"\nGenerated graph with {random_graph.nodes_number} nodes and {random_graph.links_number} links:")
    print(random_graph)

    # Print node details
    print("\nNodes:")
    for node in random_graph.nodes:
        print(f"{node}:")
        print(f"  Input links: {[l.label for l in node.input]}")
        print(f"  Output links: {[l.label for l in node.output]}")

    # Print link details
    print("\nLinks:")
    for link in random_graph.links:
        print(f"Link {link.label}: {link}")
        print(f"  mu: {link.mu:.2f}, sigma: {link.sigma:.2f}")
        print(f"  Correlations (sample):")
        # Print up to 3 correlation values
        printed = 0
        for other_link, rho in link.rho.items():
            if other_link != link and printed < 3:
                print(f"    with Link {other_link.label}: {rho:.2f}")
                printed += 1
    draw_graph(random_graph)

    # Assuming modello is a function that processes the graph
    modello(random_graph, 1, num_nodes)



if __name__ == "__main__":
    main(num_nodes=4)