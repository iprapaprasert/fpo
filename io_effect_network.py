import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Parameters
file_path = "C:/notebooks/networkx/network_food.xlsx"
sheet_name = "Total effect_26"
node_attr_sheet_name = "node_attr"
node_size_col = "total_effect_size"
node_sector_col = "sector"
target_nodes = ["Construction", "Real Estate"]

# Data preparation
## Load data from Excel
adj_matrix = pd.read_excel(file_path, index_col=0, sheet_name=sheet_name)
node_attr_df = pd.read_excel(file_path, index_col=0, sheet_name=node_attr_sheet_name)

## Convert node sizes and sectors to dictionaries
node_sizes = node_attr_df[node_size_col].to_dict()
node_sectors = node_attr_df[node_sector_col].to_dict()

# Create directed graph
G = nx.from_pandas_adjacency(adj_matrix, create_using=nx.DiGraph)

## Remove self-loops (edges where u == v)
G.remove_edges_from(nx.selfloop_edges(G))

## Find all nodes connected to "Food Manufacturing" (both in and out edges)
connected_nodes = set()
for target_node in target_nodes:
    connected_nodes |= set(nx.descendants(G, target_node)) | set(nx.ancestors(G, target_node)) | {target_node}

## Create a subgraph with only the connected nodes
G_sub = G.subgraph(connected_nodes)

## Extract edge weights for visualization
edge_weights = [G_sub[u][v]['weight'] for u, v in G_sub.edges()]
max_weight = max(edge_weights) if edge_weights else 1
edge_widths = [15 * (w / max_weight) for w in edge_weights]

# Extract and normalize node sizes
min_size = min(node_sizes.values()) if node_sizes else 1
max_size = max(node_sizes.values()) if node_sizes else 1
node_size_scaled = {node: 500 + 1500 * ((node_sizes[node] - min_size) / (max_size - min_size + 1e-6)) for node in G_sub.nodes()}

# Define sector-based colors
sector_colors = {
    "Agriculture": "green",
    "Industrial": "red",
    "Services": "yellow"
}

# Assign colors to nodes and edges
node_colors = []
edge_colors = []
for node in G_sub.nodes():
    if node in target_nodes:
        node_colors.append("blue")
    else:
        node_colors.append(sector_colors.get(node_sectors.get(node, ""), "gray"))

for u, v in G_sub.edges():
    if u in target_nodes:
        edge_colors.append("blue")
    else:
        edge_colors.append(sector_colors.get(node_sectors.get(u, ""), "gray"))

# Draw the filtered graph
pos = nx.spring_layout(G_sub, center=(0, 0), scale=1.0)
pos[target_node] = (-1, 0)
plt.figure(figsize=(10, 8))
nx.draw(
    G_sub, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors, 
    node_size=[node_size_scaled[node] for node in G_sub.nodes()], 
    arrows=True, width=edge_widths, font_size=10)
plt.show()
