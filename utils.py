
import time
import random
import warnings
import numpy as np
import osmnx.distance
import osmnx as ox
import networkx as nx
from threading import Thread
from datetime import timedelta
from multiprocessing import Process, Queue
from python_tsp.exact import solve_tsp_dynamic_programming

warnings.filterwarnings("ignore", category=UserWarning)
def calculate_shortest_path(G, origin_node, destination_node):
        return  ox.distance.shortest_path(G, origin_node, destination_node, weight='length',cpus=8)

def calculate_path_length(G, origin_node, destination_node):
        return nx.shortest_path_length(G, origin_node, destination_node, weight='length')

def func(G, origin_coordinates, destination_coordinates):
        origin_node = ox.get_nearest_node(G, origin_coordinates)
        destination_node = ox.get_nearest_node(G, destination_coordinates)
        # print('Converted from coordinates space to node space.')
        shortest_route_by_distance  = calculate_shortest_path(G, origin_node, destination_node)
        # print("Found shortest path by distance.")
        # print(f"{shortest_route_by_distance}")
        
        #for node in shortest_route_by_distance:
        #        n = G.nodes[node]
        #        print(f"Lattitude : {n['x']} , Longitude : {n['y']}")
        distance_in_meters = calculate_path_length(G, origin_node, destination_node)
        #print(f"Distance in meters : {distance_in_meters:.2f} meters.")
        return shortest_route_by_distance, distance_in_meters

def vrp(G, depot_locations, delivery_locations, q):

        all_locations = depot_locations + delivery_locations
        #print(f"All locations : {all_locations}")

        #G = ox.load_graphml("Dhaka.graphml")

        #route, distance = func(G, all_locations[0], all_locations[1])
        #q.put(route)
        route_data = [[func(G, location_1, location_2) if location_1 is not location_2 else [0, 0] for location_2 in all_locations] for location_1 in all_locations]
        #for location_1 in all_locations:
                #rows = [float(func(G, location_1, location_2)[1]) if location_1 is not location_2 else 0 for location_2 in all_locations]
                #for location_2 in all_locations:
                #        if location_1 is not location_2:
                #                rows.append(float(func(G, location_1, location_2)[1]))
                #        else:
                #                rows.append(0)
                # distance_matrix.append(rows)
        #print(distance_matrix)
        #print(route_data)
        #for row in route_data:
        #        print(len(row))
        #        print(row[0])
        #       break
        distance_matrix = np.array([np.array([element[1] for element in row]) for row in route_data])
        #print(distance_matrix)
        permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
        #print(permutation, '\n', distance)
        for idx in range(1, len(permutation)):
                i = permutation[idx]
                i_1 = permutation[idx - 1]
                data = route_data[i_1][i][0]
                q.put(data)
        q.put(route_data[-1][0][0])