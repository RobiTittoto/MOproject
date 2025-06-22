import numpy as np
from generatore_istanze import generate_random_graph
from semplificazione_con_grafo import create_node_hyperlink_incidence_matrix


def main():
    g = generate_random_graph(4,4)
    incidence_matrix = np.array(g.to_incidence_matrix())
    print(incidence_matrix)

    create_node_hyperlink_incidence_matrix(incidence_matrix,1,4)

if __name__ == '__main__':
    main()


