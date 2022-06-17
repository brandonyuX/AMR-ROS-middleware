#This file is used to schedule Work Orders
import json
import sys
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface
#Sample work order json
# [{
# 		"wo_id": "WO001",
# 		"details": {
# 			"batch_id": 123,
# 			"req_qty": 20,
# 			"fill_vol": 250

# 		}
# 	},
# 	{
# 		"wo_id": "WO002",
# 		"details": {
# 			"batch_id": 456,
# 			"req_qty": 20,
# 			"fill_vol": 150

# 		}
# 	}
# ]
dbinterface.startup()
def findOptimalWo():
    wolist=dbinterface.getWO()
    for wo in wolist:
        print(wo.woid)
    
findOptimalWo()