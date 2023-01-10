#The module calculate the distance between 2 points given a source and destination location
from dijkstar import Graph, find_path

graph = Graph()
#Cost can be calculated using simple euclidean distance

graph.add_edge(1,3,(100,'Charging Station'))
graph.add_edge(3,1,(100,'Turning Point'))
graph.add_edge(2,3,(100,'Unscrambling Station'))
graph.add_edge(3,2,(100,'Turning Point'))
graph.add_edge(3,4,(100,'Warehouse'))
graph.add_edge(4,3,(100,'Turning Point'))
graph.add_edge(4,5,(100,'Packing Station'))
graph.add_edge(5,4,(100,'Warehouse'))
graph.add_edge(3,6,(100,'Custom Location'))
graph.add_edge(6,3,(100,'Custom Location'))
graph.add_edge(5,7,(100,'Custom Location'))
graph.add_edge(7,5,(100,'Custom Location'))




graphdict={"Charging Station":1,
            "Unscrambling Station":2,
            "Turning Point":3,
            "Warehouse":4,
            "Packing Station":5,
            "Custom Location 1":6
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

def cal_shortest_edge(e1,e2):
    tempstr=(find_path(graph, e1, e2))
    print('<P>From Path Calculate Module : {}\n'.format(tempstr))

def test():
    pathlist=find_path(graph,1,2, cost_func=cost_func).nodes
    for path in pathlist:
        key = next(key for key, value in graphdict.items() if value == path)
        print(key+'-->')
