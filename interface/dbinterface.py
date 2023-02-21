from typing import final
import pyodbc
import sys
import time
import datetime
import yaml
# setting path
sys.path.append('../Middleware Development')

from mwclass.robotconfig import RobotConfig
from mwclass.stationmap import StationMap
from mwclass.plcrequest import PLCReq
from mwclass.subtask import SubTask
from mwclass.task import Task
from mwclass.robot import Robot
from mwclass.workorder import WO
from mwclass.user import User
from threading import Thread


 #Robot config list

rc_list=[]
#Station map list

sm_list=[]
#PLC request list

req_list=[]
#Robot current list

rbt_list=[]

#Task List
tsk_list=[]

#Sub Task List
subtsk_list=[]

#Work order list
wo_list=[]

#Get current time 
now = datetime.datetime.utcnow()

def startup():
    global cursor
    print('<DB>Database stack start up')
    with open('server-config.yaml', 'r') as f:
        doc = yaml.safe_load(f)

    #Set database parameters from config files
    server=doc['DATABASE']['SERVER']
    database=doc['DATABASE']['DB']
    
    
    cnxn = pyodbc.connect('Driver=SQL Server;Server='+server+';Database='+database+';Trusted_Connection=yes;')
    cnxn.autocommit=True
    cursor = cnxn.cursor()
    print('<DB>Database connected')

def getBundleInfo():
   
    rc_list.clear()
    sm_list.clear()
    req_list.clear()
    rbt_list.clear()
    
    #Create object list from configuration database
    cursor.execute("SELECT * FROM Configuration") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        rc=RobotConfig(row[0],row[1],row[2],row[3],row[4])
        rc_list.append(rc)
        row = cursor.fetchone()

    #Create station map list from database
    cursor.execute("SELECT * FROM MapStations") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        sm=StationMap(row[1],row[2],row[3],row[4],row[5])
        sm_list.append(sm)
        row = cursor.fetchone()

    #Fetch PLC request list from database
    cursor.execute("SELECT * FROM PLCRequest") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        req=PLCReq(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
        req_list.append(req)
        row = cursor.fetchone()

    #Fetch Robot current status
    cursor.execute("SELECT * FROM Robot") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        rbt=Robot(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        rbt_list.append(rbt)
        row = cursor.fetchone()
    #print('Updated variable from DB!')
    #time.sleep(3)
    
    return rc_list,sm_list,req_list,rbt_list

def getRobotList():
    #Fetch Robot current status
    cursor.execute("SELECT * FROM Robot") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        rbt=Robot(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        rbt_list.append(rbt)
        row = cursor.fetchone()
    return rbt_list


def getSubTaskList():
    subtsk_list.clear()
    cursor.execute("SELECT * FROM SubTask") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=SubTask(row[1],row[2],row[3],row[5])
        
        subtsk_list.append(tsk)
        row = cursor.fetchone()
    return subtsk_list

#Delete Subtask information
def delSubTaskByID(tskmodno):
    cursor.execute("DELETE FROM SubTask WHERE TaskModelID = ?",tskmodno) 
    cursor.commit()

#Retrieve Subtask information by task model id
def getSubTaskListByID(tskmodno):
    subtsk_list.clear()
    cursor.execute("SELECT * FROM SubTask WHERE TaskModelID = ?",tskmodno) 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=SubTask(row[0],row[1],row[2],row[3],row[4],row[5])
        
        subtsk_list.append(tsk)
        row = cursor.fetchone()
    return subtsk_list

#Retrieve Subtask information by task model id and step
def getSubTaskListByStepID(tskmodno,step):
    subtsk_list.clear()
    cursor.execute("SELECT * FROM SubTask WHERE TaskModelID = ? AND Step=?",tskmodno,step) 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=SubTask(row[0],row[1],row[2],row[3],row[4],row[5])
        
        subtsk_list.append(tsk)
        row = cursor.fetchone()
    return subtsk_list

def getReqList():
    req_list.clear()
    #Fetch PLC request list from database
    cursor.execute("SELECT * FROM PLCRequest") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        req=PLCReq(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
        req_list.append(req)
        row = cursor.fetchone()
    return req_list
def getTaskList():
     #Fetch Robot task list
    tsk_list.clear()
    cursor.execute("SELECT * FROM ProductionTask") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])
        
        tsk_list.append(tsk)
        row = cursor.fetchone()

    return tsk_list

#Write move chain step
def writeMCStep(tid,step):
    #print(tid)
    # cursor.execute("SELECT TaskCode FROM ProductionTask WHERE TaskID=?",tid) 
    # row = cursor.fetchone() 
    # newstep=row[0]+1
    #print(newstep)
    cursor.execute("UPDATE ProductionTask SET TaskCode=? WHERE TaskID=?",step,tid) 
    cursor.commit()
    
def getMCStep(tid,table):
    if table=='production':
        cursor.execute("SELECT TaskCode FROM ProductionTask WHERE TaskID=?",tid) 
    else:
        cursor.execute("SELECT TaskCode FROM CustomTask WHERE TaskID=?",tid) 
    row = cursor.fetchone() 
    #print (row)
    return row[0]
#Get the latest task that is not completed
def getTaskListTop():
     #Fetch Robot task list
    tsk_list.clear()
    cursor.execute("SELECT TOP 1 * FROM ProductionTask WHERE Completed=0") 
    row = cursor.fetchone() 
    if row:
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])  
        tsk_list.append(tsk)
    
    return tsk_list

