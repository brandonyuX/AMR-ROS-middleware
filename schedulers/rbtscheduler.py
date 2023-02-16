import sys,os
import time
import datetime
import threading
# setting path
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.robotinterface as robotinterface
import interface.chrinterface as chrinterface
import interface.plcinterface as plcinterface
import interface.wmsinterface as wmsinterface
import logic.pathcalculate as pathcalculate



production=True

tskq=[]
lastloc=''
dbmaphash={'STN1' : 'Station 1', 'STN2' : 'Station 2','STN3':'Station 3','STN4':'Station 4','STN5':'Station 5'}
mapdict={"STN1":0,
            "STN2":1,
            "STN3":2,
            "STN4":3,
            "STN5":4,
            "Charging Station":5
            }
coflag=False

#Method to determine whether to get custom operation task
def getCO(priority):
    global coflag
    #Get request id and push it to custom operation
    os.environ['CUSTORDERSTATUS']='QUERY'
    #Decide on task id based on priority
    if priority:
        ctid=dbinterface.getCustomTaskID()
    else:
        ctid=dbinterface.getCustomNTaskID()
    wmsinterface.customop(ctid)
    #Wait for query to be completed
    while os.environ['CUSTORDERSTATUS']=='QUERY':
        pass
    costat=os.environ['CUSTORDERSTATUS']
    #Set custom order flag to 1 if MES is able to generate task
    if costat=='OK':
        dbinterface.setCRStatus(ctid)
        coflag=True
    else:
        pass

