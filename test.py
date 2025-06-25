import copy

from framework import logger, instance_generator, mv_problem, ms_problem


def main(num_nodes, origin, destination, log: bool):

    logger.LOG_ENABLED = log

    if num_nodes < origin or num_nodes < destination or origin == destination:
        return

    # Generazione grafo randomico
    graph = instance_generator.generate_connected_graph(num_nodes)

    #Stampa informazioni sul grafo
    logger.log(f"\nGenerated graph with {graph.nodes_number} nodes and {graph.links_number} links:")
    logger.log(graph)

    # Stampa informzioni sui nodi
    logger.log("\nNodes:")
    for node in graph.nodes:
        logger.log(f"{node}:")
        logger.log(f"  Input links: {[l.label for l in node.input]}")
        logger.log(f"  Output links: {[l.label for l in node.output]}")

    # Stampa informazioni archi
    logger.log("\nLinks:")
    for link in graph.links:
        logger.log(f"Link {link.label}: {link}")
        logger.log(f"  mu: {link.mu:.2f}, sigma: {link.sigma:.2f}")
        logger.log(f"  Correlations (sample):")
        # Print up to 3 correlation values
        printed = 0
        for other_link, rho in link.rho.items():
            if other_link != link and printed < 3:
                logger.log(f"    with Link {other_link.label}: {rho:.2f}")
                printed += 1
    instance_generator.draw_graph(graph)

    # Esecuzione dei modelli di ottimizzazione
    graph.new_travel(graph.get_node(origin), graph.get_node(destination), gamma=6)
    mv_travel_result = mv_problem.resolve_mv_problem(copy.copy(graph))
    graph.new_travel(graph.get_node(origin), graph.get_node(destination), gamma=6)
    ms_travel_result = ms_problem.resolve_ms_problem(copy.copy(graph))


    print("Calcolo miglior percorso dal nodo ", origin, " al nodo ", destination)
    # Stampa percorso del problema MV
    print("\nPercorso trovato (MV): (archi)", " -> ".join(str(link.label) for link in mv_travel_result.travel.path))

    # Stampa percorso del problema MS
    print("Percorso trovato (MS): (archi)", " -> ".join(str(link.label) for link in ms_travel_result.travel.path))

    print("Memoria utilizzata: ", mv_travel_result.travel.memory_usage)
    print("Memoria utilizzata: ", ms_travel_result.travel.memory_usage)
    print("Tempo utilizzata: ", mv_travel_result.travel.processing_time)
    print("Tempo utilizzata: ", ms_travel_result.travel.processing_time)



if __name__ == "__main__":
    main(num_nodes = 25,origin=1,destination=10, log=False) #Settare log a true per ottenere più informazioni sulle operazioni svolte dal programma