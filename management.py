import sys,os

# setting path
sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface

selection=['Show Production Task','Show Custom Task','Show Custom Request','Delete All Production tasks','Delete All Custom Tasks','Delete work order','Void all work orders','Delete All Work Order']
dbinterface.startup()

print('Welcome to RMS management interface')



try:
    while True:
        for i,sel in enumerate(selection):
            print('{}: {} '.format(i+1,sel))
        choice=input('Please select services\n')
        match choice:
            case '1':
                tasklist=dbinterface.getTask('production')
                for task in tasklist:
                    print(task)
                pass
            case '2':
                tasklist=dbinterface.getTask('custom')
                for task in tasklist:
                    print(task)
                pass
            case '4':
                dbinterface.deleteAllProduction()
            case '5':
                dbinterface.deleteAllCustom()
            case '6':
                wo=input('Please enter wo number\n')
                dbinterface.deleteWO(wo)
                print('WO deleted!')
            case '7':
                dbinterface.voidWO()
            case '8':
                dbinterface.deleteAllWO()
        input()
except KeyboardInterrupt:
    exit(0)