#Get the latest custom task that is not completed
def getCustomListTop():
     #Fetch Robot task list
    tsk_list.clear()
    cursor.execute("SELECT TOP 1 * FROM CustomTask WHERE Completed=0") 
    row = cursor.fetchone() 
    if row:
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])  
        tsk_list.append(tsk)
    
    return tsk_list

#Check if uncompleted task exists in Custom Task table
def checkCTExist():
     
    cursor.execute("SELECT * FROM CustomTask WHERE Completed=0") 
    row = cursor.fetchone() 
    if row:
        return True
    else:
        return False
    
    return tsk_list
def getIPList():
    iplist=[]
    cursor.execute("SELECT RobotIP FROM Configuration") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        iplist.append(row[0])
        row = cursor.fetchone()
    return iplist

def getIP(rid):
    cursor.execute("SELECT RobotIP FROM Configuration WHERE RobotID=?",rid) 
    row = cursor.fetchone() 
    return row[0]


def insertReq(plcid,reqid,destloc,priority,reqtime,tskmodno):
    cursor.execute("INSERT INTO PLCRequest(PLCID,ReqID,DestLoc,Priority,ReqTime,TaskModelNo) VALUES (?,?,?,?,?,?)",plcid,reqid,destloc,priority,reqtime,tskmodno)
    cursor.commit()


def insertRbtTask(destloc,tskmod):
    cursor.execute("SELECT EndStep FROM SubTask WHERE TaskModelID=?",tskmod) 
    row=cursor.fetchone()
    es=row[0]
    cursor.execute("INSERT INTO ProductionTask(RobotID,Completed,TaskCode,CurrStep,EndStep,DestLoc,Executing,TaskModelID,ReqID,MoveStep) VALUES (?,?,?,?,?,?,?,?,?,?)",1,0,0,1,es,destloc,0,tskmod,100,0)
    cursor.commit()
    print('<DB> Write to robot task destination {}'.format(destloc))

#Insert custom task from WMS
def insertCustomTask(destloc,tskmod,wmsreq,wmstsk):
    cursor.execute("SELECT EndStep FROM SubTask WHERE TaskModelID=?",tskmod) 
    row=cursor.fetchone()
    es=row[0]
    cursor.execute("INSERT INTO CustomTask(RobotID,Completed,TaskCode,CurrStep,EndStep,DestLoc,Executing,TaskModelID,WMSReqID,WMSTID,HSMsg,MoveStep) VALUES (?,?,?,?,?,?,?,?,?,?,?)",1,0,0,1,es,destloc,0,tskmod,wmsreq,wmstsk,'CUSTOM',0)
    cursor.commit()
    print('<DB> Write to robot task destination {}'.format(destloc))

