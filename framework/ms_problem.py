import math
import time
from memory_profiler import memory_usage
from framework import mv_problem, logger
from framework.graph_classes import Graph
import xpress as xp



def branch_and_bound(lb: float, ub: float, graph: Graph, depth=0, max_depth=100):
    epsilon = 1e-6

    try:
        model = xp.problem()

        # Impostazione del livello di log
        model.setControl('outputlog', 1 if logger.LOG_ENABLED else 0)

        # Creazione delle variabili omega
        hyperlinks = graph.get_hyperlink()

        omega = {}
        for (link_a, link_b) in hyperlinks.keys():
            omega[(link_a, link_b)] = model.addVariable(
                name=f'omega_{link_a}_{link_b}',
                vartype=xp.continuous
            )


        # Aggiunta vincoli al modello
        mv_problem.model_add_constrain(model, omega, graph)

        # Impostazione della funzione obiettivo
        objective = (
                xp.Sum(
                    link.mu * omega[link, link]
                    for link in graph.links
                )
                + ((graph.travel.gamma * math.sqrt(ub) - graph.travel.gamma * math.sqrt(lb)) / (ub - lb)) *
                xp.Sum(
                    hyperlinks[(link_a, link_b)].phi *
                    omega[link_a, link_b]
                    for link_a in graph.links
                    for link_b in graph.links
                )
                + (graph.travel.gamma * math.sqrt(lb) - graph.travel.gamma * math.sqrt(ub)) / (lb - ub) + graph.travel.gamma * math.sqrt(lb)
        )
        model.setObjective(objective, sense=xp.minimize)

        # Ottimizzazione modello
        time_start = time.time()
        model.solve()
        time_end = time.time()
        total_time = time_end - time_start

        if model.getAttrib('solstatus') == xp.SolStatus.OPTIMAL:
            logger.log("\nStatistiche:")
            logger.log(f"Iterazioni simplex: {model.getAttrib('simplexiter')}")
            logger.log(f"Tempo preprocessing:", total_time)

        # Calcolo eta_star
        eta_star = sum(
            hyperlinks[(link_a, link_b)].phi * model.getSolution(omega[link_a, link_b])
            for link_a in graph.links
            for link_b in graph.links
        )

        logger.log("eta star: ", eta_star," ciclo ", depth+1)

        # Calcolo che branch esplorare
        if eta_star == ub or eta_star == lb:
            return model, omega

        val_lower = calc(graph, model, omega, lb, eta_star, eta_star)
        val_upper = calc(graph, model, omega, eta_star, ub, eta_star)

        new_lb, new_ub = (lb, eta_star) if val_lower < val_upper else (eta_star, ub)


        if abs((new_lb + new_ub) / 2 - (lb + ub) / 2) < epsilon or depth >= max_depth:
            return model, omega

        # Chiamata ricorsiva
        return branch_and_bound(new_lb, new_ub, graph, depth + 1)

    except Exception as e:
        print(f"Errore in branch_and_bound: {str(e)}")
        return model, omega


def calc(graph, model,omega, lb, ub, eta_star):
    logger.log("lb:",lb,"ub:", ub)
    try:
        term1 = sum(link.mu * model.getSolution(omega[link, link]) for link in graph.travel.path)
        term2 = (graph.travel.gamma * math.sqrt(lb)) / (ub - lb) * eta_star
        term3 = (graph.travel.gamma * math.sqrt(lb) - graph.travel.gamma * math.sqrt(ub)) / (lb - ub)
        term4 = graph.travel.gamma * math.sqrt(lb)
        return term1 + term2 + term3+ term4
    except Exception as e:
        print(f"Errore in calc: {str(e)}")
        return float('inf')  # Restituisce il caso peggiore se il calcolo fallisce



def resolve_ms_problem(graph: Graph):
    def wrapper():
        return branch_and_bound(l0, u0, graph)
    logger.log("----- Risoluzione problema mv ------")
    hyperlinks = graph.get_hyperlink()

    # Impostazione limiti iniziali
    l0 = 0
    u0 = 0
    for key in hyperlinks.keys():
        u0 += hyperlinks[key].phi

    logger.log("l0={}".format(l0))
    logger.log("u0={}".format(u0))

    # Risoluzione problema
    time_start = time.time()
    max_memory_used, result = memory_usage(wrapper, max_usage=True, retval=True)
    model, omega = result
    time_end = time.time()
    total_time = time_end - time_start

    if model.getAttrib('solstatus') == xp.SolStatus.OPTIMAL:
        logger.log("\nStatistiche:")
        logger.log(f"Iterazioni simplex: {model.getAttrib('simplexiter')}")
        logger.log(f"Tempo processamento: ", total_time)
        logger.log(f"Utilizzo memoria: ", max_memory_used)

    # Elaborazione della soluzione
    path = []
    for link_a in graph.links:
        for link_b in graph.links:
            if model.getSolution(omega[link_b, link_a]) == 1:
                if link_a != link_b:
                    print("Attenzione errore: É presente in soluzione un arco inesistente")
                if model.getSolution(omega[link_a, link_b]) == 1:
                    if link_a not in path:
                        path.append(link_a)

    graph.travel.add_path(path)
    graph.travel.processing_time = total_time
    graph.travel.memory_usage = max_memory_used
    graph.travel.travel_time = model.attributes.objval


    return graph
