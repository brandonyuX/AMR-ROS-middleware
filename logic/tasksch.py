import sys
import time
import datetime
import threading
# setting path
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.robotinterface as robotinterface

tskq=[]
dbmaphash={'STN1' : 'Station 1', 'STN2' : 'Station 2','STN3':'Station 3','STN4':'Station 4','STN5':'Station 5'}
mapdict={"STN1":0,
            "STN2":1,
            "STN3":2,
            "STN4":3,
            "STN5":4,
            "Charging Station":5
            }
def tskpolling():
    #Initialize database connection
    dbinterface.startup()
    rbt_list=dbinterface.getRobotList()
    for rbt in rbt_list:
        print(rbt)
    # list=dbinterface.getReqList()
    # for item in list:
    #     print(item)
    #Initialze robot interface
    robotinterface.startup()
    
    loop=True
    while(loop):
        #print('=====Start Async task get=====')
        tsklist=dbinterface.getTaskList()
        for i,tsk in enumerate(tsklist):
            tskq.append([])
            splitloc=str(tsk.destloc).split(';')
            for loc in splitloc:
                #print(tsk.rid)
                tskq[i].append(loc)
        
        if len(tsklist)>0:
            #print("=====Master Scheduler Cycle======")
            time.sleep(1)
            #If there are active tasks in tasklist, loop through task list to assign job to robot
            for i,tsk in enumerate(tsklist):
                
                #Do not process if task is marked as complete
                if(int(tsk.comp)==1):
                    print('<MS>Completed all steps for task {}'.format(tsk.tid))
                    loop=False
                    break

                #Do not execute next step when task is still processing
                elif(int(tsk.exec)==1):
                    #print('Task {} for robot {} on step {} still executing'.format(tsk.tid,tsk.rid,tsk.currstep-1))
                    continue
                    
                    
                else:

                    if(tsk.currstep>1):
                        for i in range(1,tsk.currstep):
                            subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,i)
                            if(subtsk[0].at=='Move'):
                                #Pop from list if previous move has been established
                                tskq[i].pop(0)
                    #Start execution of subtask
                    #Get action type of subtask 
                   
                    #print(tsk.destloc)
                   
                    #print('Sending Command to Robot {}.\n Current Step: {} End Step: {}'.format(tsk.rid,tsk.currstep,tsk.endstep))
                    if(tsk.currstep>tsk.endstep):
                        dbinterface.incStep(tsk.tid,tsk.endstep,True)
                        dbinterface.setExecute(0,tsk.tid)
                    

                   

                    if(tsk.currstep<=tsk.endstep):
                        subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,tsk.currstep)
                        if(subtsk[0].at=='Move'):
                            sname=tskq[i].pop(0)
                            #print(mapdict[sname])
                            print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                            print('<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,sname))
                            #Send command to robot interface to run this step
                            #print(mapdict[sname])
                            cmdres=robotinterface.publish_cmd(tsk.rid,mapdict[sname])
                            if(cmdres):
                                dbinterface.setExecute(1,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                            else:
                                print('<ERR>Robot connection failed. Terminating loop.')
                                loop=False
                        if(subtsk[0].at=='Load'):
                            print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                            print('<MS>Sending load command to robot {}.'.format(tsk.rid))
                            dbinterface.setExecute(1,tsk.tid)
                            #Test set execute to false after 5 seconds
                            
                            robotinterface.jack_up(tsk.rid)
                            #Wait for load to complete
                            time.sleep(25)
                            print('<MS>Load Completed')
                            dbinterface.setExecute(0,tsk.tid)
                            dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                        if(subtsk[0].at=='Unload'):
                            print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                            print('<MS>Sending unload command to robot {}.'.format(tsk.rid))
                            dbinterface.setExecute(1,tsk.tid)
                            #Test set execute to false after 5 seconds
                            robotinterface.jack_down(tsk.rid)
                            #Wait for unload to complete
                            time.sleep(25)
                            print('<MS>Unload Completed')
                            dbinterface.setExecute(0,tsk.tid)
                            dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                #time.sleep(2)
  
            
        else:
            print('=====No task found yet. Polling...')
            time.sleep(0.5)
            



# t1=threading.Thread(target=tskpolling)
# t1.start()
# t1.join()
tskpolling()