#Write movestep
def incMoveStep(tid,table):
    
    if table=='production':
        cursor.execute("SELECT MoveStep FROM ProductionTask WHERE TaskID=?",tid) 
        row = cursor.fetchone() 
        newstep=row[0]+1
        cursor.execute("UPDATE ProductionTask SET MoveStep = ? WHERE TaskID=?",newstep,tid) 
        cursor.commit()
    else:
        cursor.execute("SELECT MoveStep FROM CustomTask WHERE TaskID=?",tid) 
        row = cursor.fetchone() 
        newstep=row[0]+1
        cursor.execute("UPDATE CustomTask SET MoveStep = ? WHERE TaskID=?",newstep,tid) 
        cursor.commit()

#Read movestep
def getMoveStep(tskid,table):
    if table=='production':
        cursor.execute("SELECT MoveStep FROM ProductionTask WHERE TaskID=?",tskid) 
    else:
        cursor.execute("SELECT MoveStep FROM CustomTask WHERE TaskID=?",tskid)  
    
    row=cursor.fetchone()
    return row[0]


def writeTask(finalrid,reqid,rbt_list,req_list):
    
    startloc=(next((x for x in rbt_list if x.rid == finalrid), None).currloc)
    destloc=(next((x for x in req_list if x.reqid == reqid), None).destloc)
    tskmodno=(next((x for x in req_list if x.reqid == reqid), None).tskmodno)
    print(startloc)
    print(destloc)
    
    cursor.execute("INSERT INTO Task (RobotID,ReqID,Completed,TaskCode,CurrStep,LastUpd,Executing,TaskModelID,DestLoc,Processing) VALUES (?,?,?,?,?,?,?,?,?)",finalrid,reqid,0,000,1,datetime.now(),0,tskmodno,destloc,0)
    cursor.commit()

def writeSubTask(tsklist):
    
    for tsk in tsklist:
        cursor.execute("INSERT INTO SubTask (TaskModelID,ActionType,Step,EndStep,Command) VALUES (?,?,?,?,?)",tsk.tskmodno,tsk.action,tsk.step,len(tsklist),tsk.cmd)
        cursor.commit()

def updateReqStatus(status,reqid):
    cursor.execute("UPDATE PLCRequest SET Status = ? WHERE ReqID=?",status,reqid) 
    cursor.commit()

def updateReqDest(loc,reqid):
    cursor.execute("UPDATE PLCRequest SET DestLoc = ? WHERE ReqID=?",loc,reqid) 
    cursor.commit()

def updateRbtStatus(status,rbtid):
    cursor.execute("UPDATE Robot SET Avail = ? WHERE RobotID=?",status,rbtid) 
    cursor.commit()

#Update robot charging
def updateRbtCharge(rbtid,state):
    cursor.execute("UPDATE Robot SET Charging = ? WHERE RobotID=?",state,rbtid) 
    cursor.commit()

def updateRbtLoc(rbtid,currloc):
    cursor.execute("UPDATE Robot SET CurrentLoc=? WHERE RobotID=?",currloc,rbtid) 
    cursor.commit()

def getRbtLoc(rbtid):
    cursor.execute("SELECT CurrentLoc FROM Robot WHERE RobotID=?",rbtid) 
    row = cursor.fetchone() 
    return row[0]

#Update position status to database
def updateRbtPosStatus(rbtid,x,y,r):
    cursor.execute("UPDATE Robot SET x=?,y=?,r=? WHERE RobotID=?",x,y,r,rbtid) 
    cursor.commit()

#Update robot battery level
def updateRbtBatt(rbtid,battlvl):
    cursor.execute("UPDATE Robot SET BattLvl=? WHERE RobotID=?",battlvl,rbtid) 
    cursor.commit()

#Update position status to database
def updateRbtMsg(rbtid,msg):
    cursor.execute("UPDATE Robot SET msg=? WHERE RobotID=?",msg,rbtid) 
    cursor.commit()

