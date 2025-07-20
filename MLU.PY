import heapq
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

#  existing weight, capacity, and demand matrices
weight_matrix = [
# A   B   C   D   E   F   G
 [ 0, 18, 0,  5,  0,  1, 0],  # A
 [ 18,  0, 7, 15, 14, 13, 4],  # B
 [ 0,  7, 0,  0,  3, 17, 0],   # C
 [ 5,  15, 0,  0,  0, 0, 16],  # D
 [ 0,  14, 3,  0,  0, 0, 19],  # E
 [ 1, 13,17,  0,  0, 0, 0],   # F
 [0, 4,  0,  16,  19, 0, 0]    # G
]

original_capacity_matrix = [
# A     B     C     D     E     F     G
 [0, 1000, 1000, 1000, 1000, 1000, 1000],  # A
 [1000, 0, 1000, 1000, 1000, 1000, 1000],  # B
 [1000, 1000, 0, 1000, 1000, 1000, 1000],  # C
 [1000, 1000, 1000, 0, 1000, 1000, 1000],  # D
 [1000, 1000, 1000, 1000, 0, 1000, 1000],  # E
 [1000, 1000, 1000, 1000, 1000, 0, 1000],  # F
 [1000, 1000, 1000, 1000, 1000, 1000, 0]   # G
]

capacity_matrix = [[val * 0.8 for val in row] for row in original_capacity_matrix]
demand_matrix = [
# A    B    C    D    E    F    G
[ 0, 300,   0, 500,   0, 200, 300],  # A
[300,   0, 600,   0, 250, 200,   0],  # B
[ 0, 600,   0,   0, 300,   0,   0],   # C
[500,   0,   0,   0,   0,   0, 350],  # D
[ 0, 250, 300,   0,   0,   0, 200],   # E
[200, 200,   0,   0,   0,   0, 250],  # F
[300,   0,   0, 350, 200, 250,   0]   # G
]
nodes = [1, 2, 3, 4, 5, 6, 7]

# Convert matrices to graph, demand, and capacity dictionaries
def matrix_to_graph(matrix, nodes):
    return {
        nodes[i]: {nodes[j]: matrix[i][j] for j in range(len(nodes)) if matrix[i][j] > 0}
        for i in range(len(nodes))
    }

def matrix_to_demand(matrix, nodes):
    return {
        (nodes[i], nodes[j]): matrix[i][j]
        for i in range(len(nodes))
        for j in range(len(nodes))
        if matrix[i][j] > 0
    }

def matrix_to_capacity(matrix, nodes):
    return {
        (nodes[i], nodes[j]): matrix[i][j]
        for i in range(len(nodes))
        for j in range(len(nodes))
        if matrix[i][j] > 0
    }

# Find all paths between two nodes
def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    paths = []
    for node in graph.get(start, {}):
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            paths.extend(newpaths)
    return paths

# K-Shortest Path calculation using Eppstein's algorithm
def eppstein_k_shortest_paths(graph, src, dst, K=2):
    def path_cost(path):
        return sum(graph[path[i]][path[i+1]] for i in range(len(path)-1))
    all_paths = find_all_paths(graph, src, dst)
    paths_with_costs = sorted([(path_cost(p), p) for p in all_paths])
    return paths_with_costs[:K]

# Helper function to get all links in the graph
def get_relevant_links(nodes):
    return sorted({(src, dst) for src in nodes for dst in nodes if src < dst})

# Compute k-shortest paths for all node pairs
def compute_paths(graph, nodes):
    all_k_paths = {}
    all_shortest_paths = {}
    for src in nodes:
        for dst in nodes:
            if src < dst:
                k_paths = eppstein_k_shortest_paths(graph, src, dst, K=2)
                if k_paths:
                    all_k_paths[(src, dst)] = k_paths
                    all_shortest_paths[(src, dst)] = k_paths[0]
    return all_k_paths, all_shortest_paths
def find_all_paths_with_costs(graph, src, dst):
    def dfs(current, end, path, cost):
        if current == end:
            all_paths.append((list(path), cost))
            return
        for neighbor in graph.get(current, {}):
            if neighbor not in path:
                path.append(neighbor)
                dfs(neighbor, end, path, cost + graph[current][neighbor])
                path.pop()

    all_paths = []
    dfs(src, dst, [src], 0)
    return all_paths


