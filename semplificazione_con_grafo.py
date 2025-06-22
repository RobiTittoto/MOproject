import numpy as np
import scipy


def create_node_hyperlink_incidence_matrix(incidence_matrix, origin, destination):
    """
                Funzione che genera la matrice H completa e costruisce l'equazione del sistema.

                Args:
                    incidence_matrix: Matrice di incidenza del grafo (n_nodi x num_links)
                    origin: Lista dei nodi sorgente (0-based indexing)
                    destination: Lista dei nodi pozzo (0-based indexing)

                Returns:
                    Tuple (H_finale, omega_vars, h_vettore)
                """

    if not origin or not destination:
        raise ValueError("I nodi origine e destinazione non possono essere vuoti o None")

    num_nodes, num_links = incidence_matrix.shape
    od_pair = [origin-1, destination-1]

    def generate_hyperlink_matrix():
        """
            Genera la matrice degli archi i^j applicando i vincoli (9a) e (9b).
            """


        # Inizializza la matrice con gli archi i^j
        for i in range(num_links):
            for j in range(num_links):
                hyperlinks_matrix[i, j] = f"{i + 1}^{j + 1}"

        # Applica vincoli (9a) e (9b) per settare gli zeri
        for node in range(num_nodes):
            # Trova archi uscenti dal nodo (coefficiente -1)
            out_links = np.where(incidence_matrix[node, :] == -1)[0]
            if len(out_links) > 1:
                # Vincolo (9a): Se a, b ∈ L_out(a), allora ω_a∧b = 0
                for i in out_links:
                    for j in out_links:
                        if i != j:
                            hyperlinks_matrix[i, j] = '0'

            # Trova archi entranti nel nodo (coefficiente +1)
            in_links = np.where(incidence_matrix[node, :] == 1)[0]
        if len(in_links) > 1:
            # Vincolo (9b): Se a, b ∈ L_in(a), allora ω_a∧b = 0
            for i in in_links:
                for j in in_links:
                    if i != j:
                        hyperlinks_matrix[i, j] = '0'

        return hyperlinks_matrix

    def generate_J_vector():
        """
        Generate the J vector automatically from the hyperlinks matrix.
        The J vector contains elements of the form "J_i^j" for each unique directed edge (i, j)
        in the hyperlinks matrix, excluding diagonal elements and symmetric pairs.
        """
        J = []
        processed_links = set()

        for (i, j), value in np.ndenumerate(hyperlinks_matrix):
            if i == j or value == '0':
                continue

            edge = (i, j)
            symmetric_edge = (j, i)

            if edge not in processed_links and symmetric_edge not in processed_links:
                J.append(f"J_{i + 1}^{j + 1}")
                processed_links.update({edge, symmetric_edge})

        return J

    def generate_node_hyperlink_incidence_matrices():
        """
        Genera tutte le matrici H_n per ogni rarco.
        """
        return [generate_node_hyperlink_incidence_matrix_link_a(link_a) for link_a in range(num_links)]


    def generate_node_hyperlink_incidence_matrix_link_a(link_a):
        """
        Genera la matrice H_a per l'arco a-esimo.
        """

        # Trova i nodi che l'arco a connette
        link_a_nodes = set(np.where(incidence_matrix[:, link_a] != 0)[0])

        # Determina quali righe includere
        if link_a_nodes.intersection(od_pair):
            rows_to_include = []
            for node in range(num_nodes):
                if node not in od_pair or node in link_a_nodes:
                    rows_to_include.append(node)
        else:
            rows_to_include = [node for node in range(num_nodes) if node not in od_pair]

        # Trova le colonne (archi) NON zeri della riga a della matrice archi
        columns_to_include = [j for j, val in enumerate(hyperlinks_matrix[link_a, :]) if val != '0']

        # Estrai la sotto-matrice
        node_hyperlink_incidence_matrix_link_a = incidence_matrix[np.ix_(rows_to_include, columns_to_include)]

        return node_hyperlink_incidence_matrix_link_a

    def create_map_hyperlink_column():
        """
        Crea una mappa che associa ogni arco (i^j) alla sua posizione nelle colonne di Hp.
        """
        hyperlinks_map = {}
        column_pos = 0

        for i in range(num_hyperlinks):
            for j in range(num_hyperlinks):
                if hyperlinks_matrix[i, j] != '0':
                    hyperlinks_map[(i, j)] = column_pos
                    column_pos += 1

        return hyperlinks_map

    def generate_row_vector_J():
        """
        Genera i vettori riga per ogni elemento J_x^y.
        """
        row_vectors_J = []

        for j_element in J_list:
            # Estrai x e y da "J_x^y"
            parts = j_element.replace("J_", "").split("^")
            x = int(parts[0]) - 1  # Converti a 0-based
            y = int(parts[1]) - 1  # Converti a 0-based

            # Crea il vettore riga inizializzato a zero
            row_vector_J = np.zeros(diagonal_node_hyperlink_incidence_matrix.shape[1], dtype=int)

            # Trova le posizioni di x^y e y^x nella matrice Hp
            pos_xy = hyperlink_map.get((x, y))
            pos_yx = hyperlink_map.get((y, x))

            # Imposta i valori
            if pos_xy is not None:
                row_vector_J[pos_xy] = 1
            if pos_yx is not None:
                row_vector_J[pos_yx] = -1

            row_vectors_J.append(row_vector_J)

        return row_vectors_J

    def create_complete_J_matrix():
        """
        Combina tutti i vettori riga in una matrice J completa.
        """
        if not row_vectors_J:
            return np.array([])
        return np.vstack(row_vectors_J)

    def create_node_hyperlink_incidence_matrix():
        """
        Crea la matrice H combinando Hp e J.
        """
        if diagonal_node_hyperlink_incidence_matrix.shape[1] != matrix_J.shape[1]:
            raise ValueError(
                f"Incompatibilità nelle colonne: Hp ha {diagonal_node_hyperlink_incidence_matrix.shape[1]} colonne, "
                f"J ha {matrix_J.shape[1]} colonne")

        return np.vstack([diagonal_node_hyperlink_incidence_matrix, matrix_J])

    def build_omega_vector():
        """
        Costruisce il vettore simbolico ω (omega) delle variabili di flusso degli hyperlink.

        Args:
            hyperlinks_matrix: Matrice degli archi con vincoli applicati

        Returns:
            Lista di stringhe rappresentanti le variabili ω
        """
        omega_vars = []

        # Scandisce la matrice archi per creare le variabili ω
        for i in range(num_hyperlinks):
            for j in range(num_hyperlinks):
                if hyperlinks_matrix[i, j] != '0':
                    if i == j:
                        # Variabile per singolo link: ω_a^a
                        omega_vars.append(f"ω_{i + 1}^{j + 1}")
                    else:
                        # Variabile per coppia di link: ω_a^b
                        omega_vars.append(f"ω_{i + 1}^{j + 1}")
        return omega_vars

    def build_vector_J():
        """
        Costruisce il vettore h del lato destro dei vincoli.

        Returns:
            Array numpy rappresentante il vettore h
        """

        number_symmetry_constraints = len(J_list) #Numero di vincoli di simmetria J
        h_parts = []

        # Costruisce hp per ogni matrice H_n
        for n, H_n in enumerate(node_hyperlink_incidence_matrices_list):
            num_rows_Hn = H_n.shape[0]
            h_n = np.zeros(num_rows_Hn)

            # Identifica quale nodo corrisponde a ciascuna riga di H_n
            # Trova i nodi che l'arco n connette
            nodes_link_n = set(np.where(incidence_matrix[:, n] != 0)[0])

            # Determina le righe incluse in H_n (stesso algoritmo di genera_H_n)
            if nodes_link_n.intersection(od_pair):
                included_lines = []
                for node in range(incidence_matrix.shape[0]):
                    if node not in od_pair or node in nodes_link_n:
                        included_lines.append(node)
            else:
                included_lines = [nodo for nodo in range(incidence_matrix.shape[0]) if nodo not in od_pair]

            # Imposta i valori di h_n basati sui nodi terminali
            for idx, node in enumerate(included_lines):
                if node == origin:
                    h_n[idx] = -1  # Sorgente
                elif node == destination:
                    h_n[idx] = 1  # Pozzo
                else:
                    h_n[idx] = 0  # Nodo intermedio

            h_parts.append(h_n)

        # Concatena tutte le parti hp
        hp = np.concatenate(h_parts) if h_parts else np.array([])

        # Aggiunge zeri per i vincoli di simmetria J
        h_J = np.zeros( number_symmetry_constraints)

        # Combina hp e h_J
        return np.concatenate([hp, h_J]) if hp.size > 0 else h_J

    '''Inizio codice'''

    print("=== GENERAZIONE MATRICE H ===")
    print(f"Matrice di incidenza input: {incidence_matrix.shape}")

    print(f"Nodi sorgente: {origin}")  # Converti a 1-based per display
    print(f"Nodi pozzo: {destination}")  # Converti a 1-based per display

    # Passo 1: Genera la matrice degli archi con vincoli

    hyperlinks_matrix = np.empty((num_links, num_links), dtype=object)
    hyperlinks_matrix = generate_hyperlink_matrix()
    print(f"Matrice archi generata: {hyperlinks_matrix.shape}")

    num_hyperlinks = hyperlinks_matrix.shape[0]

    # Passo 2: Genera automaticamente il vettore J
    J_list = generate_J_vector()
    print(f"Vincoli J generati: {len(J_list)}")

    # Passo 3: Genera tutte le matrici H_n
    node_hyperlink_incidence_matrices_list = generate_node_hyperlink_incidence_matrices()  # Genera tutte le matrici H_n per ogni arco.
    print(f"Matrici H_n generate: {len(node_hyperlink_incidence_matrices_list)}")

    # Passo 4: Crea la matrice diagonale a blocchi Hp
    diagonal_node_hyperlink_incidence_matrix = scipy.linalg.block_diag(
        *node_hyperlink_incidence_matrices_list)
    print(f"Matrice Hp: {diagonal_node_hyperlink_incidence_matrix.shape}")

    # Passo 5: Crea la matrice J
    hyperlink_map = create_map_hyperlink_column()  # Crea una mappa che associa ogni arco (i^j) alla sua posizione nelle colonne di Hp
    row_vectors_J = generate_row_vector_J()  # Genera i vettori riga per ogni elemento J_x^y.
    matrix_J = create_complete_J_matrix()

    if matrix_J.size > 0:
        print(f"Matrice J: {matrix_J.shape}")
        node_hyperlink_incidence_matrix = create_node_hyperlink_incidence_matrix()  # Crea la matrice H combinando Hp e J.
    else:
        print("Nessun vincolo J")
        node_hyperlink_incidence_matrix = diagonal_node_hyperlink_incidence_matrix

    print(f"Matrice H finale: {node_hyperlink_incidence_matrix.shape}")

    # Passo 6: Costruisce i vettori ω e h
    omega_vars = build_omega_vector()
    h_vector = build_vector_J()

    print(f"Vettore ω: {len(omega_vars)} variabili")
    print(f"Vettore h: {len(h_vector)} elementi")
    print("=" * 30)

    return node_hyperlink_incidence_matrix, omega_vars, h_vector


def main():
    A = np.array([
        [-1, 0, 0, 0],
        [1, -1, -1, 0],
        [0, 1, 1, -1],
        [0, 0, 0, 1]
    ])
    (H_finale, omega_vars, h_vettore) = create_node_hyperlink_incidence_matrix(A,1,4)
    print("\nMatrice H finale:")
    print(H_finale)

    print(f"\nVettore ω (variabili di flusso):")
    print(omega_vars)

    print(f"\nVettore h (termini noti):")
    print(h_vettore)


if __name__ == "__main__":
    main()