#Delete task based on request id
def deltask(reqid):
    cursor.execute("DELETE FROM ProductionTask WHERE ReqID = ?",reqid) 
    cursor.commit()

#Increment step to task 
def incStep(tid,step,comp,table):
    if table=='production':
        if comp:
            cursor.execute("UPDATE ProductionTask SET Completed=? WHERE TaskID=?",1,tid) 
            cursor.commit()
        else:
            cursor.execute("UPDATE ProductionTask SET CurrStep=? WHERE TaskID=?",step,tid) 
            cursor.commit()
    else:
        if comp:
            cursor.execute("UPDATE CustomTask SET Completed=? WHERE TaskID=?",1,tid) 
            cursor.commit()
        else:
            cursor.execute("UPDATE CustomTask SET CurrStep=? WHERE TaskID=?",step,tid) 
            cursor.commit()

#Set execution bit for task
def setExecute(exec,tid,table):
    if table=='production':
        cursor.execute("UPDATE ProductionTask SET Executing=? WHERE TaskID=?",exec,tid) 
    else:
        cursor.execute("UPDATE CustomTask SET Executing=? WHERE TaskID=?",exec,tid) 
    cursor.commit()

#Write to log
def writeLog(type,msg,disp):
    #logging.info(msg)
    if disp:
        print(msg)
    if(type=='ms'):
        cursor.execute("UPDATE MessageTable SET MSMsg=? WHERE MsgID=1",msg) 
        cursor.commit()
#Read from log
def readLog(type):
    if(type=='ms'):
        cursor.execute("SELECT MSMsg FROM MessageTable WHERE MsgID=1") 
        row = cursor.fetchone() 
        return row[0]

#Find available work order in each station
def findWO(stn):
    statement="SELECT TOP 1 * FROM wo_stn{} WHERE processed_qty=0 AND status='NEW'".format(stn)
    cursor.execute(statement)
    row=cursor.fetchone()
    return row

#Set work order completed
def setWOComplete(stn,wonum):
    statement="UPDATE wo_stn{} SET status='COMPLETED' WHERE wo_number='{}'".format(stn,wonum)   
    cursor.execute(statement) 
    cursor.commit()

#Set work order start
def setWOStart(stn,wonum):
    statement="UPDATE wo_stn{} SET status='STARTED' WHERE wo_number='{}'".format(stn,wonum)   
    cursor.execute(statement) 
    cursor.commit()

#Check if work order all completed or no order is in the table
def checkWOComplete(stn):
    statement="SELECT CASE WHEN COUNT(*) = 0 THEN 'true'WHEN COUNT(*) = SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) THEN 'true' ELSE 'false' END AS all_completed FROM {}".format(stn)
