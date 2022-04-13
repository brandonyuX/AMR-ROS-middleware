#This module includes the logic to decide which AMR is best suited for the job
import sys
# setting path
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
#The module will take input such as distance, availability, battery and priority
battscale=10


def makeDecision(rbt_list,rc_list,req_list,reqid):
    #This sortation only take in account the cost generated by Dijkstra
    rbt_list.sort(key=lambda x:x.cost,reverse=False)
    index=0
    finalrid=-1
    
    for rbt in rbt_list:
        index+=1
        #Scale battery requirement by cost
        battreq=rbt.cost/battscale
        #Take remainder of current battery level minus battery requirement
        battrem=rbt.battlvl-battreq
        #Find battery threshold of each robot
        battthres=(next((x for x in rc_list if x.rid == rbt.rid), None).battthres)
        #If remaining projected battery more then threshold, assign robot
        if battrem>battthres:
            finalrid=rbt.rid
            break

    if(finalrid!=-1):
        print('<D>From Decision Module : Robot {} is number {} choice from path calculation algorithm'.format(finalrid,index))
        print('<D>From Decision Module : Robot {} is projected to have {} percent of battery left after task is completed based on {} percent of battery required'.format(finalrid,battrem,battreq))
        print('<D>From Decision Module : Therefore, Robot {} should perform the task'.format(finalrid))
        index=0
        #Write a corresponding task to database
        #dbinterface.writeTask(finalrid,reqid,rbt_list,req_list)
        return (finalrid)
    else:
        print('<D>From Decision Module : No available robot found due to battery constraint!!')
        return -1
