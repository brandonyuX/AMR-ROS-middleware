#This file is used to schedule Work Orders
import json
import threading,time
import sys,os
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.plcinterface as plcinterface
from enum import Enum
#Sample work order json
# {"Batch ID": String, "Init SN": String, "Manufacture Date": String, "Fill and Pack Date": String, "Fill Volume": Number, "Target Torque": Number, "Work Orders": [String, String, String, ...]}
req_qty=12
#Find all available work order

#Initialize batch number
os.environ['currbatchid']='Null'
#Initialize work order state

forceack=False

class wostate(Enum):
    INITIAL = 0
    WAITSTARTACK = 1
    WAITCOMPLETE = 2
    WAITCOMPLETEACK = 3
wostatearr=[wostate.INITIAL]*7
currbatchno=''
def startWOS():
    while True:
        #Loop through all orders
        for stn in range (1,7):
            #print(plcinterface.checkStnDone(stn,check=True,bcode=None,wonum=None))
            match wostatearr[stn]:
                case wostate.INITIAL:
                    global forceack
                    os.environ[f'stn{stn}state'] ='IDLE'  
                    #Check if station is available
                    stnstate,wowstate=plcinterface.checkStnStatus(stn)
                    #print(f'stn{stn} state {stnstate} wostate {wowstate}')
                    if stnstate in [1,2,3] and wowstate in [0,1,4,5]:

                        # if plcinterface.checkStnDone(stn,check=True):
                        #     wostatearr[stn]=wostate.WAITCOMPLETE
                        #     print(f'Station {stn} now in WAIT COMPLETE state')
                        
                        #Find new work order
                        wo=dbinterface.findWO(stn,'NEW')
                        
                            
                        # print(f"<WOS> Station {stn} is available.")
                        #time.sleep(1)
                        if(wo): 
                            # print(f"<WOS> Work order {wo[2]} available for station {stn}.")
                            #Send wo to PLC without starting it by initializing req and proc pty to 0        
                            plcinterface.sendWO2PLC(stn,wo)
                            #Send WO number and wait for ack on next state
                            wostatearr[stn]=wostate.WAITSTARTACK
                            #Write WO state to db
                            dbinterface.writeWOState(stn=stn,wo=wo[2],state='WAIT START ACK')
                            print(f'Station {stn} now in WAIT START ACK state')
                            os.environ[f'stn{stn}state'] ='WAIT START ACK STATE' 

                    elif wowstate in [1,2] and plcinterface.checkStnDone(stn,check=True,bcode=None,wonum=None)==2:
                        print(f'Station {stn} now in WAIT START ACK state')
                        #os.environ[f'stn{stn}state'] ='WAIT START ACK STATE' 
                        wostatearr[stn]=wostate.WAITSTARTACK
                        wo=dbinterface.findWO(stn,'NEW')

                    elif wowstate in [2,3]:

                        print("<WOS> Station {} is busy with work order. Jump to wait for completion".format(stn))
                        forceack=True
                        wostatearr[stn]=wostate.WAITCOMPLETE
                        # print(stn)
                        wo=dbinterface.findWO(stn,'STARTED')
                        #print(wo[2])
                        #dbinterface.writeWOState(stn=stn,wo=wo[2],state='WAIT COMPLETE')
                        print(f'Station {stn} now in WAIT COMPLETE state')
                        #os.environ[f'stn{stn}state'] =f'PROCESSING WO {wo[2]}' 
                    
                    
                        #dbinterface.writeWOState(stn=stn,wo=wo[2],state='WAIT START ACK')
                        
                case wostate.WAITSTARTACK:
                    
                    #Check whether start acknowledge is received
                    if plcinterface.checkStartAck(stn):
                        print("<WOS> Start acknowledgement received for station {}.".format(stn))
                        #Start WO by changing required qty 
                        wo=dbinterface.findWO(stn,'NEW')
                        if(wo):
                            plcinterface.startWO(stn,wo)
                            dbinterface.setWODBStart(stn,wo[2])
                            
                            #Check if Work Order is the last one
                            if stn==6:
                                if dbinterface.checkWOLast(stn=6,batchnum=wo[1]):
                                    dbinterface.writeLog(msg='Detected last work order')
                                    #time.sleep(5)
                                    plcinterface.setLastWO(True)
                                    pass
                            wostatearr[stn]=wostate.WAITCOMPLETE
                            #dbinterface.writeWOState(stn=stn,wo=wo[2],state='WAIT COMPLETE')
                            print(f'Station {stn} now in WAIT COMPLETE state')
                            os.environ[f'stn{stn}state'] =f'WAIT TO COMPLETE WO {wo[2]}' 
                case wostate.WAITCOMPLETE:
                    #print(stn)
                    wo=dbinterface.findWO(stn,'STARTED')
                    #print(wo)
                    #print(wo[2])
                    #Check whether order is completed
                    if plcinterface.checkStnDone(stn,check=False,bcode=wo[1],wonum=wo[2])==1:
                        if stn==6:
                            os.environ['currbatchid']=wo[1]
                        print("<WOS> Order completed for station {}. Waiting for MES acknowledgement.".format(stn))
                        wostatearr[stn]=wostate.WAITCOMPLETEACK
                        #dbinterface.writeWOState(stn=stn,wo=wo[2],state='WAIT COMPLETE ACK')
                        print(f'Station {stn} now in WAIT COMPLETE ACK state')
                        os.environ[f'stn{stn}state'] ='COMPLETED. WAIT MES ACK' 
                        
                    else:
                        #Wait for complete ack from MES in the next stage
                        pass
                    
                case wostate.WAITCOMPLETEACK:
                    if plcinterface.checkCMPAck(stn):
                        
                        
                        wo=dbinterface.findWO(stn,'STARTED')
                        if(wo):
                            print('<WOS>Current work order to complete: {}'.format(wo[2]))
                            dbinterface.setWODBComplete(stn,wo[2])
                            #Issue cmdstop when batch is complete
                            #plcinterface.setStnState(i,'Stop')
                            #Restart process
                            #dbinterface.writeWOState(stn=stn,wo=wo[2],state='COMPLETE')
                            print("<WOS>Complete acknowledgement for station {} received.".format(stn))
                        wostatearr[stn]=wostate.INITIAL        
                        print(f'Station {stn} back to INITIAL STATE')
                        #Set command to stop after Work Order completion other then Station 6
                        
                        if(stn==6) and dbinterface.checkWOLast(stn=6,batchnum=wo[1]):
                            for i in range(1,6):
                                plcinterface.setStnState(stn=i,state='Stop')
                                dbinterface.writeLog(msg=f'Stopping station {stn}')

                        os.environ[f'stn{stn}state'] ='IDLE'  
            #If new WO exist and plc has completed order
            #print('{} for station {} is available'.format(wo[2],i))
            # if plcinterface.checkStnDone(i):
            #     #Find available WO for each station
            #     wo=dbinterface.findWO(i)
            #     if wo:
            #         #Send wo to PLC
            #         plcinterface.sendWO2PLC(i,wo)
            #         #Set WO to start status to prevent resending
            #         dbinterface.setWOStart(i,wo[2])
            time.sleep(1)
        

#dbinterface.startup()
def findOptimalWo():
    wolist=dbinterface.getWO()
    for wo in wolist:
        print(wo.woid)
    
    
def startup():
    
    print('<MS>Work order scheduler start up')
    time.sleep(5)
    t1=threading.Thread(target=startWOS,daemon=True)
    t1.start()
