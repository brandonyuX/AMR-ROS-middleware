#This file is used to schedule Work Orders
import json
import threading,time
import sys
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
import interface.plcinterface as plcinterface
#Sample work order json
# {"Batch ID": String, "Init SN": String, "Manufacture Date": String, "Fill and Pack Date": String, "Fill Volume": Number, "Target Torque": Number, "Work Orders": [String, String, String, ...]}
req_qty=12
#Find all available work order

#Initialize work order state
wostate=[0]*6


def startWOS():
    while True:
        #Loop through all orders
        for i in range (1,3):
            
            match wostate[i]:
                case 0:
                    #Check if station is available
                    stnavail=plcinterface.checkStnAvail(i)
                    if stnavail==1:
                        print("<WOS> Station {} is available.".format(i))
                        #If available find next WO in db
                        wo=dbinterface.findWO(i)
                        if(wo): 
                            #Send wo to PLC without starting it by initializing req and proc pty to 0        
                            plcinterface.sendWO2PLC(i,wo[2])
                            #Send WO number and wait for ack on next state
                            wostate[i]=1
                    elif stnavail==2:
                        print("<WOS> Station {} is busy with work order. Jump to wait for completion".format(i))
                        wostate[i]=2
                case 1:
                    #Check whether start acknowledge is received
                    if plcinterface.checkStartAck:
                        print("<WOS> Start acknowledgement received for station {}.".format(i))
                        #Start WO by changing required qty 
                        wo=dbinterface.findWO(i)
                        plcinterface.startWO(i,wo)
                        dbinterface.setWOStart(i,wo[2])
                        wostate[i]=2
                case 2:
                    #Check whether order is completed
                    if plcinterface.checkStnDone(i):
                        print("<WOS> Order completed for station {}. Waiting for MES acknowledgement.".format(i))
                        #Wait for complete ack from MES in the next stage
                        wostate[i]=3
                case 3:
                    if plcinterface.checkCMPAck(i):
                        print("<WOS>Complete acknowledgement for station {} received. Find next order.".format(i))
                        
                        #Restart process
                        wostate[i]=0               
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
    t1=threading.Thread(target=startWOS,daemon=True)
    t1.start()
