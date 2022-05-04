import sys
import time
import datetime
import threading
# setting path
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.robotinterface as robotinterface



def tskpolling():
    loop=True
    while(loop):
        #print('=====Start Async task get=====')
        tsklist=dbinterface.getTaskList()

        if len(tsklist)>0:
            print("=====Task Found======")
            for tsk in tsklist:
                
                if(int(tsk.comp)==1):
                    print('Complete all steps')
                    loop=False

                if(int(tsk.exec)==1):
                    print('Task {} on step {} still executing'.format(tsk.tid,tsk.currstep))
                    
                    
                else:
                    
                    print('Sending Command to Robot {}.\n Current Step: {} End Step: {}'.format(tsk.rid,tsk.currstep,tsk.endstep))
                    if(tsk.currstep+1>tsk.endstep):
                        dbinterface.incStep(tsk.tid,tsk.endstep,True)
                        dbinterface.stepComplete(tsk.tid)
                    else:
                        dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                    
                time.sleep(1)
  
            
        else:
            print('=====No task found yet. Polling...')
            time.sleep(0.5)
            


t1=threading.Thread(target=tskpolling)
t1.start()
t1.join()