def tskpolling():
    #Initialize database connection
    #dbinterface.startup()
    
  
    # list=dbinterface.getReqList()
    # for item in list:
    #     print(item)
    #Initialze robot interface
    #robotinterface.startup()
    time.sleep(1)
    print('<MS> Start robot scheduler')
    loop=True
    currIndex=0
    while(loop):
        #print('=====Start Async task get=====')
        try:
            #time.sleep(1)
            tsklist=[]
            
           #Get from different action database based on custom order flag
            if(coflag):
               tsklist=dbinterface.getCustomListTop()
            else:
                tsklist=dbinterface.getTaskListTop()
            
            


            
            
            if len(tsklist)>0:
                tskq.clear()
                #Populate location list
                for tsk in (tsklist):
                    splitloc=str(tsk.destloc).split(';')
                    for loc in splitloc:
                        #print(tsk.rid)
                        tskq.append(loc)
            
            
                
                #If there are active tasks in tasklist, loop through task list to assign job to robot
                for i,tsk in enumerate(tsklist):
                

                    #Do not execute next step when task is still processing
                    if(int(tsk.exec)==1):
                        #dbinterface.writeLog('ms','Task {} for robot {} on step {} is executing'.format(tsk.tid,tsk.rid,tsk.currstep-1),False)
                        #print('Task {} for robot {} on step {} still executing'.format(tsk.tid,tsk.rid,tsk.currstep-1))
                        pass
                        
                        
                        
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
                            global coflag
                            dbinterface.writeLog('ms','End of execution for task {}'.format(tsk.tid),True)
                            dbinterface.incStep(tsk.tid,tsk.endstep,True)
                            tskq.clear()
                            tsklist.clear()
                            dbinterface.setExecute(0,tsk.tid)
                            currIndex=0
                            #dbinterface.updateReqStatus('REQUEST COMPLETED',tsk.reqid)
                            if(dbinterface.checkPriorityTask()):
                                getCO(True)
                            
                            
                                
                        

                    
                        
                        if(tsk.currstep<=tsk.endstep):
                            print('<MS> Current step is {}'.format(tsk.currstep))
                            print('Processing master step {} out of step {}'.format(tsk.currstep,tsk.endstep))
                            dbinterface.updateReqStatus('PROCESSING REQUEST',tsk.reqid)
                            subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,tsk.currstep)
                            
                            #Special move sequence
                            if(subtsk[0].at=='MoveC'):
                                #sname=tskq[i].pop(0)
                                #dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                #print(currIndex)
                                dbinterface.writeLog('ms','<MS>Processing move chain',True)
                                
                                #Detect previously moved and adjust move chain
                                # if tsk.currstep>1:
                                #     for i in range(len(tskq)):
                                #         if tskq[i]=='SRC':
                                #             currIndex=i+1
                                
                                #print(currmcstep)
                                
                                #New movement planning
                                #Get movestep to decide which movement is the robot at (SRC or DEST)
                                movestep=dbinterface.getMoveStep()
                                
                                dest=''
                                #Create path using path calculate
                                print('<MS> Generating path from current location')
                                
                                if(movestep==0):
                                    pathlist=pathcalculate.generate_path_simple(tskq[0])
                                    robotinterface.publish_sound(tskq[0])
                                    dest=tskq[0]
                                else:
                                    pathlist=pathcalculate.generate_path_simple(tskq[1])
                                    robotinterface.publish_sound(tskq[1])
                                    dest=tskq[1]
                                    
                                #Get previous movechain step
                                mcstep=dbinterface.getMCStep()
                                
                                for i in range(mcstep,len(pathlist)):
                                    print('<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,pathlist[i]))
                                    os.environ['reached'] = 'False'
                                    
                                    print('Moving robot to {}'.format(pathlist[i]))
                                    print('<MS>Processing move chain {} out of {}'.format(i,len(pathlist)))
                                    robotinterface.publish_cmd(tsk.rid,pathlist[i])
                                    
                                    dbinterface.setExecute(1,tsk.tid)
                                    
                                    while  os.environ['reached'] != 'True':
                                        pass
                                    print('<MS> Robot reached signal received')
                                    
                                    #Write mcstep based on current index and update robot location
                                    dbinterface.updateRbtLoc(1,pathlist[i])
                                    dbinterface.writeMCStep(tsk.tid,i)
                                    
                                print('<MS> Robot reached destination')
                                robotinterface.publish_sound('reach')
                                #End of loop means completed
                                if(dest=="Stn1" or dest=="WH"):
                                        time.sleep(1)
                                        robotinterface.align_qr()
                                
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                                dbinterface.setExecute(0,tsk.tid)
                                
                                
                                
                                #Legacy movement planning
                                # currmcstep=dbinterface.readMCStep(tsk.tid)
                                # if tskq[currmcstep]=='SRC':
                                #     currmcstep=currmcstep+1
                                # for i in range(currmcstep,len(tskq)):
                                #     if tskq[i]=='END' or tskq[i]=='SRC' or tskq[i]=='DEST' or tskq[i]=='DEST2':
                                        
                                #         global lastloc
                                #         if(tskq[i-1]=="Stn1" or tskq[i-1]=="WH"):
                                #             time.sleep(1)
                                #             robotinterface.align_qr()
                                #         dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                                #         dbinterface.setExecute(0,tsk.tid)
                                #         dbinterface.updateRbtLoc(1,tskq[i-1])
                                        
                                #         lastloc=tskq[i-1]
                                #         robotinterface.publish_sound('reach')
                                #         currIndex=i+1
                                #         #dbinterface.writeLog('ms','<MS>Detect temporal end of movement',True)
                                #         #Break out of loop when a temporal stop is detected to move on to next action
                                #         break
                                #     else:
                                #         print('<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,tskq[i]))
                                #         #Publish sound for final destination based on pointer location
                                #         if(i==0 or i==currIndex):
                                #             for j in range(i,len(tskq)):
                                                
                                #                 if tskq[i]=='END' or tskq[i]=='SRC' or tskq[i]=='DEST' or tskq[i]=='DEST2':
                                #                     print('Publish sound for {}'.format(tskq[j-1]))
                                #                     robotinterface.publish_sound(tskq[j-1])
                                #                     time.sleep(1)
                                #                     break
                                        
                                #         os.environ['reached'] = 'False'
                                        
                                #         print('Moving robot to {}'.format(tskq[i]))
                                #         print('<MS>Processing move chain {} out of {}'.format(i,len(tskq)))
                                #         robotinterface.publish_cmd(tsk.rid,tskq[i])
                                        
                                #         dbinterface.setExecute(1,tsk.tid)
                                        
                                #         while  os.environ['reached'] != 'True':
                                #             pass
                                #         print('<MS> Robot reached signal received')
                                        
                                #         #Increase mcstep
                                        
                                #         dbinterface.writeMCStep(tsk.tid)
                                time.sleep(0.1)


                            #Define multiple request task
                            if(subtsk[0].at=='Move'):
                                #print('attempt move')
                                sname=tskq[0]
                                
                                os.environ['reached'] = 'False'
                                #print(mapdict[sname])
                                #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                                dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                #print('<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,sname))
                                dbinterface.writeLog('ms','<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,sname),True)
                                #Send command to robot interface to run this step
                                #print(mapdict[sname])
                                if production:
                                    
                                    dbinterface.setExecute(1,tsk.tid)
                                    print('Publish sound for {}'.format(sname))
                                    robotinterface.publish_sound(sname)
                                    robotinterface.publish_cmd(tsk.rid,sname)
                                    while  os.environ['reached'] != 'True':
                                        pass
                                    if( sname=="Stn1" or  sname=="WH"):
                                        time.sleep(1)
                                        robotinterface.align_qr()
                                    dbinterface.updateRbtLoc(1,tskq[0])
                                    dbinterface.setExecute(0,tsk.tid)
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
                            


                            #Unload subtask
                            if(subtsk[0].at=='Send'):
                                #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                                dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                #print('<MS>Sending unload command to robot {}.'.format(tsk.rid))
                                dbinterface.writeLog('ms','<MS>Sending unload command to robot {}.'.format(tsk.rid),True)
                                dbinterface.setExecute(1,tsk.tid)
                                #Test set execute to false after 5 seconds
                                if production:
                                    dbinterface.writeLog('ms','<MS>Get current location to determine handshake',True)
                                    currentloc=dbinterface.getRbtLoc(1)
                                    #Check last location to determine type of handshake
                                    if(currentloc=="Stn1"):
                                        #Send request to send to plc
                                        dbinterface.writeLog('ms','<MS>Send request to send to PLC',True)
                                        plcinterface.writePLC("rts",True,"Stn1")
                                        #Check if PLC is ready to receive
                                        dbinterface.writeLog('ms','<MS>Wait for ready to receive from PLC',True)
                                        while(plcinterface.readPLC("rtr","Stn1")!=True):
                                            pass
                                        print('<MS> Received ready to receive from PLC. Start rolling conveyor.')
                                        robotinterface.send_item()
                                        print('<MS> Wait for station 1 to detect item on tail end sensor.')
                                        while(plcinterface.readPLC("te","Stn1")!=True):
                                            pass
                                        print('<MS> Item detected on station 1')
                                        #Write PLC processed quantity to start WO
                                        #plcinterface.setWOStart(1)
                                    elif currentloc=="WH":
                                        #Send request to send to plc
                                        dbinterface.writeLog('ms','<MS>Send request to send to PLC',True)
                                        plcinterface.writePLC("rts",True,"WH")
                                        #Check if PLC is ready to receive
                                        dbinterface.writeLog('ms','<MS>Wait for ready to receive from PLC',True)
                                        while(plcinterface.readPLC("rtr","WH")!=True):
                                            pass
                                        print('<MS> Received ready to receive from PLC. Start rolling conveyor.')
                                        robotinterface.send_item()
                                        print('<MS> Wait for warehouse to detect item on tail end sensor.')
                                        while(plcinterface.readPLC("te","WH")!=True):
                                            pass
                                        print('<MS> Item detected on Warehouse')
                                        #Signal WMS ready bin
                                        wmsinterface.signalBinAtWH()
                                       
                                        
                                    else:
                                        robotinterface.send_item()
                                while(os.environ.get('convcomplete')=='False'):
                                    pass
                                dbinterface.writeLog('ms','<MS>Receive Completed',True)
                                os.environ['convcomplete'] ='False'
                                robotinterface.reset_conv()
                                dbinterface.setExecute(0,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)

                            #Loading subtask         
                            if(subtsk[0].at=='Receive'):
                                #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                                #print('<MS>Sending load command to robot {}.'.format(tsk.rid))
                                dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                dbinterface.writeLog('ms','<MS>Sending load command to robot {}.'.format(tsk.rid),True)
                                dbinterface.setExecute(1,tsk.tid)
                                #Test set execute to false after 5 seconds
                                if production:
                                    dbinterface.writeLog('ms','<MS>Get current location to determine handshake',True)
                                    currentloc=dbinterface.getRbtLoc(1)
                                    #Check last location to determine type of handshake
                                    if(currentloc=="Stn1"):
                                        dbinterface.writeLog('ms','<MS>Start rolling conveyor and send ready to receive',True)
                                        robotinterface.receive_item()
                                        #Send ready to receive to plc
                                        time.sleep(0.5)
                                        plcinterface.writePLC("rtr",True,'Stn1')
                                        time.sleep(0.5)
                                        dbinterface.writeLog('ms','<MS>Wait for Station 1 Head End sensor to clear',True)
                                        while(plcinterface.readPLC("he","Stn1")==True):
                                            pass
                                        dbinterface.writeLog('ms','<MS>Sensor cleared on station 1',True)
                                    #Interface when robot reach warehouse
                                    elif(currentloc=="WH"):
                                        dbinterface.writeLog('ms','<MS>Check if WMS has ready item',True)
                                        #Check if wms is ready
                                        # while(plcinterface.readPLC("wmsoutrdy","WH")==0):
                                        #     pass
                                        # #Reset wms ready bit
                                        # plcinterface.writePLC("resetwmsoutrdy",0,"WH")
                                        os.environ['wmsrdy'] = 'False'
                                        while os.environ['wmsrdy']=='False':
                                            pass
                                        dbinterface.writeLog('ms','<MS>Start rolling conveyor and send ready to receive',True)
                                        robotinterface.receive_item()
                                        #Send ready to receive to plc
                                        time.sleep(0.5)
                                        plcinterface.writePLC("rtr",True,'WH')
                                        time.sleep(0.5)
                                        dbinterface.writeLog('ms','<MS>Wait for Station 1 Head End sensor to clear',True)
                                        while(plcinterface.readPLC("he","WH")==True):
                                            pass
                                        dbinterface.writeLog('ms','<MS>Sensor cleared on station 1',True)
                                    else:
                                        robotinterface.receive_item()
                                #robotinterface.receive_item()
                                #Wait for load to complete
                                while(os.environ.get('convcomplete')=='False'):
                                    pass
                                robotinterface.reset_conv()
                                dbinterface.writeLog('ms','<MS>Receive Completed',True)
                                os.environ['convcomplete'] ='False'
                                
                                dbinterface.setExecute(0,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)

                        
                            if(subtsk[0].at=="Charge"):
                                dbinterface.writeLog('ms','<MS>Initiate Charging',True)
                                #Extend rod
                                dbinterface.writeLog('ms','<MS>Extending Rod',True)
                                if production:
                                    chrinterface.extend()
                                time.sleep(15)
                                #Start charge
                                dbinterface.writeLog('ms','<MS>Start Charging',True)
                                if production:
                                    #chrinterface.start()
                                    pass
                                dbinterface.updateRbtCharge(1,1)
                                dbinterface.setExecute(0,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                            if(subtsk[0].at=="StopCharge"):
                                dbinterface.writeLog('ms','<MS>Stop Charging',True)
                                #Extend rod
                                chrinterface.stop()
                                time.sleep(5)
                                dbinterface.writeLog('ms','<MS>Retracting Rod',True)
                                chrinterface.retract()
                                time.sleep(15)
                                dbinterface.updateRbtCharge(1,0)
                                dbinterface.setExecute(0,tsk.tid)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                            #Wait for complete signal from end user
                            if(subtsk[0].at=="WaitComplete"):
                                if tsk.hsmsg=='CUSTOM':
                                    os.environ['waitcustom'] = 'False'
                                    dbinterface.writeLog('ms','<MS>Wait for next action from WMS',True)
                                    
                                    while(os.environ.get('waitcustom')=='False'):
                                        pass
                                    
                                    pass
                                else:
                                    os.environ['waitcomplete'] = 'False'
                                    dbinterface.writeLog('ms','<MS>Wait for user to signal complete',True)
                                    robotinterface.publish_sound('wait-carton')
                                    while(os.environ.get('waitcomplete')=='False'):
                                        pass
                                    dbinterface.writeLog('ms','<MS>Complete command received!',True)
                                    dbinterface.setExecute(0,tsk.tid)
                                    dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                            

                    #time.sleep(2)
    
                
            else:
                #print('=====No task found yet. Polling...')
                #dbinterface.writeLog('ms','No Task Found',False)
                #Reset custom order flag if coflag is True and no task is detected in the custom order list
                if(coflag):
                    coflag=False
                if(dbinterface.checkPriorityTask()):
                    getCO(True)
                else:
                    if(dbinterface.checkNormalTask()):
                        getCO(False)
                    
                        
                time.sleep(0.1)
                pass
        except Exception as e:
            print(e)
        #time.sleep(1.5)


def startup():
    
    print('<MS>Robot Scheduler start up')
    t1=threading.Thread(target=tskpolling,daemon=True)
    t1.start()
    #t1.join()
#tskpolling()


