def create_incidence_matrix(num_nodes, num_links):
    # Initialize an n x m matrix filled with zeros
    incidence_matrix = [[0 for _ in range(num_links)] for _ in range(num_nodes)]

    for link_idx in range(num_links):
        print(f"\nEnter details for link {link_idx}:")
        while True:
            try:

                if source < 0 or source >= num_nodes or target < 0 or target >= num_nodes:
                    print("Error: Node index out of range. Try again.")
                elif source == target:
                    print("Error: Self-loops (same source and target) are not allowed in standard incidence matrices.")
                else:
                    break
            except ValueError:
                print("Error: Please enter valid integers.")

        # Update the incidence matrix
        incidence_matrix[source][link_idx] = 1  # +1 for outgoing link
        incidence_matrix[target][link_idx] = -1  # -1 for incoming link

    return incidence_matrix


def print_matrix(matrix):
    for row in matrix:
        print(" ".join(f"{elem:3}" for elem in row))


if __name__ == "__main__":
    print("=== Directed Graph Incidence Matrix Generator ===")
    num_nodes = int(input("Enter the number of nodes (n): "))
    num_links = int(input("Enter the number of links (m): "))

    incidence_matrix = create_incidence_matrix(num_nodes, num_links)

    print("\n=== Incidence Matrix ===")
    print_matrix(incidence_matrix)