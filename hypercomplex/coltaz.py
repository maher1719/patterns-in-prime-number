#!/usr/bin/env python3
import sympy
"""
This script provides two functionalities:
1. Plotting the 3n+1 (Collatz) sequence as a directed graph.
2. Plotting a general tree (implemented as a full binary tree) by level.

Usage (from command line):
    python script.py --collatz N   # where N is the starting integer for the Collatz sequence
    python script.py --tree M      # where M is the number of levels in the tree

The script uses:
- NetworkX for graph data structures and algorithms.
- Matplotlib for plotting.
- A custom hierarchical layout (hierarchy_pos) to neatly display trees.
"""

import argparse
import networkx as nx
import matplotlib.pyplot as plt

def collatz_sequence(n: int) -> list:
    """
    Compute the Collatz (3n+1) sequence starting from n until it reaches 1.
    
    Parameters:
        n (int): The starting integer (must be positive).
    
    Returns:
        list: The Collatz sequence as a list of integers.
    
    The function implements the iterative rules:
        - If n is even, n → n/2.
        - If n is odd,  n → 3n + 1.
    The sequence is conjectured (Collatz Conjecture) to eventually reach 1.
    """
    if n < 1:
        raise ValueError("Input must be a positive integer.")
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def plot_collatz_graph(n: int) -> None:
    """
    Plot the Collatz sequence as a directed graph and display the number of nodes.
    
    Each number in the sequence is a node, and an edge is drawn from a number to its successor.
    The graph is visualized using a spring layout for clarity.
    
    Parameters:
        n (int): The starting integer for the Collatz sequence.
    """
    # Create a directed graph
    G = nx.DiGraph()
    # Compute the sequence and add edges
    seq = collatz_sequence(n)
    for i in range(len(seq) - 1):
        G.add_edge(seq[i], seq[i+1])
    
    # Calculate the number of nodes
    num_nodes = G.number_of_nodes()
    print(f"Number of nodes in Collatz graph: {num_nodes}")
    
    # Use a spring layout for a visually appealing arrangement
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=600, node_color="skyblue", arrows=True, arrowstyle='->', arrowsize=12)
    
    # Include the number of nodes in the title
    plt.title(f"Collatz 3n+1 Directed Graph for n = {n} (Nodes: {num_nodes})")
    plt.show()

def hierarchy_pos(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    Compute the hierarchical positions for a tree-like graph.
    
    This function recursively assigns positions to each node to produce a tree layout.
    Adapted from a well-known solution on StackOverflow.
    
    Parameters:
        G (networkx.Graph): The graph (should be a tree).
        root: The root node of current branch.
        width (float): Horizontal space allocated for this branch.
        vert_gap (float): Gap between levels of the tree.
        vert_loc (float): Vertical location of root.
        xcenter (float): Horizontal location of root.
    
    Returns:
        dict: A dictionary mapping each node to a position (x, y).
    """
    def _hierarchy_pos(G, root, left, right, vert_loc, pos=None, parent=None):
        if pos is None:
            pos = {root: ((left + right) / 2, vert_loc)}
        else:
            pos[root] = ((left + right) / 2, vert_loc)
        # Get children (neighbors excluding the parent)
        children = list(G.neighbors(root))
        if parent is not None and parent in children:
            children.remove(parent)
        if len(children) != 0:
            dx = (right - left) / len(children)
            next_left = left
            for child in children:
                next_right = next_left + dx
                pos = _hierarchy_pos(G, child, next_left, next_right, vert_loc - vert_gap, pos, root)
                next_left += dx
        return pos

    return _hierarchy_pos(G, root, 0, width, vert_loc)

def plot_general_tree(m: int) -> None:
    """
    Plot a general tree (implemented as a full binary tree) with m levels.
    
    The tree is generated using NetworkX's balanced_tree generator.
    For m levels, the tree height is set to m - 1 (with the root being level 0).
    
    Parameters:
        m (int): The total number of levels in the tree (m >= 1).
    
    Note:
        Although here we construct a binary tree (branching factor 2), the approach can be extended
        to general trees by modifying the branching factor.
    """
    if m < 1:
        raise ValueError("Number of levels must be at least 1.")
    # Generate a balanced binary tree: branching factor r=2 and height=m-1
    G = nx.balanced_tree(r=2, h=m-1)
    # Compute hierarchical positions to display the tree in levels
    pos = hierarchy_pos(G, root=0)
    nx.draw(G, pos, with_labels=True, node_size=600, node_color="lightgreen", arrows=False)
    plt.title(f"Binary Tree with {m} Levels")
    plt.show()

if __name__ == "__main__":
    # Set up command-line argument parsing to select the functionality.
    parser = argparse.ArgumentParser(
        description="Plot the Collatz 3n+1 directed graph or a general tree by level m."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--collatz", type=int, help="Starting integer n for the Collatz 3n+1 graph.")
    group.add_argument("--tree", type=int, help="Number of levels m for the general tree (binary tree).")
    args = parser.parse_args()
    coll=[]
    for i in range(2,10000):
        
            l=len(collatz_sequence(i))
            coll.append({"number":i,"collatz":l,"ratio":i/l})
        
        #print("15 * ",i//15,i, len(collatz_sequence(i)))
    sorted_ratio=sorted(coll, key=lambda x:x["collatz"])
    print(sorted_ratio)
    if args.collatz is not None:
        plot_collatz_graph(args.collatz)
        print(collatz_sequence(args.collatz))
    elif args.tree is not None:
        plot_general_tree(args.tree)
