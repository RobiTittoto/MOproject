from graph_classes import Graph, Travel, Node
import gurobipy as gp

def resolve_mv_problem(graph: Graph, o: int, d: int, log: bool):

    model = gp.Model()
    if not log :
        model.setParam('OutputFlag', 0)

    travel = Travel(graph.get_node(o), graph.get_node(d))

    omega = model.addVars(graph.get_hyperlink().keys(), vtype=gp.GRB.CONTINUOUS, name='omega')

    model.addConstr(
        (
                gp.quicksum(omega[link, link] for link in travel.origin.input) -
                gp.quicksum(omega[link, link] for link in travel.origin.output)
                == -1
        ), name='vincolo 8.1'
    )

    model.addConstr(
        (
                gp.quicksum(
                    omega[link, link] for link in travel.destination.input) -
                gp.quicksum(
                    omega[link, link] for link in travel.destination.output)
                == 1
        ), name='vincolo 8.2'
    )

    '''model.addConstrs(
        (
            gp.quicksum(omega[link, link] for link in graph.nodes[node].input) -
            gp.quicksum(omega[link, link] for link in graph.nodes[node].output)
            == 0 for node in range(len(graph.nodes))
        ), name='vincolo 8.3'
    )'''

    for node in graph.nodes:
        if node != travel.origin and node != travel.destination:
            model.addConstr(
                (gp.quicksum(omega[link, link] for link in node.input) ==
                 gp.quicksum(omega[link, link] for link in node.output)
            )
            )
    for node in range(len(graph.nodes)):
        model.addConstrs(
            (
                omega[link_a, link_b] == 0
                for link_a in graph.nodes[node].output
                for link_b in graph.nodes[node].output
                if link_a != link_b
            ), name='vincolo_9a'
        )
        model.addConstrs(
            (
                omega[link_a, link_b] == 0
                for link_a in graph.nodes[node].input
                for link_b in graph.nodes[node].input
                if link_a != link_b
            ), name='vincolo 9b'
        )
        model.addConstrs(
            (
                omega[link_a, link_b]
                ==
                omega[link_b, link_a]
                for link_a in graph.nodes[node].input
                for link_b in graph.nodes[node].input
                if link_a != link_b
            ), name='vincolo 10'
        )

    hyperlinks = graph.get_hyperlink()
    #phi = [h.rho * h.link_a.sigma * h.link_b.sigma for key in hyperlinks.keys() if (h := hyperlinks.get(key))]
    model.setObjective(
        (
                gp.quicksum(
                    link.mu * omega[link, link]
                    for link in graph.links
                )
                +
                gp.quicksum(
                    hyperlinks[(link_a, link_b)].phi *
                    omega[link_a, link_b]
                    for link_a in graph.links
                    for link_b in graph.links
                )
        ), sense=gp.GRB.MINIMIZE
    )

    model.optimize()

    for link_a in graph.links:
        for link_b in graph.links:
            if omega[link_a, link_b].X != 0:
                if omega[link_a, link_b].X == 1:
                    travel.links.append(link_a)
                if omega[link_a, link_b].X != 1 or link_a !=link_b:
                    print("Errore")
    return travel