#Get work order
def writeWO(wolist):
    reqqty=5
    
    for wo in wolist:
        cursor.execute("INSERT INTO wo_stn1 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn2 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn3 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn4 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn5 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn6 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
#Write into Work Order
def writeWO(wolist):
    reqqty=12
    
    for wo in wolist:
        cursor.execute("INSERT INTO wo_stn1 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn2 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn3 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn4 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn5 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()
        cursor.execute("INSERT INTO wo_stn6 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor.commit()

    print('<DB> Write Work Order to all stations')
        # cursor.execute("INSERT INTO WOQueue (WOID) VALUES (?)",wo.woid)
        # cursor.commit()

def getWO():
    wo_list.clear()
    cursor.execute("SELECT * FROM WOList") 
    row = cursor.fetchone() 
    while row:
        wo=WO(row[1],row[2],row[3])
        wo_list.append(wo)
        row = cursor.fetchone()

    return wo_list

def getWOID(wo_id):
    wo_list.clear()
    cursor.execute("SELECT * FROM WOList WHERE WOID=?",wo_id) 
    row = cursor.fetchone() 
    while row:
        wo=WO(row[1],row[2],row[3])
        wo_list.append(wo)
        row = cursor.fetchone()

    return wo_list
#Get work order queue information
def getWOQ(stn):
    if stn>6 or stn<1:
        print('No such station!')
    else:
        cursor.execute("SELECT * FROM WOQueue")
        row = cursor.fetchone() 
        while row:
            stat=row[2*stn]
            if stat=='a':
                return row[1]
            row = cursor.fetchone()

#Create custom request queue
def writeCustomReq(reqid,dest,priority):
    cursor.execute("INSERT INTO CustomRequest (reqid,dest,priority,status) VALUES (?,?,?)",reqid,dest,priority,'NEW')
    cursor.commit()
 #Get priority task id
def getCustomTaskID(priority):
    cursor.execute("SELECT TOP 1 * FROM CustomRequest WHERE priority=? AND status='NEW'",priority) 
    row = cursor.fetchone() 
    return row[1]

 #Get normal task id
def getCustomNTaskID():
    cursor.execute("SELECT TOP 1 * FROM CustomRequest WHERE priority=0 AND status='NEW'") 
    row = cursor.fetchone() 
    return row[1]

#Check if priority task is active   
def checkPriorityTask():
    cursor.execute("SELECT * FROM CustomRequest WHERE priority=1 AND status='NEW'") 
    row = cursor.fetchone() 
    if row:
        return True
    else:
        
        return False
    
#Check if there is any normal custom request
def checkNormalTask():
    cursor.execute("SELECT * FROM CustomRequest WHERE priority=0 AND status='NEW'") 
    row = cursor.fetchone() 
    if row:
        return True
    else:
        return False

#Change Custom Request status
def setCRStatus(reqid):
    cursor.execute("UPDATE CustomRequest SET status='PROCESSING' WHERE reqid = ?",reqid)
    cursor.commit()
    
    
#Set work order, station number and status (a-available,p-in progress, c-completed, f-fault)
def updateWO(wo_id,stn,stat):
   
    if stn==1:
        cursor.execute("UPDATE WOQueue SET USStatus = ?, USLastUpd = ? WHERE WOID=?",stat,datetime.datetime.now(),wo_id) 
    elif stn==2:
        cursor.execute("UPDATE WOQueue SET FSStatus = ?, FSLastUpd = ? WHERE WOID=?",stat,datetime.datetime.now(),wo_id) 
    elif stn==3:
        cursor.execute("UPDATE WOQueue SET CSStatus = ?, CSLastUpd = ? WHERE WOID=?",stat,datetime.datetime.now(),wo_id) 
    elif stn==4:
        cursor.execute("UPDATE WOQueue SET LSStatus = ?, LSLastUpd = ? WHERE WOID=?",stat,datetime.datetime.now(),wo_id) 
    elif stn==5:
        cursor.execute("UPDATE WOQueue SET ISStatus = ?, ISLastUpd = ? WHERE WOID=?",stat,datetime.datetime.now(),wo_id) 
    elif stn==6:
        cursor.execute("UPDATE WOQueue SET PSStatus = ?, PSLastUpd = ? WHERE WOID=?",stat,datetime.datetime.now(),wo_id) 
    else:
        print('Invalid station number')
    cursor.commit()

#Get destination mapping for particular action
def getFlow(action):
    cursor.execute("SELECT * FROM ActionFlow WHERE FlowAction= ?",action) 
    row = cursor.fetchone() 
    return row[2]

#print(getIP(1))
#Return user
def getUser(username):
    cursor.execute("SELECT * FROM UserTable WHERE username= ?",username) 
    row = cursor.fetchone() 
    if row:
        user=User(row[1],row[2]) 
        return user
    else:
        return ''

#Check if user exists
def userExist(username):
    cursor.execute("SELECT * FROM UserTable WHERE username= ?",username) 
    row=cursor.fetchone()
    if row:
        return True
    else:
        return False

#Create user with username and hashed password
def addUser(username,password):
    cursor.execute("INSERT INTO UserTable (username,password) VALUES (?,?)",username,password) 
    
    cursor.commit()  
    
def getUserName(userid):
    print(userid)
    cursor.execute("SELECT * FROM UserTable WHERE username=?",userid) 
    row = cursor.fetchone() 
    if row:
        print(row[0])
        return row[0]
    

