import xpress as xp
import time
from framework import logger
from framework.graph_classes import Graph
import psutil
import os


def resolve_mv_problem(graph: Graph):

    logger.log("----- Risoluzione problema mv ------")

    # Inizializza il modello Xpress
    xp.init('/Applications/FICO Xpress/xpressmp/bin/xpauth.xpr')
    model = xp.problem()

    # Imposta il livello di log
    model.setControl('outputlog', 1 if logger.LOG_ENABLED else 0)

    # Crea le variabili omega
    hyperlinks = graph.get_hyperlink()
    omega = {(link_a, link_b): xp.var(name=f'omega_{link_a}_{link_b}')
             for (link_a, link_b) in hyperlinks.keys()}

    # Aggiungi le variabili al modello
    model.addVariable(omega)

    # Aggiungi i vincoli
    model_add_constrain(model, omega, graph)

    # Imposta la funzione obiettivo
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

    # Risolvi il problema
    model.solve()

    if model.getAttrib('solstatus') == xp.SolStatus.OPTIMAL:
        logger.log("\nStatistiche:")
        logger.log(f"Iterazioni simplex: {model.getAttrib('simplexiter')}")
        logger.log(f"Tempo processamento: ", model.attributes.time)
        logger.log(f"Utilizzo memoria: ", model.attributes.peakmemory/ 1024 / 1024)

    # Elabora la soluzione
    path = []
    for link_a in graph.links:
        for link_b in graph.links:
            if model.getSolution(omega[link_b, link_a]) == 1:
                if link_a != link_b:
                    print("Attenzione errore è present in soluzione un arco inesistente")
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
    graph.travel.travel_time = model.getSolution()

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

def measure_memory_usage():
    """Misura l'utilizzo della memoria del processo corrente in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Converti in MB
