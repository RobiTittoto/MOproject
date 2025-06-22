import random
from creazione_problema import Graph, Node, Link
import numpy as np

from m_v_problem import modello


def generate_random_graph(num_nodes: int, num_links: int) -> Graph:
    """
    Generates a random graph with the given number of nodes and links.

    Parameters:
        num_nodes (int): Number of nodes in the graph
        num_links (int): Number of links in the graph

    Returns:
        Graph: A randomly generated graph instance
    """
    # Create empty graph
    g = Graph()

    # Add nodes
    nodes = [g.add_node() for _ in range(num_nodes)]

    # Generate random links
    for _ in range(num_links):
        # Randomly select origin and destination (must be different)
        origin, destination = random.sample(nodes, 2)

        # Generate random parameters
        mu = random.uniform(10, 30)
        sigma = random.uniform(0.1 * mu, 0.3 * mu)

        # Create link with empty rho dictionary (will be populated later)
        link = g.add_link(origin, destination, mu, sigma)

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


def main():
    # Example usage
    num_nodes = 4
    num_links = 4

    # Generate random graph
    random_graph = generate_random_graph(num_nodes, num_links)

    # Print graph information
    print(f"Generated graph with {random_graph.nodes_number} nodes and {random_graph.link_number} links:")
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

    modello(random_graph, 1, 4)
if __name__ == "__main__":
    main()