import xpress as xp
from framework import logger
from framework.graph_classes import Graph


def resolve_mv_problem(graph: Graph):
    logger.log("----- Risoluzione problema mv ------")

    # Inizializza il modello Xpress
    model = xp.problem()

    # Imposta il livello di log
    model.setControl('outputlog', 1 if logger.LOG_ENABLED else 0)

    # Creazione delle variabili omega
    hyperlinks = graph.get_hyperlink()

    omega = {}

    for (link_a, link_b) in hyperlinks.keys():

        omega[(link_a, link_b)] = model.addVariable(
            name=f'omega_{link_a}_{link_b}',
            vartype=xp.continuous
        )

    # Aggiungta dei vincoli
    model_add_constrain(model, omega, graph)

    # Impostazione della funzione obiettivo
    objective = (
            xp.Sum(
                link.mu * omega[link, link]
                for link in graph.links
            ) +
            xp.Sum(
                hyperlinks[(link_a, link_b)].phi * omega[link_a, link_b]
                for link_a in graph.links
                for link_b in graph.links
                if (link_a, link_b) in hyperlinks
            )
    )

    model.setObjective(objective, sense=xp.minimize)

    # Ottimizzazione modello
    model.solve()

    if model.getAttrib('solstatus') == xp.SolStatus.OPTIMAL:
        logger.log("\nStatistiche:")
        logger.log(f"Iterazioni simplex: {model.getAttrib('simplexiter')}")
        logger.log(f"Tempo processamento: ", model.attributes.time)
        logger.log(f"Utilizzo memoria: ", model.attributes.peakmemory/ 1024 / 1024)

    # Elaborazione della soluzione
    path = []
    for link_a in graph.links:
        for link_b in graph.links:
            if model.getSolution(omega[link_b, link_a]) == 1:
                if link_a != link_b:
                    print("Attenzione errore: É presente in soluzione un arco inesistente")
                if model.getSolution(omega[link_a, link_b]) == 1:
                    label_exists = False
                    for link in path:
                        if link_a.label == link.label:
                            label_exists = True
                            break

                    if not label_exists:
                        path.append(link_a)

    graph.travel.add_path(path)
    graph.travel.processing_time = model.attributes.time
    graph.travel.memory_usage = model.attributes.peakmemory/ 1024 / 1024
    graph.travel.travel_time = model.attributes.objval

    return graph


def model_add_constrain(model: xp.problem, omega, graph: Graph):
    travel = graph.travel

    # Vincolo 8.1
    model.addConstraint(
        xp.Sum(omega[link, link] for link in travel.start.input) -
        xp.Sum(omega[link, link] for link in travel.start.output) == -1
    )

    # Vincolo 8.2
    model.addConstraint(
        xp.Sum(omega[link, link] for link in travel.end.input) -
        xp.Sum(omega[link, link] for link in travel.end.output) == 1
    )

    # Vincolo 8.3
    for node in graph.nodes:
        if node != travel.start and node != travel.end:
            model.addConstraint(
                xp.Sum(omega[link, link] for link in node.input) ==
                xp.Sum(omega[link, link] for link in node.output)
            )

    # Vincoli 9a, 9b e 10
    for node in graph.nodes:
        # Vincolo 9a
        for link_a in node.output:
            for link_b in node.output:
                if link_a != link_b and (link_a, link_b) in omega:
                    model.addConstraint(
                        omega[link_a, link_b] == 0
                    )

        # Vincolo 9b
        for link_a in node.input:
            for link_b in node.input:
                if link_a != link_b and (link_a, link_b) in omega:
                    model.addConstraint(
                        omega[link_a, link_b] == 0
                    )

        # Vincolo 10
        for link_a in node.input:
            for link_b in node.input:
                if link_a != link_b and (link_a, link_b) in omega and (link_b, link_a) in omega:
                    model.addConstraint(
                        omega[link_a, link_b] == omega[link_b, link_a]
                    )

