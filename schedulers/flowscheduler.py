import sys
import asyncio


# setting path
sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface
import interface.robotinterface as rbtinterface
dbinterface.startup()

flowStr=dbinterface.getFlow('GetEmptyBottle')

flowList=flowStr.split(';')
print('Total flow actions: {}'.format(len(flowList)))

for flow in flowList:
    interface=flow.split('-')[0]
    action=flow.split('-')[1]
    print('{} {}'.format(interface,action))
    go=False
   
   #Get relevant action from particular action
    match action:
        case 'GO':
            stn=flow.split('-')[2]
            go=True
            print('Calling robot interface to go to {}'.format(stn))
            
        case 'WAIT':
            wact=flow.split('-')[2]
            print('Waiting for {}'.format(wact))
        case 'EB':
            print('Prepare Empty Bottle')
        case 'WaitReach':
            print('Wait for robot to reach')
    
    
    match interface:
        case 'AMR':
            if go:
                while rbtinterface.movetoloc(stn)!=True:
                    pass
        case 'WMS':
            print('Call WMS Interface')