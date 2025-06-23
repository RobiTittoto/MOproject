import numpy as np
import gurobipy as gp
from generatore_istanze import generate_connected_graph
from semplificazione_con_grafo import create_node_hyperlink_incidence_matrix


def main():
    g = generate_connected_graph(4)
    incidence_matrix = np.array(g.to_incidence_matrix())
    print(incidence_matrix)

    # Esempio iniziale del tuo dizionario psi
    psi = {
        (0, 0): 0.0, (1, 1): 0.0, (2, 2): 0.0, (3, 3): 0.0,  # VARIANZE individuali → metti 0.0 o valori >0
        (0, 1): 0.1, (1, 0): 0.1,
        (0, 2): 0.2, (2, 0): 0.2,
        (1, 2): 0.05, (2, 1): 0.05,
        (1, 3): 0.3, (3, 1): 0.3,
        (2, 3): 0.15, (3, 2): 0.15,
        (0, 3): 0.12, (3, 0): 0.12,
    }

    # Conversione in matrice numpy (inizialmente zeri)
    psi_array = np.zeros((g.links_number, g.links_number))

    # Inserisci i valori del dizionario nella matrice
    for (i, j), value in psi.items():
        psi_array[i, j] = value

    gamma1 = 0.5
    gamma2 = 6
    mu = np.array([5, 10, 8, 12])  # esempio valori medi


    node_hyperlink_incidence_matrix, omega_vars, h_vector = create_node_hyperlink_incidence_matrix(incidence_matrix,1,4)

    model = gp.Model()

    # Crea le variabili ω
    omega = []
    for nome in omega_vars:
        var = model.addVar(lb=0.0, ub=1.0, vtype=gp.GRB.CONTINUOUS, name=nome)
        omega.append(var)

    # Vincoli lineari H_finale @ ω = h_vettore
    for i in range(node_hyperlink_incidence_matrix.shape[0]):
        expr = gp.LinExpr()
        for j in range(node_hyperlink_incidence_matrix.shape[1]):
            coeff = node_hyperlink_incidence_matrix[i, j]
            if coeff != 0:
                expr += coeff * omega[j]
        model.addConstr(expr == h_vector[i], name=f"Constraint_{i}")

    # Funzione obiettivo ming₂
    build_objective_ming2(model, omega, omega_vars, mu, psi, gamma1)

    model.optimize()

def build_objective_ming2(model, omega, omega_vars, mu, psi, gamma1):
    """
    Costruisce la funzione obiettivo ming₂ secondo la formula:
    min g₂(ω) = Σ μₐ * ω_{a∧a} + γ₁ * Σₐ Σ_b ψ_{ab} * ω_{a∧b}

    Parameters:
        model      : modello Gurobi
        omega      : lista di variabili Gurobi corrispondenti alle ω
        omega_vars : lista di stringhe dei nomi delle ω nell'ordine di omega
        mu         : array numpy dei costi medi μₐ
        psi        : matrice numpy ψ_{ab}
        gamma1     : parametro γ₁

    Returns:
        None (l'obiettivo viene impostato nel modello)
    """

    obiettivo_media = gp.LinExpr()
    n_archi = mu.shape[0]

    # Primo termine: Σ μₐ * ω_{a∧a}
    for idx, nome in enumerate(omega_vars):
        if '^' in nome:
            parts = nome.replace("ω_", "").split("^")
            if parts[0] == parts[1]:  # ω_{a∧a}
                arco_idx = int(parts[0]) - 1  # 0-based index per mu
                obiettivo_media += mu[arco_idx] * omega[idx]

    # Secondo termine: γ₁ * Σₐ Σ_b ψ_{ab} * ω_{a∧b}
    obiettivo_varianza = gp.LinExpr()
    for idx, nome in enumerate(omega_vars):
        if '^' in nome:
            parts = nome.replace("ω_", "").split("^")
            a = int(parts[0]) - 1
            b = int(parts[1]) - 1
            obiettivo_varianza += psi[a, b] * omega[idx]

    model.setObjective(obiettivo_media + gamma1 * obiettivo_varianza, gp.GRB.MINIMIZE)

if __name__ == '__main__':
    main()


