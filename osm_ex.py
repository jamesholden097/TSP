import osmnx as ox
import networkx as nx
from datetime import timedelta
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning) 
start_time = time.perf_counter()
# ox.config(log_console=True)
'''
# The place where your 2 points are located. It will be used to create a graph from the OSM data
# In this example, the 2 points are two addresses in Manhattan, so we choose "Manhattan"
# It could be a bounding box too, or an area around a point
graph_area = [" Uttara, Dhaka, Bangladesh", "Gulshan, Dhaka, Bangladesh"]

# Create the graph of the area from OSM data. It will download the data and create the graph
G = ox.graph_from_place(graph_area, network_type='drive')

# OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# Save graph to disk if you want to reuse it
#ox.save_graphml(G, "Manhattan.graphml")
'''
# Load the graph
G = ox.load_graphml("Dhaka.graphml")
print('Done loading')
# Plot the graph
#fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)

# Two pairs of (lat,lng) coordinates
origin_coordinates = (23.777380940199116, 90.41641665057213)
destination_coordinates = (23.867507937892775, 90.39508294789347)

# If you want to take an address (osmx will use Nominatim service for this)
# origin_coordinates = ox.geocode("2 Broad St, New York, NY 10005")

# In the graph, get the nodes closest to the points
#origin_node = ox.distance.nearest_nodes(G, origin_coordinates[0], origin_coordinates[1])
#destination_node = ox.distance.nearest_nodes(G, destination_coordinates[0], destination_coordinates[1])
origin_node = ox.get_nearest_node(G, origin_coordinates)
destination_node = ox.get_nearest_node(G, destination_coordinates)
print('Converted from coordinates space to node scape.')

# Get the shortest route by distance
shortest_route_by_distance = ox.distance.shortest_path(G, origin_node, destination_node, weight='length')
print("Found shortest path by distance.")
for node in shortest_route_by_distance:
    n = G.nodes[node]
    print(f"Lattitude : {n['x']} , Longitude : {n['y']}")

# Plot the shortest route by distance
#fig, ax = ox.plot_graph_route(G, shortest_route_by_distance, route_color='y', route_linewidth=6, node_size=0)

# Get the shortest route by travel time
shortest_route_by_travel_time = ox.distance.shortest_path(G, origin_node, destination_node, weight='travel_time')
print(f"Found shortest path by time : {shortest_route_by_travel_time}.")

# Plot the shortest route by travel time
#fig, ax = ox.plot_graph_route(G, shortest_route_by_travel_time, route_color='y', route_linewidth=6, node_size=0)


# Get the travel time, in seconds
# Note here that we use "nx" (networkx), not "ox" (osmnx)
travel_time_in_seconds = nx.shortest_path_length(G, origin_node, destination_node, weight='travel_time')
print(f"Travel Time : {travel_time_in_seconds:.2f} seconds.")

#The travel time in "HOURS:MINUTES:SECONDS" format
travel_time_in_hours_minutes_seconds = f"{timedelta(seconds=travel_time_in_seconds)}"
print(f"Travel time in H:M:S {travel_time_in_hours_minutes_seconds}")

# Get the distance in meters
distance_in_meters = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
print(f"Distance in meters : {distance_in_meters:.2f} meters.")
print(f"Time taken to solve : {(time.perf_counter() - start_time):.2f} seconds.")
exit(0)
start_time = time.perf_counter()
# Plot the 2 routes
fig, ax = ox.plot_graph_routes(G, routes=[shortest_route_by_distance, shortest_route_by_travel_time], route_colors=['r', 'y'], route_linewidth=6, node_size=0)
print(f"Time taken to plot : {(time.perf_counter() - start_time):.2f } seconds.")
