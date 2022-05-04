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

def tskpolling():
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
            print("=====Task Found======")
            #If there are active tasks in tasklist, loop through task list to assign job to robot
            for i,tsk in enumerate(tsklist):
                
                #Do not process if task is marked as complete
                if(int(tsk.comp)==1):
                    print('Completed all steps for request {}'.format(tsk.reqid))
                    loop=False

                #Do not execute next step when task is still processing
                elif(int(tsk.exec)==1):
                    print('Task {} on step {} still executing'.format(tsk.tid,tsk.currstep))
                    
                    
                else:
                    #Start execution of subtask
                    #Get action type of subtask 
                   
                    #print(tsk.destloc)
                    subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,tsk.currstep)
                    if(subtsk[0].at=='Move'):
                        print('Sending move command to robot {} bound for {}'.format(tsk.rid,tskq[i].pop(0)))
                    if(subtsk[0].at=='Load'):
                        print('Sending load command to robot {}.'.format(tsk.rid))
                    if(subtsk[0].at=='Unload'):
                        print('Sending unload command to robot {}.'.format(tsk.rid))
                    #print('Sending Command to Robot {}.\n Current Step: {} End Step: {}'.format(tsk.rid,tsk.currstep,tsk.endstep))
                    if(tsk.currstep+1>tsk.endstep):
                        dbinterface.incStep(tsk.tid,tsk.endstep,True)
                        dbinterface.stepComplete(tsk.tid)
                    else:
                        dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                    
                time.sleep(3)
  
            
        else:
            print('=====No task found yet. Polling...')
            time.sleep(0.5)
            



# t1=threading.Thread(target=tskpolling)
# t1.start()
# t1.join()
tskpolling()