# Compute the link loads based on demand and paths
def compute_link_loads(demand, all_k_paths, graph, capacity_dict):
    link_loads = defaultdict(float)
    traffic_splits = {}
    for (src, dst), demand_value in demand.items():
        if (src, dst) not in all_k_paths:
            continue
        k_paths = all_k_paths[(src, dst)]
        min_cost = k_paths[0][0]
        equal_cost_paths = [p for cost, p in k_paths if abs(cost - min_cost) < 1e-6]
        if len(equal_cost_paths) > 1:
            path1, path2 = equal_cost_paths[:2]
            bottleneck_capacity = min(
                capacity_dict.get(tuple(sorted((path1[i], path1[i + 1]))), float('inf'))
                for i in range(len(path1) - 1)
            )
            if demand_value <= bottleneck_capacity:
                traffic_splits[(src, dst)] = [(path1, demand_value)]
                for i in range(len(path1) - 1):
                    u, v = sorted([path1[i], path1[i + 1]])
                    link_loads[(u, v)] += demand_value
            else:
                main_load = bottleneck_capacity
                alt_load = demand_value - main_load
                traffic_splits[(src, dst)] = [(path1, main_load), (path2, alt_load)]
                for path, load in [(path1, main_load), (path2, alt_load)]:
                    for i in range(len(path) - 1):
                        u, v = sorted([path[i], path[i + 1]])
                        link_loads[(u, v)] += load
        else:
            path = k_paths[0][1]
            traffic_splits[(src, dst)] = [(path, demand_value)]
            for i in range(len(path) - 1):
                u, v = sorted([path[i], path[i + 1]])
                link_loads[(u, v)] += demand_value
    return link_loads, traffic_splits

# Fortz cost function based on utilization
def fortz_cost_function(ogutil):
    if 0 <= ogutil < 1/3:
        return 1
    elif 1/3 <= ogutil < 2/3:
        return 3
    elif 2/3 <= ogutil < 9/10:
        return 10
    elif 9/10 <= ogutil < 1:
        return 70
    elif 1 <= ogutil < 1.1:
        return 500
    else:
        return 5000

def compute_max_utilization(link_loads, capacity_dict):
    max_utilization = 0
    for link in get_relevant_links(nodes):
        load = link_loads.get(link, 0)
        capacity = capacity_dict.get(link, 0)
        utilization = load / capacity if capacity > 0 else 0
        max_utilization = max(max_utilization, utilization)
    return max_utilization

def compute_extra_load(link_loads, capacity_dict):
    extra_load = 0
    for link in get_relevant_links(nodes):
        load = link_loads.get(link, 0)
        capacity = capacity_dict.get(link, 0)
        if load > capacity:
            extra_load += load - capacity
    return extra_load

def compute_new_cost_function(link_loads, capacity_dict):
    # Calculate Maximum Utilization (MU)
    max_utilization = compute_max_utilization(link_loads, capacity_dict)

    # Calculate Extra Load (sum of la - ca for all links where la > ca)
    extra_load = compute_extra_load(link_loads, capacity_dict)

    # Calculate Total Edges (E)
    total_edges = len(get_relevant_links(nodes))

    # Calculate the new cost function (Φ)
    new_cost_function = max_utilization + (extra_load / total_edges if total_edges > 0 else 0)

    return new_cost_function

def print_network_state(iteration, all_k_paths, link_loads, traffic_splits, capacity_dict,original_cap):
    print(f"\n{'='*600}\nIteration {iteration} Network State\n{'='*120}")
    print(f"\n{'Source → Destination':<22} {'All Paths':<500} {'K-Shortest Paths':<60}")
    print("="*600)

    for (src, dst) in sorted(all_k_paths.keys()):
        # All paths
        all_paths = find_all_paths_with_costs(graph, src, dst)
        all_paths_str = "; ".join(["→".join(map(str, p)) + f" (cost: {c})" for p, c in all_paths])

        # K-shortest paths
        k_paths = all_k_paths[(src, dst)]
        k_paths_str = "; ".join(["→".join(map(str, p)) + f" (cost: {c})" for c, p in k_paths])

        print(f"{src} → {dst:<19} {all_paths_str:<500} {k_paths_str}")


    print("\nLink Statistics:")
    print(f"{'Link':<10} {'Load':<10} {'ThresholdCapacity':<20} {'Utilization':<25}{'Status':<10}  {'Fortz Cost':<10}")
    print("="*150)

    total_fortz_cost = 0
    utilizations = []
    origUtil=[]

    # For each link, calculate utilization and Fortz cost
    for link in get_relevant_links(nodes):
        load = link_loads.get(link, 0)
        capacity = capacity_dict.get(link, 0)
        utilization = load / capacity if capacity > 0 else 0
        utilizations.append(utilization)
        status = "CONGESTED" if utilization > 1 else "OK"
        fortz_cost = fortz_cost_function(utilization)
        total_fortz_cost += fortz_cost
        print(f"{link[0]}-{link[1]:<8} {load:<10.2f} {capacity:<20}  {utilization:<25.2f} {status:<10} {fortz_cost:<10}")


    # Calculate the new cost function for the entire network
    new_cost_function = compute_new_cost_function(link_loads, capacity_dict)

    # Print Fortz Cost and New Cost Function
    print(f"\nTotal Fortz Cost: {total_fortz_cost}")
    print(f"New Cost Function (Φ): {new_cost_function:.2f}")



