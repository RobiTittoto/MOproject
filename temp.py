import math
import gurobipy as gp

import instance_generator
import mv_problem

from graph_classes import Graph

def branch_and_bound(lb: float, ub: float, graph: Graph, gamma, depth=0, max_depth=100):
    epsilon = 1e-6

    try:
        model = gp.Model()
        model.setParam('OutputFlag', 0)

        omega = model.addVars(graph.get_hyperlink().keys(), vtype=gp.GRB.CONTINUOUS, name='omega')
        model.update()

        mv_problem.model_add_constrain(model, omega, graph)  # add constraints (13)
        hyperlinks = graph.get_hyperlink()

        # Set the objective function
        model.setObjective(
            (
                    gp.quicksum(
                        link.mu * omega[link, link]
                        for link in graph.links
                    )
                    + ( ( gamma * math.sqrt(ub) - gamma * math.sqrt(lb) ) / (ub - lb) )*
                    gp.quicksum(
                        hyperlinks[(link_a, link_b)].phi *
                        omega[link_a, link_b]
                        for link_a in graph.links
                        for link_b in graph.links
                    )
                    + (gamma * math.sqrt(lb) - gamma * math.sqrt(ub)) / (lb - ub) + gamma * math.sqrt(lb)
            ),
            sense=gp.GRB.MINIMIZE
        )

        model.optimize()

        for link_a in graph.links:
            for link_b in graph.links:
                if omega[link_a, link_b].X != 0:
                    if omega[link_a, link_b].X == 1:
                        graph.travel.links.append(link_a)
                    if omega[link_a, link_b].X != 1 or link_a != link_b:
                        print("Errore")
        for link in graph.travel.links:
            print(link.label)

        if model.status != gp.GRB.OPTIMAL:
            raise Exception("Model didn't solve to optimality")

        # Calculate eta_star
        eta_star = sum(
            hyperlinks[(link_a, link_b)].phi * omega[link_a, link_b].X
            for link_a in graph.links
            for link_b in graph.links
        )


        # Calcolare che branch esplorare
        val_lower = calc(graph, omega, gamma, lb, eta_star, eta_star)
        val_upper = calc(graph, omega, gamma, eta_star, ub, eta_star)

        new_lb, new_ub = (lb, eta_star) if val_lower < val_upper else (eta_star, ub)

        # CONDIZIONE CORRETTA
        if abs((new_lb + new_ub) / 2 - (lb + ub) / 2) < epsilon or depth >= max_depth:
            # Processa la soluzione finale
            for link_a in graph.links:
                for link_b in graph.links:
                    if omega[link_a, link_b].X != 0:
                        if omega[link_a, link_b].X == 1:
                            graph.travel.links.append(link_a)
                        elif link_a != link_b:
                            print("Attenzione: valore non intero o incoerenza")
            return (new_lb + new_ub) / 2  # Ritorna il punto medio

        # Recursive call
        return branch_and_bound(new_lb, new_ub, graph, gamma, depth + 1, max_depth)

    except Exception as e:
        print(f"Error in branch_and_bound: {str(e)}")
        return (lb + ub) / 2  # Return current best estimate


def calc(graph, omega, gamma, lb, ub, eta_star):
    print("eta_star:", eta_star,"lb:",lb,"ub:", ub)
    try:
        term1 = sum(link.mu * omega[link, link].X for link in graph.links)
        term2 = (gamma * math.sqrt(lb)) / (ub - lb) * eta_star
        term3 = (gamma * math.sqrt(lb) - gamma * math.sqrt(ub)) / (lb - ub)
        term4 = gamma * math.sqrt(lb)
        return term1 + term2 + term3+ term4
    except Exception as e:
        print(f"Error in calc: {str(e)}")
        return float('inf')  # Return worst case if calculation fails

