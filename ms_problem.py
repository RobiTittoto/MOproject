import math


import mv_problem
import temp
from graph_classes import Graph
import gurobipy as gp
import logger


def initialization():
    pass


def branch_and_bound(lb: float, ub: float, graph: Graph, gamma):
    epsilon = 0.0005
    model = gp.Model()

    model.setParam('OutputFlag', 0)

    omega = model.addVars(graph.get_hyperlink().keys(), vtype=gp.GRB.CONTINUOUS, name='omega')
    model.update()

    mv_problem.model_add_constrain(model, omega, graph)  # aggiunge i vincoli (13)
    hyperlinks = graph.get_hyperlink()

    model.setObjective(
        (
                gp.quicksum(
                    link.mu * omega[link, link]
                    for link in graph.links
                )
                + (gamma * math.sqrt(lb)) / (ub - lb) *
                gp.quicksum(
                    hyperlinks[(link_a, link_b)].phi *
                    omega[link_a, link_b]
                    for link_a in graph.links
                    for link_b in graph.links
                )
                + (gamma * math.sqrt(lb) - gamma * math.sqrt(ub)) / (lb - ub) + gamma * math.sqrt(lb)

        ), sense=gp.GRB.MINIMIZE
    )

    model.optimize()

    eta_star = 0
    for link_a in graph.links:
        for link_b in graph.links:
            eta_star += hyperlinks[(link_a, link_b)].phi * omega[link_a, link_b].X
    print("eta_star:", eta_star)

    new_lb, new_ub = [lb, eta_star] if calc(graph, omega, gamma , lb, eta_star, eta_star) < calc(graph, omega, gamma , eta_star, ub, eta_star) else [eta_star,ub]

    print("new_lb:", new_lb, "new_ub:", new_ub)

    if (new_lb + new_ub) / 2 - (lb + ub) / 2 < epsilon:
        for link_a in graph.links:
            for link_b in graph.links:
                if omega[link_a, link_b].X != 0:
                    if omega[link_a, link_b].X == 1:
                        graph.travel.links.append(link_a)
                    if omega[link_a, link_b].X != 1 or link_a != link_b:
                        print("Errore")
    else:
        branch_and_bound(new_lb, new_ub, graph, gamma)
    return





def calc(graph, omega, gamma, lb, ub, eta_star):
    tot = 0
    for link in graph.links:
        tot += link.mu * omega[link, link].X

    tot += (gamma * math.sqrt(lb)) / (ub - lb) * eta_star

    tot += (gamma * math.sqrt(lb) - gamma * math.sqrt(ub)) / (lb - ub) + gamma * math.sqrt(lb)
    return tot


def resolve_ms_problem(graph: Graph):
    gamma = 6
    hyperlinks = graph.get_hyperlink()
    l0 = 0
    u0 = 0
    for key in hyperlinks.keys():
        u0 += key[0].mu if key[0] == key[1] else 0
        u0 += hyperlinks[key].phi

    print("l0={}".format(l0))
    print("u0={}".format(u0))

    epsilon = 1e-6

    print(temp.branch_and_bound(l0, u0,graph, gamma))
