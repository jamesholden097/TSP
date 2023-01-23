"""Simple Vehicles Routing Problem (VRP).

   This is a sample using the routing library python wrapper to solve a VRP
   problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.

   Distances are in meters.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model():
	"""Stores the data for the problem."""
	data = {}
	data['distance_matrix'] = [
		[
			0, 11, 6, 6, 9, 17, 9, 11, 8, 14, 18, 28
		],
		[
			11, 0, 10, 12, 13, 17, 9, 17, 12, 13, 18, 16
		],
		[
			6, 10, 0, 4, 4, 21, 11, 9, 3, 16, 20, 24
		],
		[
			6, 12, 4, 0, 5, 21, 12, 6, 5, 18, 22, 29
		],
		[
			9, 13, 4, 5, 0, 23, 15, 6, 1, 20, 24, 28
		],
		[
			17, 17, 21, 21, 23, 0, 10, 25, 23, 8, 6, 16
		],
		[
			9, 9, 11, 12, 15, 10, 0, 17, 14, 8, 12, 33
		],
		[
			11, 17, 9, 5, 6, 25, 17, 0, 6, 22, 26, 32
		],
		[
			8, 12, 3, 5, 1, 23, 14, 6, 0, 19, 24, 27
		],
		[
			14, 13, 16, 18, 20, 8, 8, 22, 19, 0, 11, 23
		],
		[
			18, 18, 20, 22, 24, 6, 12, 26, 24, 11, 0, 20
		],
		[
			28, 16, 24, 29, 28, 16, 33, 32, 27, 23, 20, 0
		]

	]
	data['num_vehicles'] = 1
	data['depot'] = 0
	return data


def print_solution(data,  manager,  routing,  solution):
	"""Prints solution on console."""
	print(f'Objective: {solution.ObjectiveValue()}')
	max_route_distance = 0
	for vehicle_id in range(data['num_vehicles']):
		index = routing.Start(vehicle_id)
		plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
		route_distance = 0
		while not routing.IsEnd(index):
			plan_output += ' {} -> '.format(manager.IndexToNode(index))
			previous_index = index
			index = solution.Value(routing.NextVar(index))
			route_distance += routing.GetArcCostForVehicle(previous_index,  index,  vehicle_id)
			#print(routing.GetArcCostForVehicle(previous_index,  index,  vehicle_id))
		plan_output += '{}\n'.format(manager.IndexToNode(index))
		plan_output += 'Distance of the route: {}km\n'.format(route_distance)
		print(plan_output)
		max_route_distance = max(route_distance,  max_route_distance)
	print('Maximum of the route distances: {}km'.format(max_route_distance))



def main():
	"""Entry point of the program."""
	# Instantiate the data problem.
	data = create_data_model()

	# Create the routing index manager.
	manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
										   data['num_vehicles'], data['depot'])

	# Create Routing Model.
	routing = pywrapcp.RoutingModel(manager)


	# Create and register a transit callback.
	def distance_callback(from_index,  to_index):
		"""Returns the distance between the two nodes."""
		# Convert from routing variable Index to distance matrix NodeIndex.
		from_node = manager.IndexToNode(from_index)
		to_node = manager.IndexToNode(to_index)
		return data['distance_matrix'][from_node][to_node]

	transit_callback_index = routing.RegisterTransitCallback(distance_callback)

	# Define cost of each arc.
	routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

	# Add Distance constraint.
	dimension_name = 'Distance'
	routing.AddDimension(
		transit_callback_index, 
		0, 	# no slack
		3000,   # vehicle maximum travel distance
		True,   # start cumul to zero
		dimension_name)
	distance_dimension = routing.GetDimensionOrDie(dimension_name)
	distance_dimension.SetGlobalSpanCostCoefficient(100)

	# Setting first solution heuristic.
	search_parameters = pywrapcp.DefaultRoutingSearchParameters()
	search_parameters.first_solution_strategy = (
		routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

	# Solve the problem.
	solution = routing.SolveWithParameters(search_parameters)

	# Print solution on console.
	if solution:
		print_solution(data,  manager,  routing,  solution)
	else:
		print('No solution found !')


if __name__ == '__main__':
	main()