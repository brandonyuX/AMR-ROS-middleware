import sys
import time
import datetime
import threading
# setting path
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.robotinterface as robotinterface

production=False
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
    #dbinterface.startup()
    
  
    # list=dbinterface.getReqList()
    # for item in list:
    #     print(item)
    #Initialze robot interface
    #robotinterface.startup()
    time.sleep(5)
    loop=True
    while(loop):
        #print('=====Start Async task get=====')
        time.sleep(2)
        tsklist=dbinterface.getTaskListTop()
        


        for i,tsk in enumerate(tsklist):
            #tskq.clear()
            #print(tsk)
            tskq.append([])
            splitloc=str(tsk.destloc).split(';')
            for loc in splitloc:
                #print(tsk.rid)
                tskq[i].append(loc)
        
        if len(tsklist)>0:
           
            #If there are active tasks in tasklist, loop through task list to assign job to robot
            for i,tsk in enumerate(tsklist):
              

                #Do not execute next step when task is still processing
                if(int(tsk.exec)==1):
                    #dbinterface.writeLog('ms','Task {} for robot {} on step {} is executing'.format(tsk.tid,tsk.rid,tsk.currstep-1),False)
                    #print('Task {} for robot {} on step {} still executing'.format(tsk.tid,tsk.rid,tsk.currstep-1))
                    continue
                    
                    
                    
                else:

                    # if(tsk.currstep>1):
                    #     for i in range(1,tsk.currstep):
                    #         subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,i)
                    #         if(subtsk[0].at=='Move'):
                    #             #Pop from list if previous move has been established
                    #             tskq[i].pop(0)
                    #Start execution of subtask
                    #Get action type of subtask 
                   
                    #print(tsk.destloc)
                   
                    #print('Sending Command to Robot {}.\n Current Step: {} End Step: {}'.format(tsk.rid,tsk.currstep,tsk.endstep))
                    if(tsk.currstep>tsk.endstep):
                        #print('End of execution for task {}'.format(tsk.tid))
                        dbinterface.writeLog('ms','End of execution for task {}'.format(tsk.tid),True)
                        dbinterface.incStep(tsk.tid,tsk.endstep,True)
                        dbinterface.setExecute(0,tsk.tid)
                        dbinterface.updateReqStatus('REQUEST COMPLETED',tsk.reqid)
                    

                   
                    
                    if(tsk.currstep<=tsk.endstep):
                        
                        dbinterface.updateReqStatus('PROCESSING REQUEST',tsk.reqid)
                        subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,tsk.currstep)
                        
                        #Define multiple request task
                        if(subtsk[0].at=='Move'):
                            #print('attempt move')
                            sname=tskq[i].pop(0)
                            #print(mapdict[sname])
                            #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                            dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                            #print('<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,sname))
                            dbinterface.writeLog('ms','<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,sname),True)
                            #Send command to robot interface to run this step
                            #print(mapdict[sname])
                            if production:
                                robotinterface.publish_cmd(tsk.rid,sname)
                                dbinterface.setExecute(1,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                            else:
                                dbinterface.setExecute(1,tsk.tid) 
                                time.sleep(5)
                                dbinterface.writeLog('ms','Move Completed',True)
                                dbinterface.setExecute(0,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                                
                        #Misc location
                        if(subtsk[0].at=='Misc'):
                            dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                            dbinterface.writeLog('ms','<MS>Sending wait command to robot {}.'.format(tsk.rid),True)
                            #Send approach signal to host PLC
                            dbinterface.setExecute(1,tsk.tid)
                            #Wait for user to press button to confirm operation done
                            
                            time.sleep(5)
                            
                            dbinterface.writeLog('ms','<MS>Wait Completed',True)
                            dbinterface.setExecute(0,tsk.tid)
                            dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                        

                        #Loading subtask         
                        if(subtsk[0].at=='Load'):
                            #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                            #print('<MS>Sending load command to robot {}.'.format(tsk.rid))
                            dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                            dbinterface.writeLog('ms','<MS>Sending load command to robot {}.'.format(tsk.rid),True)
                            dbinterface.setExecute(1,tsk.tid)
                            #Test set execute to false after 5 seconds
                            if production:
                                robotinterface.jack_up(tsk.rid)
                            #Wait for load to complete
                            time.sleep(25)
                            dbinterface.writeLog('ms','<MS>Load Completed',True)
                            dbinterface.setExecute(0,tsk.tid)
                            dbinterface.incStep(tsk.tid,tsk.currstep+1,False)

                        #Unload subtask
                        if(subtsk[0].at=='Unload'):
                            #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                            dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                            #print('<MS>Sending unload command to robot {}.'.format(tsk.rid))
                            dbinterface.writeLog('ms','<MS>Sending unload command to robot {}.'.format(tsk.rid),True)
                            dbinterface.setExecute(1,tsk.tid)
                            #Test set execute to false after 5 seconds
                            if production:
                                robotinterface.jack_down(tsk.rid)
                            #Wait for unload to complete
                            time.sleep(25)
                            #print('<MS>Unload Completed')
                            dbinterface.writeLog('ms','<MS>Unload Completed',True)
                            dbinterface.setExecute(0,tsk.tid)
                            dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                #time.sleep(2)
  
            
        else:
            #print('=====No task found yet. Polling...')
            dbinterface.writeLog('ms','No Task Found',False)
            time.sleep(2)
            


def startup():
    
    print('<MS>Master Scheduler start up')
    t1=threading.Thread(target=tskpolling,daemon=True)
    t1.start()
    #t1.join()
#tskpolling()