# Optimize network and print the MLU
def optimize_network(max_iterations=15):
    global graph, demand, capacity_dict
    graph = matrix_to_graph(weight_matrix, nodes)
    demand = matrix_to_demand(demand_matrix, nodes)
    capacity_dict = matrix_to_capacity(capacity_matrix, nodes)
    original_cap=matrix_to_capacity(original_capacity_matrix, nodes)
    current_weight_matrix = [row[:] for row in weight_matrix]

    for iteration in range(1, max_iterations+1):
        graph = matrix_to_graph(current_weight_matrix, nodes)
        all_k_paths, _ = compute_paths(graph, nodes)
        link_loads, traffic_splits = compute_link_loads(demand, all_k_paths, graph, capacity_dict)
        print_network_state(iteration, all_k_paths, link_loads, traffic_splits, capacity_dict,original_cap)

        congested_links = [
            link for link in get_relevant_links(nodes)
            if link_loads.get(link, 0) / capacity_dict.get(link, 1) > 1
        ]
        if not congested_links:
            print("\nOptimization complete - no congested links remaining!")
            break

        alternative_paths = {}
        for link in congested_links:
            src, dst = link
            all_paths = find_all_paths(graph, src, dst)
            alternative_paths[link] = [
                (path, sum(graph[path[i]][path[i+1]] for i in range(len(path)-1)))
                for path in all_paths
                if all((path[i], path[i+1]) != link and (path[i+1], path[i]) != link for i in range(len(path)-1))
            ]

        alternative_paths = {}
        for link in congested_links:
            src, dst = link
            all_paths = find_all_paths(graph, src, dst)
            alternative_paths[link] = [
                (path, sum(graph[path[i]][path[i+1]] for i in range(len(path)-1)))
                for path in all_paths
                if all((path[i], path[i+1]) != link and (path[i+1], path[i]) != link for i in range(len(path)-1))
            ]

        for link in congested_links:
            paths = alternative_paths.get(link, [])
            if not paths:
                continue
            alt_path, alt_cost = min(paths, key=lambda x: x[1])
            current_cost = current_weight_matrix[link[0]-1][link[1]-1]
            x = (alt_cost - current_cost) / 2
            if x <= 0:
                continue
            current_weight_matrix[link[0]-1][link[1]-1] += x
            current_weight_matrix[link[1]-1][link[0]-1] += x
            for i in range(len(alt_path)-1):
                u, v = alt_path[i], alt_path[i+1]
                if current_weight_matrix[u-1][v-1] > x:
                    current_weight_matrix[u-1][v-1] = max(1, current_weight_matrix[u-1][v-1] - x)
                    current_weight_matrix[v-1][u-1] = max(1, current_weight_matrix[v-1][u-1] - x)
                    break

        print("\nAdjusted Weight Matrix:")
        for row in current_weight_matrix:
            print(row)



    # After optimization, calculate MLU (Maximum Link Utilization)
    max_utilization = max(
        link_loads.get(link, 0) / capacity_dict.get(link, 1)
        for link in get_relevant_links(nodes)
    )


    print(f"\n\n{'='*50}\n{'MAXIMUM LINK UTILIZATION (MLU)'}\n{'='*50}")
    print(f"MLU = {max_utilization:.2f}")
    print([round(link_loads.get(link, 0) / capacity_dict.get(link, 1), 2)
       for link in get_relevant_links(nodes)])
    fortz_costs = {
    link: fortz_cost_function(link_loads.get(link, 0) / capacity_dict.get(link, 1))
    for link in get_relevant_links(nodes)
    }
    print([
    round(fortz_cost_function(link_loads.get(link, 0) / capacity_dict.get(link, 1)), 2)
    for link in get_relevant_links(nodes)
    ])


# Run the optimizer
optimize_network()

