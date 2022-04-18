#The module calculate the distance between 2 points given a source and destination location
from dijkstar import Graph, find_path

graph = Graph()
#Cost can be calculated using simple euclidean distance
graph.add_edge(1, 2, (110, 'Station 1'))
graph.add_edge(2, 1, (110, 'Station 1'))
graph.add_edge(3, 1, (110, 'Station 1'))
graph.add_edge(2, 3, (125, 'Station 2'))
graph.add_edge(3, 4, (108, 'Station 3'))
graph.add_edge(4, 5, (120, 'Station 4'))
graph.add_edge(5, 1, (120, 'Station 5'))
graph.add_edge(1,6, (120, 'Charging Station'))

graphdict={"Station 1":1,
            "Station 2":2,
            "Station 3":3,
            "Station 4":4,
            "Station 5":5,
            "Charging Station":6
            }


def cost_func(u, v, edge, prev_edge):
     length, name = edge
     if prev_edge:
        prev_name = prev_edge[1]
     else:
         prev_name = None
     cost = length
     if name != prev_name:
         cost += 10
     return cost


#Calculate shortest path given a source and destination
def calculate_shortest(src,dest):
    tempstr=(find_path(graph, graphdict[src], graphdict[dest], cost_func=cost_func))
    print('<P>From Path Calculate Module : {}\n'.format(tempstr))
    return (find_path(graph, graphdict[src], graphdict[dest], cost_func=cost_func).total_cost)


