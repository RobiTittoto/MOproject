from creazione_problema import Graph, Travel, Node
import gurobipy as gp
from gurobipy import Var


def modello(graph: Graph, o: int, d: int):
    travel = Travel(graph.get_node(o), graph.get_node(d))
    model = gp.Model()
    print(len(graph.get_hyperlink()))
    omega = model.addVars(graph.get_hyperlink().keys(), vtype=gp.GRB.BINARY, name='omega')
    print('Omega: ' + str(omega))

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






def main():
    incidence_matrix = [
        [-1, 0, 0, 0],
        [1, -1, -1, 0],
        [0, 1, 1, -1],
        [0, 0, 0, 1]
    ]

    mu_list = [1.0, 2.0, 3.0, 4.0]
    sigma_list = [0.1, 0.2, 0.3, 0.4]


    g = Graph.from_incidence_matrix(incidence_matrix, mu_list, sigma_list)
    print(g)
    origin = g.get_node(1)
    destination = g.get_node(3)
    print(origin, destination)
    modello(g, 1, 3)

    print(g)
    for l in g.links:
        print(l)

if __name__ == "__main__":
    main()
