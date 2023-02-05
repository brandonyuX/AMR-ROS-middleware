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
def startWOS():
    while True:
        #Loop through all orders
        for i in range (1,3):
            
            
            #If new WO exist and plc has completed order
            #print('{} for station {} is available'.format(wo[2],i))
            if plcinterface.checkStnDone(i):
                #Find available WO for each station
                wo=dbinterface.findWO(i)
                if wo:
                    #Send wo to PLC
                    plcinterface.sendWO2PLC(i,wo)
                    #Set WO to start status to prevent resending
                    dbinterface.setWOStart(i,wo[2])
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
