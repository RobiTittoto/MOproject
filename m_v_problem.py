from creazione_problema import Graph, Travel, Node
import gurobipy as gp


def modello(graph: Graph, origin: Node, destination: Node):
    travel = Travel(origin, destination)

    model = gp.Model()

    omega = model.addVars(graph.get_hyperlink(), vtype=gp.GRB.BINARY, name='omega')

    # assegno alle prime num_link omega il valore di w_11, w_22, w_23 ...

    model.addConstr(
        (
                gp.quicksum(omega[link.label * graph.link_number + link.label] for link in travel.origin.input) -
                gp.quicksum(omega[link.label * graph.link_number + link.label] for link in travel.origin.input)
                == -1
        ), name='vincolo 8.1'
    )

    model.addConstr(
        (
                gp.quicksum(
                    omega[(link.label * graph.link_number + link.label) + 1] for link in travel.destination.input) -
                gp.quicksum(
                    omega[(link.label * graph.link_number + link.label) + 1] for link in travel.destination.input)
                == 1
        ), name='vincolo 8.2'
    )

    model.addConstrs(
        (
            gp.quicksum(omega[(link.label * graph.link_number + link.label) + 1] for link in graph.nodes[node].input) -
            gp.quicksum(omega[(link.label * graph.link_number + link.label) + 1] for link in graph.nodes[node].input)
            == 0 for node in range(len(graph.nodes))
        ), name='vincolo 8.3'
    )
    for node in range(len(graph.nodes)):
        model.addConstrs(
            (
                omega[(link_a.label * graph.link_number + link_b.label) + 1] == 0 for link_a in graph.nodes[node].output
                for link_b in graph.nodes[node].output if link_a != link_b
            ), name='vincolo 9a'
        )
        model.addConstrs(
            (
                omega[(link_a.label * graph.link_number + link_b.label) + 1] == 0
                for link_a in graph.nodes[node].input
                for link_b in graph.nodes[node].input
                if link_a != link_b
            ), name='vincolo 9b'
        )
        model.addConstrs(
            (
                omega[(link_a.label * graph.link_number + link_b.label) + 1] == omega[
                    (link_b.label * graph.link_number + link_a.label) + 1]
                for link_a in graph.nodes[node].input
                for link_b in graph.nodes[node].input
                if link_a != link_b
            ), name='vincolo 10'
        )
        phi = [hyperlink.rho * hyperlink.link_a.sigma * hyperlink.link_b.sigma for hyperlink in graph.get_hyperlink()]
        model.setObjective(
            (
                    gp.quicksum(
                        link.mu * omega[(link.label * graph.link_number + link.label) + 1]
                        for link in graph.link
                    )
                    +
                    gp.quicksum(
                        phi[(link_a.label * graph.link_number + link_b.label) + 1] * phi[
                            (link_a.label * graph.link_number + link_b.label) + 1]
                        for link_a in graph.link
                        for link_b in graph.link
                    )
            )
        )
