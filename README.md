Minimizing the Maximum Link Utilization in SDN

This repository implements an Enhanced Heuristic Algorithm to minimize the Maximum Link Utilization (MLU) in a Software Defined Network (SDN). The approach dynamically adjusts OSPF link weights, computes K-shortest paths, detects congestion, and redistributes traffic to optimize overall network performance.


Overview

Modern networks often suffer from link congestion due to uneven traffic distribution. This project models an undirected network graph with:
- Nodes (routers/devices)
- Links with weights (OSPF costs)
- Link capacities
- Traffic demand matrix

The goal is to:
- Compute K = 2 shortest paths for each source–destination pair using Eppstein’s algorithm.
- Calculate link loads and utilization.
- Identify congested links when utilization exceeds 80% of their capacity.
- Adjust OSPF weights dynamically using a cost offset.
- Split traffic proportionally between congested and alternative paths.
- Iterate until maximum link utilization is minimized and all congestion is resolved.



Key Features

- Computes all paths and selects K-shortest paths for every node pair  
- Dynamic weight adjustment using cost offset logic  
- Realistic demand, capacity, and weight matrices  
- Link load and utilization computation per iteration  
- Fortz cost function to evaluate severity of congestion  
- Detailed output for each iteration  
- Final MLU (Maximum Link Utilization) report



Project Structure

- weight_matrix: Initial OSPF link cost matrix  
- capacity_matrix: Maximum link capacity matrix (with 80% threshold)  
- demand_matrix: Traffic demands between node pairs  
- matrix_to_graph, matrix_to_demand, matrix_to_capacity: Matrix converters  
- eppstein_k_shortest_paths: Computes K-shortest paths using Eppstein’s algorithm  
- compute_link_loads: Calculates link traffic loads  
- fortz_cost_function: Evaluates congestion cost  
- optimize_network(): Main iterative heuristic loop  
- print_network_state(): Shows detailed per-iteration output



How to Run

1. Clone this repository
2. Install dependencies
3. Run the main script

Output

At each iteration, the script displays:
- All possible paths and the selected K-shortest paths for each pair
- Link loads, threshold capacities, utilization, congestion status
- Fortz cost for each link
- Updated link weights after weight adjustment
- Final Maximum Link Utilization (MLU) after all iterations

Example output:
Link: 2–3 | Load: 1200 | Capacity: 800 | Utilization: 1.50 | Status: CONGESTED | Fortz Cost: 5000
...
MLU = 0.92
