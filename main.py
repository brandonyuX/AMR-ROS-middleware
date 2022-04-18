# This file will provide the main logic of the Middleware


#import interface.dbinterface as dbinterface
import interface.dbinterface as dbinterface
import interface.robotinterface as robotinterface
import interface.plcinterface as plcinterface
import logic.pathcalculate as pathcal
import logic.decision as decision
import time,datetime
import tkinter as tk
from flask import Flask, render_template
rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()

mapdict={"Station 1":0,
            "Station 2":1,
            "Station 3":2,
            "Station 4":3,
            "Station 5":4,
            "Charging Station":5
            }

def run():
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    #Print Current robot information

    print('=====Robot Configuration=====')
    for rc in rc_list:
        print(rc)
    print('\n')


    print('=====Robot Information=====')
    for rbt in rbt_list:
        print(rbt)
    print('\n')

    #Print Current request information
    print('=====Request Information=====')
    for req in req_list:
        print(req)
    print('\n')

    if len(req_list)>0:
        #Sort the request list by priority
        req_list.sort(key=lambda x:x.priority,reverse=False)
        #Loop through request list in order of priority
        for req in req_list:
            print('=====Start processing request with priority {}=====\n'.format(req.priority))
        
            #Loop through robot list 
            for rbt in rbt_list:
                print('Find possible route for robot {} from {} to {}\n'.format(rbt.rid,req.srcloc,req.destloc))
                print('Current robot position at {}'.format(rbt.currloc))
                print('=====> Sending route information to path calculate module to calculate cost')
                #Call path calculation module to calculate cost for each robot
                rbt.setCost(pathcal.calculate_shortest(rbt.currloc,req.srcloc)+pathcal.calculate_shortest(req.srcloc,req.destloc))
            
            print('=====> Sending path information to decision module to make a decision')
            #Call decision module to decide on which AMR to do the job
            rid=decision.makeDecision(rbt_list,rc_list,req_list,req.reqid)
            print('======End of decision=====\n')
            if(rid!=-1):
                print('=====> Send command to robot {} to perform task'.format(rid))
                robotinterface.publish_info(rid)
                dbinterface.updateReqStatus('PROCESSING',req.reqid)
                dbinterface.updateRbtStatus('TASK ASSIGNED',rid)
                dbinterface.writeTask(rid,req.reqid,rbt_list,req_list)
                robotinterface.publish_cmd(rid,mapdict[req.destloc])

            else:
                print('!!!!Failed to find appropriate robot for the task!!!!!')
            
            print('\n====================================END ROUTINE=========================================================')

          


            time.sleep(1)

#run()

def execute():
    run()

# print('M8M AMR Resource Management Software CLI')
# print('*Demonstration Script*')
# print('=====Robot Configuration=====')
# for rc in rc_list:
#     print(rc)
# print('\n')


# print('=====Robot Information=====')
# for rbt in rbt_list:
#     print(rbt)
# print('\n')
# print(datetime.datetime.now())
# while True:
#     print('Please press [enter] to run one interation of logic')
#     x=input()
#     print('====================================START ROUTINE=========================================================\n')
#     run()


    