#The module calculate the distance between 2 points given a source and destination location
from dijkstar import Graph, find_path
import sys

sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface

graph = Graph()
#Cost can be calculated using simple euclidean distance

graph.add_edge(1,4,(100,'Charging Station'))
graph.add_edge(4,1,(100,"TPDown"))

graph.add_edge(2,3,(100,'Stn 1'))
graph.add_edge(3,2,(100,'TPUp'))

graph.add_edge(3,4,(100,'TPUp'))
graph.add_edge(4,3,(100,"TPDown"))

graph.add_edge(4,5,(100,'TPDown'))
graph.add_edge(5,4,(100,"TPLeft"))

graph.add_edge(3,5,(100,'TPUp'))
graph.add_edge(5,3,(100,"TPLeft"))

# graph.add_edge(4,9,(100,'TPDown'))
# graph.add_edge(9,4,(100,"MR"))

graph.add_edge(4,10,(100,'TPDown'))
graph.add_edge(10,4,(100,"PL"))

graph.add_edge(5,6,(100,'TPLeft'))
graph.add_edge(6,5,(100,"WH"))

graph.add_edge(6,7,(100,'WH'))
graph.add_edge(7,6,(100,"Stn 6"))

graph.add_edge(5,7,(100,'TPLeft'))
graph.add_edge(7,5,(100,"Stn 6"))

graph.add_edge(7,8,(100,'Stn 6'))
graph.add_edge(8,7,(100,"FL"))

graph.add_edge(5,9,(100,'TPLeft'))
graph.add_edge(9,5,(100,"MR"))

graphdict={"CHR":1,
            "Stn1":2,
            "TPUp":3,
            "TPDown":4,
            "TPLeft":5,
            "WH":6,
            "Stn6":7,
            "FL":8,
            "MR":9,
            "PL":10
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
# function to return key for any value
def get_key(val):
    for key, value in graphdict.items():
        if val == value:
            return key
 
    return "key doesn't exist"

#Calculate shortest path given a source and destination
def calculate_shortest(src,dest):
    tempstr=(find_path(graph, graphdict[src], graphdict[dest], cost_func=cost_func))
    print('<P>From Path Calculate Module : {}\n'.format(tempstr))
    return (find_path(graph, graphdict[src], graphdict[dest], cost_func=cost_func).total_cost)

def generate_path_simple(dest):
    strlist=[]
    currentloc=dbinterface.getRbtLoc(1)
    #Find path from current location to source
    curr2src=find_path(graph, graphdict[currentloc], graphdict[dest], cost_func=cost_func)
    for i in range(len(curr2src[0])):
        val=curr2src[0][i]
        strlist.append(get_key(val))
    
    
    return (strlist)
    
#Generate path based on graph
def generate_path(src,dest,dest2):
    strlist=[]
    currentloc=dbinterface.getRbtLoc(1)

    #Find path from current location to source
    curr2src=find_path(graph, graphdict[currentloc], graphdict[src], cost_func=cost_func)

    #Find path from source to destination
    src2dest=(find_path(graph, graphdict[src], graphdict[dest], cost_func=cost_func))
    
    
    
    
    for i in range(len(curr2src[0])):
        val=curr2src[0][i]
        strlist.append(get_key(val))
    strlist.append('SRC')

    for i in range(len(src2dest[0])-1):
        val=src2dest[0][i+1]
        strlist.append(get_key(val))
    strlist.append('DEST')

    if(dest2!=''):
            #Find path from dest to dest 2
            dest2dest2=(find_path(graph, graphdict[dest], graphdict[dest2], cost_func=cost_func))
            for i in range(len(dest2dest2[0])-1):
                val=dest2dest2[0][i+1]
                strlist.append(get_key(val))
            strlist.append('DEST2')
       
        
    
    ret_str=";".join(strlist)
    return (ret_str)

def cal_shortest_edge(e1,e2):
    tempstr=(find_path(graph, e1, e2))
    print('<P>From Path Calculate Module : {}\n'.format(tempstr))

def test():
    pathlist=find_path(graph,1,2, cost_func=cost_func).nodes
    for path in pathlist:
        key = next(key for key, value in graphdict.items() if value == path)
        print(key+'-->')

# dbinterface.startup()
#print(generate_path('WH','Stn1'))
# # for i in range(len(pathinfo[0])):

# #     print(pathinfo[0][i])
# print(generate_path_simple('Stn1'))
# tstring='Stn1'
# sstring=tstring.split(';')
# print(sstring)