import instance_generator
import logger
import mv_problem

def main(num_nodes, origin, destination, log: bool):

    logger.LOG_ENABLED = log

    if num_nodes < origin or num_nodes < destination or origin == destination:
        return

    # Generate random connected graph
    random_graph = instance_generator.generate_connected_graph(num_nodes)

    # Print graph information
    logger.log(f"\nGenerated graph with {random_graph.nodes_number} nodes and {random_graph.links_number} links:")
    logger.log(random_graph)

    # Print node details
    logger.log("\nNodes:")
    for node in random_graph.nodes:
        logger.log(f"{node}:")
        logger.log(f"  Input links: {[l.label for l in node.input]}")
        logger.log(f"  Output links: {[l.label for l in node.output]}")

    # Print link details
    logger.log("\nLinks:")
    for link in random_graph.links:
        logger.log(f"Link {link.label}: {link}")
        logger.log(f"  mu: {link.mu:.2f}, sigma: {link.sigma:.2f}")
        logger.log(f"  Correlations (sample):")
        # Print up to 3 correlation values
        printed = 0
        for other_link, rho in link.rho.items():
            if other_link != link and printed < 3:
                logger.log(f"    with Link {other_link.label}: {rho:.2f}")
                printed += 1
    if log:
        instance_generator.draw_graph(random_graph)

    # Assuming modello is a function that processes the graph
    travel = mv_problem.resolve_mv_problem(random_graph, origin, destination, log)
    for link in travel.links:
        print(link.label)

if __name__ == "__main__":
    main(num_nodes = 5,origin=1,destination=5, log=True)