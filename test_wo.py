import interface.dbinterface as dbinterface
import time


dbinterface.startup()

def start_wo():
    wo_id='WO001'
    stat='c'
    for j in range(1,7):
        
        dbinterface.updateWO(wo_id,j,stat)
        print('Set station {} for work order {} to status {}'.format(j,wo_id,stat))
        for i in range(1,7):
            print('Pushing {} to station {}'.format(dbinterface.getWOQ(i),i))
        time.sleep(1)
#start_wo()