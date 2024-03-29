import numpy as np
import networkx as nx

def recommendation_algorithm(adj_matrix):
    # Initialize graph
    G = nx.DiGraph()

    # Add vertices to the graph
    for i in range(adj_matrix.shape[0]):
        G.add_node(i)

    # Add edges to the graph
    for i in range(adj_matrix.shape[0]):
        for j in range(adj_matrix.shape[1]):
            if adj_matrix[i, j] > 0:
                G.add_edge(i, j, weight=adj_matrix[i, j])

    # Function to calculate shortest path weight
    def shortest_path_weight(start_vertex, end_vertex):
        # Calculate shortest path
        path = nx.shortest_path(G, source=start_vertex, target=end_vertex, weight='weight')

        # Calculate path weight
        path_weight = 0
        for i in range(len(path)-1):
            path_weight += G[path[i]][path[i+1]]['weight']

        return path_weight

    # Calculate recommendations
    recommendations = {}
    for vertex in G.nodes():
        total_weight = 0
        for neighbor in G.neighbors(vertex):
            total_weight += G[vertex][neighbor]['weight']
        for neighbor in G.neighbors(vertex):
            weight = G[vertex][neighbor]['weight']
            recommendation_score = weight / total_weight
            path_weight = shortest_path_weight(vertex, neighbor)
            recommendations[neighbor] = recommendation_score * path_weight
            print(weight,recommendation_score,path_weight )

    # Sort recommendations by score
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1])

    return sorted_recommendations
A = np.array([
    [0, 1,  2,  8, 3],
    [5, 0,  4, 0,  3],
    [7, 9,  0,  6,  0],
    [3, 13,  6, 0,  7],
    [7, 10,  9,  2, 0]])
print(recommendation_algorithm(A))