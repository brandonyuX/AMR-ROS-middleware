import sys,os,random
import time,yaml
from datetime import datetime
import threading
# setting path
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.robotinterface as robotinterface
import interface.chrinterface as chrinterface
import interface.plcinterface as plcinterface
import interface.wmsinterface as wmsinterface
import logic.pathcalculate as pathcalculate
import logging
import sys



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

with open('server-config.yaml', 'r') as f:
    doc = yaml.safe_load(f)

production=doc['ROBOT']['PRODUCTION']

#Default custom request ack to true
os.environ['creqack']='True'
os.environ['wmsrdy']='False'
# log = open('rms-rbt-scheduler','a')
# sys.stdout=log

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("rms-message.log", "a")
   
    def write(self, message):
        self.terminal.write(message)
        
        self.log.write('{} {} \n'.format(datetime.now(),message))  
        

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()

#Method to determine whether to get custom operation task based on priority
def getCO(priority):
    global coflag
    #Get request id and push it to custom operation
    print('<MS> Ready to start custom operation. Wait for custom request acknowledgement')
    while os.environ['creqack']=='False':
        pass
    print('<MS> Start custom operation')
    os.environ['CUSTORDERSTATUS']='QUERY'
    #Decide on task id based on priority
    if priority:
        ctid=dbinterface.getCustomTaskID(1)
    else:
        ctid=dbinterface.getCustomTaskID(0)
    #Call WMS to call custom operation
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
    time.sleep(3)
    print('<MS> Start robot scheduler')
    loop=True
    currIndex=0
    
    while(loop):
        #print('=====Start Async task get=====')
       
            #time.sleep(1)
            tsklist=[]
            global table

            #Logic to check if robot is charging
            chargingstatus=dbinterface.checkCharging(rbtid=1)

            while(chargingstatus):
                chargingstatus=dbinterface.checkCharging(rbtid=1)
                time.sleep(1)
                pass

            table='production'
            # global coflag
            #Check if uncompleted task exist in Custom Action Table
            CTExist=dbinterface.checkCTExist()
           #Get from different action database based on custom order flag
            # print(CTExist)
            if(CTExist):
               tsklist=dbinterface.getCustomListTop()
               table='custom'
               
            else:
                tsklist=dbinterface.getTaskListTop()
                table='production'
                #Reset production priority bit
                # if pp:
                #     pp=False
            
            #print(table)
 
            if len(tsklist)>0:
                tskq.clear()
                #Populate location list
                for tsk in (tsklist):
                    splitloc=str(tsk.destloc).split(';')
                    for loc in splitloc:
                        #print(tsk.rid)
                        tskq.append(loc)
            
            
                #print('<MS> Task id {} is running'.format(tsk.tid))
                #If there are active tasks in tasklist, loop through task list to assign job to robot
                for i,tsk in enumerate(tsklist):
                

                    #Do not execute next step when task is still processing
                    if(int(tsk.exec)==1 and int(tsk.completed)==0):
                        # choice=input('<MS> Previous task did not complete. Do you want to retry(1) or cancel(2)?')
                        # match choice:
                        #     case '1':
                        #         dbinterface.setExecute(0,tsk.tid,table)
                        #     case '2':
                        #         dbinterface.incStep(tsk.tid,tsk.endstep,True,table)
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
                            # global coflag
                            dbinterface.writeLog('ms','<MS> End of execution for task {}'.format(tsk.tid),True)
                            dbinterface.incStep(tsk.tid,tsk.endstep,True,table)
                            tskq.clear()
                            tsklist.clear()
                            dbinterface.setExecute(0,tsk.tid,table)
                            
                            #dbinterface.updateReqStatus('REQUEST COMPLETED',tsk.reqid)
                           
                            #Only check for priority task everytime task is ended
                            if(dbinterface.checkPriorityTask()):
                                getCO(True)
                            
                            
                                
                        

                    
                        
                        if(tsk.currstep<=tsk.endstep):
                            # print('<MS> Current step is {}'.format(tsk.currstep))
                            print('<MS>Processing master step {} out of step {}'.format(tsk.currstep,tsk.endstep))
                            # dbinterface.updateReqStatus('PROCESSING REQUEST',tsk.reqid)
                            subtsk=dbinterface.getSubTaskListByStepID(tsk.tskmodno,tsk.currstep)
                            
                            #Handle wms custom request call here
                            if table=='custom' and tsk.currstep==1:
                                wmstid=dbinterface.getWMSTID(tsk.tid)
                                match tsk.hsmsg:
                                    case 'Retrieve':
                                        #Retrieve tote box
                                        print('<MS> Call WMS to retrieve tote with wms id')
                                        wmsinterface.reqrtb(wmstid)
                                        pass
                                    case 'Store':
                                        #Store tote box with request id
                                        print('<MS> Call WMS to store tote with wms id')
                                        wmsinterface.reqstbwid(wmstid)
                                        pass
                            elif table=='production' and tsk.currstep==1:
                                match tsk.hsmsg:
                                    case 'REB':
                                        #Retrieve empty bottle
                                        print('<MS> Call WMS to request empty bottle')
                                        wmsinterface.reqEb()
                                    case 'STB':
                                        #Store empty tote box
                                        print('<MS> Call WMS to store empty tote box')
                                        wmsinterface.reqstb()

                                    case 'WAITCARTON':
                                        print('<MS> Call WMS to retrieve empty tote box')
                                        #Call WMS to retrieve empty tote
                                        wmsinterface.reqetb()
                                        
                                pass
                                
                            
                            #Special move sequence
                            if(subtsk[0].at=='MoveC'):

                                if(dbinterface.checkCharging(rbtid=1)):
                                     dbinterface.writeLog('ms','<MS>Robot is still charging!!',True)
                                else:
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
                                    movestep=dbinterface.getMoveStep(tsk.tid,table)
                                    
                                    dest=''
                                    #Create path using path calculate
                                    print('<MS> Generating path from current location')
                                    
                                    #Get destination location based on movestep
                                    pathlist=pathcalculate.generate_path_simple(tskq[movestep])
                                    robotinterface.publish_sound(tskq[movestep])
                                    if(tskq[movestep]=='Stn1'):
                                        plcinterface.informDocked(dock=1,stn=1)
                                    else:
                                        plcinterface.informDocked(dock=0,stn=1)


                                    dest=tskq[movestep]
                                
                                        
                                    #Get previous movechain step
                                    mcstep=dbinterface.getMCStep(tsk.tid,table)
                                    
                                    for i in range(mcstep,len(pathlist)):
                                        print('<MS>Sending move command to robot {} bound for {}'.format(tsk.rid,pathlist[i]))
                                        

                                        os.environ['reached'] = 'False'
                                        
                                        
                                        print('<MS>Processing move chain {} out of {}'.format(i+1,len(pathlist)))
                                        #print('Moving robot to {}'.format(pathlist[i]))
                                        if production:
                                            robotinterface.publish_cmd(tsk.rid,pathlist[i])
                                        
                                        dbinterface.setExecute(1,tsk.tid,table)
                                        if production:
                                            while  os.environ['reached'] != 'True':
                                                pass
                                        else:
                                            time.sleep(5)
                                            os.environ['reached'] = 'True'
                                        #print('<MS> Robot reached signal received')
                                        
                                        #Write mcstep based on current index and update robot location
                                        dbinterface.updateRbtLoc(1,pathlist[i])
                                        
                                        
                                    print('<MS> Robot reached destination')
                                    robotinterface.publish_sound('reach')
                                    dbinterface.incMoveStep(tsk.tid,table)
                                    #End of loop means completed
                                    if(dest=="Stn1" or dest=="WH"):
                                            #time.sleep(1)
                                            if production:
                                                #robotinterface.align_qr()
                                                pass
                                    if dest=="Stn6":
                                        plcinterface.informDocked(dock=True,stn=6)
                                        pass
                                    dbinterface.incStep(tsk.tid,tsk.currstep+1,False,table)
                                    dbinterface.setExecute(0,tsk.tid,table)
                                
                                
                                
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
                                    
                                    dbinterface.setExecute(1,tsk.tid,table)
                                    print('Publish sound for {}'.format(sname))
                                    robotinterface.publish_sound(sname)
                                    robotinterface.publish_cmd(tsk.rid,sname)
                                    while  os.environ['reached'] != 'True':
                                        pass
                                    if( sname=="Stn1" or  sname=="WH"):
                                        time.sleep(1)
                                        #robotinterface.align_qr()
                                        pass
                                    dbinterface.updateRbtLoc(1,tskq[0])
                                    dbinterface.setExecute(0,tsk.tid,table)
                                    dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                                else:
                                    dbinterface.setExecute(1,tsk.tid,table) 
                                    time.sleep(5)
                                    dbinterface.writeLog('ms','Move Completed',True)
                                    dbinterface.setExecute(0,tsk.tid,table)
                                    dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                                    
                            #Misc location
                            if(subtsk[0].at=='Misc'):
                                dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                dbinterface.writeLog('ms','<MS>Sending wait command to robot {}.'.format(tsk.rid),True)
                                #Send approach signal to host PLC
                                dbinterface.setExecute(1,tsk.tid,table)
                                #Wait for user to press button to confirm operation done
                                
                                time.sleep(5)
                                
                                dbinterface.writeLog('ms','<MS>Wait Completed',True)
                                dbinterface.setExecute(0,tsk.tid,table)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False)
                            


                            #Unload subtask
                            if(subtsk[0].at=='Send'):
                                #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                                #dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                #print('<MS>Sending unload command to robot {}.'.format(tsk.rid))
                                dbinterface.writeLog('ms','<MS>Sending unload command to robot {}.'.format(tsk.rid),True)
                                dbinterface.setExecute(1,tsk.tid,table)
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
                                        if production:
                                            #Insert WMS start sending command
                                            robotinterface.send_item()
                                            print('<MS> Wait for station 1 to detect item on tail end sensor.')
                                            while(plcinterface.readPLC("te","Stn1")!=True):
                                                pass
                                        print('<MS> Item detected on station 1')
                                        #Write PLC processed quantity to start WO
                                        #plcinterface.setWOStart()
                                    elif currentloc=="WH":
                                        
                                        #Send request to send to plc
                                        dbinterface.writeLog('ms','<MS>Send request to send to PLC',True)
                                        plcinterface.writePLC("rts",True,"WH")
                                        #Check if PLC is ready to receive
                                        dbinterface.writeLog('ms','<MS>Wait for ready to receive from PLC',True)
                                        while(plcinterface.readPLC("rtr","WH")!=True):
                                            pass
                                        print('<MS> Received ready to receive from PLC. Start rolling conveyor.')
                                        #Tell WMS that bin is going to send to station
                                        print('<MS> Tell WMS tote is sending in.')
                                        wmsinterface.signalBinToWH()
                                        if production:
                                            robotinterface.send_item()
                                            print('<MS> Wait for warehouse to detect item on tail end sensor.')
                                            while(plcinterface.readPLC("te","WH")!=True):
                                                pass
                                        print('<MS> Item detected on Warehouse')
                                        #Signal WMS ready bin
                                        dbinterface.writeLog('ms','<MS>Send bin ready signal to WMS',True)
                                        wmsinterface.signalBinAtWH()
                                       
                                        
                                    else:
                                        print('<MS> Cannot send item at this location!')
                                        #robotinterface.send_item()
                                        
                                if production:
                                    while(os.environ.get('convcomplete')=='False'):
                                        pass
                                    
                                    dbinterface.writeLog('ms','<MS>Receive Completed',True)
                                    
                                
                                    robotinterface.reset_conv()
                                os.environ['convcomplete'] ='False'
                                dbinterface.setExecute(0,tsk.tid,table)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False,table)

                            #Loading subtask         
                            if(subtsk[0].at=='Receive'):
                                #print('<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep))
                                #print('<MS>Sending load command to robot {}.'.format(tsk.rid))
                                #dbinterface.writeLog('ms','<MS>Executing step {} out of {}'.format(tsk.currstep,tsk.endstep),True)
                                dbinterface.writeLog('ms','<MS>Sending load command to robot {}.'.format(tsk.rid),True)
                                dbinterface.setExecute(1,tsk.tid,table)
                                #Test set execute to false after 5 seconds
                                if production:
                                    
                                    currentloc=dbinterface.getRbtLoc(1)
                                    dbinterface.writeLog('ms','<MS>Get handshake for {}'.format(currentloc),True)
                                    #Check last location to determine type of handshake
                                    if(currentloc=="Stn1"):
                                        dbinterface.writeLog('ms','<MS>Start rolling conveyor and send ready to receive',True)
                                        if production:
                                            robotinterface.receive_item()
                                        #Send ready to receive to plc
                                        time.sleep(0.5)
                                        if production:
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
                                        #os.environ['wmsrdy']='False'
                                        os.environ['wmsrdy']='False'
                                        while os.environ['wmsrdy']=='False':
                                            pass
                                        dbinterface.writeLog('ms','<MS>Start rolling conveyor and send ready to receive',True)
                                        if production:
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
                                        if production:
                                            robotinterface.receive_item()
                                #robotinterface.receive_item()
                                #Wait for load to complete
                                if production:
                                    while(os.environ.get('convcomplete')=='False'):
                                        pass
                                    robotinterface.reset_conv()
                                dbinterface.writeLog('ms','<MS>Receive Completed',True)
                                os.environ['convcomplete'] ='False'
                                
                                dbinterface.setExecute(0,tsk.tid,table)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False,table)

                        
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
                                dbinterface.setExecute(0,tsk.tid,table)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False,table)

                            if(subtsk[0].at=="StopCharge"):
                                dbinterface.writeLog('ms','<MS>Stop Charging',True)
                                #Extend rod
                                chrinterface.stop()
                                time.sleep(5)
                                dbinterface.writeLog('ms','<MS>Retracting Rod',True)
                                chrinterface.retract()
                                time.sleep(15)
                                dbinterface.updateRbtCharge(1,0)
                                dbinterface.setExecute(0,tsk.tid,table)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False,table)
                            #Wait for complete signal from end user
                            if(subtsk[0].at=="WaitComplete"):
                                if table=='custom':
                                    os.environ['waitcustom'] = 'False'
                                    dbinterface.writeLog('ms','<MS>Wait for next action from WMS',True)
                                    
                                    while(os.environ.get('waitcustom')!='Confirmed'):
                                        if(os.environ.get('waitcustom')=='Continue-Confirm'):
                                            #Roll back conveyor if item not in position
                                            # robotinterface.receive_item()
                                            # while(os.environ.get('convcomplete')=='False'):
                                            #     pass
                                            # robotinterface.reset_conv()
                                            os.environ['waitcustom']='Confirmed'
                                        elif(os.environ.get('waitcustom')=='Cancel-Confirm'):
                                            dbinterface.setNxtComp(tsk.tid)
                                            os.environ['waitcustom']='Confirmed'
                                            
                                            #os.environ['waitcustom']='Confirmed'
                                            
                                   
                                    
                                    pass
                                else:
                                    os.environ['waitcomplete'] = 'False'
                                    dbinterface.writeLog('ms','<MS>Wait for user to signal complete',True)
                                    robotinterface.publish_sound('wait-carton')
                                    # pp=True
                                    while(os.environ.get('waitcomplete')=='False'):
                                        pass
                                    
                                    #Signal WMS to return tote box
                                    final_bid=000000
                                    rand_batch=random.randrange(100000,999999)
                                    if os.environ['currbatchid']=='Null':
                                        final_bid=str(rand_batch)
                                    else:
                                        final_bid=(os.environ['currbatchid'])
                                    #Call WMS to receive item

                                    plcinterface.informDocked(dock=False,stn=6)
                                    
                                    wmsinterface.reqsfc(final_bid)


                                    #Roll back conveyor if item not in position
                                    # robotinterface.receive_item()
                                    # while(os.environ.get('convcomplete')=='False'):
                                    #     pass
                                    # robotinterface.reset_conv()

                                dbinterface.writeLog('ms','<MS>Complete command received!',True)
                                dbinterface.setExecute(0,tsk.tid,table)
                                dbinterface.incStep(tsk.tid,tsk.currstep+1,False,table)
                            

                    #time.sleep(2)
    
                
            else:
                #print('=====No task found yet. Polling...')
                #dbinterface.writeLog('ms','No Task Found',False)
                
                #Check for priority task REQUEST first before checking for non priority task
                if(dbinterface.checkPriorityTask()):
                    print('<MS>Priority task found')
                    getCO(True)
                else:
                    if(dbinterface.checkNormalTask()):
                        print('<MS>Non-Priority task found')
                        getCO(False)
                    
                        
                time.sleep(0.5)
                pass
        
        #time.sleep(1.5)


def startup():
    
    dbinterface.writeLog('ms','<MS>Robot Scheduler start up',True)
    t1=threading.Thread(target=tskpolling,daemon=True)
    t1.start()
    #t1.join()
#tskpolling()


