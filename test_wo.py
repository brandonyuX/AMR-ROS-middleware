import interface.plcinterface as plcinterface
import time

print('Welcome to Work Order testing interface!\n')

selection=['Increment work order']
plcinterface.startupdemo()
def checkAllDone():
    done = True
    for stn in range(1,7):
        if(plcinterface.checkStnDone(stn,True))==0:
            done=False
    return done


while True:
    for i,sel in enumerate(selection):
        print('{}: {} '.format(i+1,sel))
    choice=input(f'Please select services (1-{len(selection)})\n')
    match choice:
        case '1':
            stn=input('Work Orders will be incremented for ALL stations! Please enter to continue.')
            if stn=='':
                while not checkAllDone():
                    for stn in range(1,7):
                        if(plcinterface.checkStnDone(stn,True))==0:
                            plcinterface.incProcQty(stn)
                            # print(f'Increase station {stn} quantity')
                    time.sleep(2)
