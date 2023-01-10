#This file is used to schedule Work Orders
import json
import sys
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
#Sample work order json
# {"Batch ID": String, "Init SN": String, "Manufacture Date": String, "Fill and Pack Date": String, "Fill Volume": Number, "Target Torque": Number, "Work Orders": [String, String, String, ...]}

#dbinterface.startup()
def findOptimalWo():
    wolist=dbinterface.getWO()
    for wo in wolist:
        print(wo.woid)
    
findOptimalWo()