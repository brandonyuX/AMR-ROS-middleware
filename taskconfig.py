from mwclass.subtask import SubTask
import interface.dbinterface as dbinterface

tsklist=[]
currsublist=[]
actiondict={'0':'Move','1':'Unload','2':'Load','3':'Custom Command'}
cmd=''

currsublist=dbinterface.getSubTaskList()
while(True):
    print('========Task Configuration Manager=========')

    # for tsk in currsublist:
    #     print('Task Model: {} || Step : {} || Peform {}'.format(tsk.tskmodno,tsk.step,actiondict[str(tsk.action)]))

    act=input('Please state action to perform.\n1. Add new Task Model\n2. Query Existing Task Model\n3. Delete Task Model\n')

    if(act=='3'):
        #Demonstrate query of task model
        query=input('Query task model number: ')
        dbinterface.delSubTaskByID(query)

    if(act=='2'):
        #Routine to query subtask
        query=input('Query task model number: ')
        
        querysublist=dbinterface.getSubTaskListByID(int(query))
        if(len(querysublist)==0):
            print('No Task Model of this id found')
        for tsk in querysublist:
            print('Task Model: {} || Step : {} || Peform {}'.format(tsk.tskmodno,tsk.step,actiondict[str(tsk.action)]))

    if(act=='1'):
        tskmodno=input('Please enter Task Model Number: ')

        cont='y'
        step=0
        while (cont=='y'):
            step+=1
            act=input("Please input action to perform (0:Move,1:Unload,2:Load,3:Custom Command): ")
            if(act=='3'):
                cmd=input('Please input custom command: ')
            if(int(act)<=3):
                actconv=actiondict[act]
                st=SubTask(tskmodno,actconv,step,cmd)
                tsklist.append(st)
            else:
                print('Invalid input')
            cont=input('Add another action? (y/n)')

        print('=====Recorded action=====')
        for tsk in tsklist:
            print('Task Model: {} || Step : {} || Peform {}'.format(tsk.tskmodno,tsk.step,tsk.action))

        record=input('Record actions in database? (y/n)')
        if(record=='y'):
            
            querysublist=dbinterface.getSubTaskListByID(int(tskmodno))
            #print(len(querysublist))
            #Check if task model id exist
            if(len(querysublist)==0):
                dbinterface.writeSubTask(tsklist)
                print('Task Model created!')
            else:
                print('Task Model already exist, please delete old task model to create new task model')