from typing import final
import pyodbc
import pymssql
import sys
import time
import datetime
import yaml
import os
# setting path
sys.path.append('../Middleware Development')

from mwclass.robotconfig import RobotConfig
from mwclass.stationmap import StationMap
from mwclass.plcrequest import PLCReq
from mwclass.customRequest import CustomRequest
from mwclass.woPerStn import WOPerStn 
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

#custom request list
cus_req_list = []

#wo per work station list
wo_per_stn_list = []

#Get current time 
now = datetime.datetime.utcnow()
with open('server-config.yaml', 'r') as f:
    doc = yaml.safe_load(f)

#Set database parameters from config files
server=doc['DATABASE']['SERVER']
database=doc['DATABASE']['DB']
req_qty=doc['PRODUCTION']['REQ_QTY']

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};Server='+server+';Database='+database+';Trusted_Connection=yes;MARS_Connection=Yes;')
def startup():
    global cursor
    print('<DB>Database stack start up')
    os.environ['reqqty']=str(req_qty)
    os.environ['prevrej']='0'
    
    
    
    # print(server)
    # cnxn=pymssql.connect(server='SMARTLABFNP\SQLEXPRESS', database='M8MMiddlewareDB', trusted=True)
    cnxn.autocommit=True
    cursor = cnxn.cursor()
    print('<DB>Database connected')

def getBundleInfo():
   
   
    rbt_list=[]
    
  

    
    cursor2=cnxn.cursor()
    #Fetch Robot current status
    cursor2.execute("SELECT * FROM Robot") 
    row = cursor2.fetchone() 
    while row: 
        #print(row[0])
        rbt=Robot(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        rbt_list.append(rbt)
        row = cursor2.fetchone()
    cursor2.close()
    #print('Updated variable from DB!')
    #time.sleep(3)
    
    return rbt_list

def getRobotList():
    #Fetch Robot current status
    cursor.execute("SELECT * FROM Robot") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        rbt=Robot(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        rbt_list.append(rbt)
        row = cursor.fetchone()
    return rbt_list


def getSubTaskList():
    subtsk_list=[]
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
    subtsk_list=[]
    if tskmodno == "":
        cursor.execute("SELECT * FROM SubTask")
    else: 
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
    subtsk_list=[]
    cursor.execute("SELECT * FROM SubTask WHERE TaskModelID = ? AND Step=?",tskmodno,step) 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=SubTask(row[0],row[1],row[2],row[3],row[4],row[5])
        
        subtsk_list.append(tsk)
        row = cursor.fetchone()
    return subtsk_list

def getReqList():
    req_list=[]
    #Fetch PLC request list from database
    cursor.execute("SELECT * FROM PLCRequest") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        req=PLCReq(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
        req_list.append(req)
        row = cursor.fetchone()
    return req_list

def getProductionTaskList(data=None):
     #Fetch Robot task list
    tsk_list=[]
    cursor2=cnxn.cursor()
    match data:
        case None:
            cursor2.execute("SELECT * FROM ProductionTask WHERE Completed=0") 
        case 'all':
            cursor2.execute("SELECT * FROM ProductionTask") 
    
    row = cursor2.fetchone() 
    while row: 
        #print(row[0])
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13])
        tsk_list.append(tsk)
        row = cursor2.fetchone()
    cursor2.close()
    # print(len(tsk_list))
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
    tsk_list=[]
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT TOP 1 * FROM ProductionTask WHERE Completed=0 ORDER BY TaskID asc") 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13])  
        tsk_list.append(tsk)
    
    return tsk_list

#Get the latest custom task that is not completed
def getCustomListTop():
     #Fetch Robot task list
    tsk_list=[]
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT TOP 1 * FROM CustomTask WHERE Completed=0 ORDER BY TaskID asc") 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[15])  
        tsk_list.append(tsk)
    
    return tsk_list

#Set to complete all related task
def forceTaskComplete(reqid,table):
    if table=='production':
        cursor.execute("UPDATE ProductionTask SET Completed=1 WHERE ReqID=?",reqid) 
    else:
        cursor.execute("UPDATE CustomTask SET Completed=1 WHERE WMSReqID=?",reqid) 

    cursor.commit()
#Get all custom task that is not completed
def getCustomTaskList(data=None):
    tsk_list=[]
    cursor2=cnxn.cursor()
    #Fetch custom task list
    match data:
        case None:
            cursor2.execute("SELECT * FROM CustomTask WHERE Completed=0") 
        case 'all':
            cursor2.execute("SELECT * FROM CustomTask") 
    
    row = cursor2.fetchone()

    while row:
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[15])
        tsk_list.append(tsk)
        row = cursor2.fetchone()
    cursor2.close()
    return tsk_list

#Get all custom request
def getCustomRequestList(data=None):
    cus_req_list=[]
    #Fetch custom request list
    cursor2=cnxn.cursor()
    match data:
        case None:
            cursor2.execute("SELECT * FROM CustomRequest WHERE status='NEW'") 
        case 'all':
            cursor2.execute("SELECT * FROM CustomRequest") 
    row = cursor2.fetchone()

    while row:
        cus_req = CustomRequest(row[0],row[1],row[2],row[3],row[4],row[5])
        cus_req_list.append(cus_req)
        row = cursor2.fetchone()

    cursor2.close()
    return cus_req_list

#Return WMS Task ID
def getWMSTID(tid):
    cursor.execute("SELECT WMSTID FROM CustomTask WHERE TaskID=?",tid)
    row = cursor.fetchone() 
    if row:
        return row[0]
    
#Set next task complete
def setNxtComp(tid):
    cursor.execute("UPDATE CustomTask SET Completed=1 WHERE TaskID=?",tid+1) 
    cursor.commit()
#Check if uncompleted task exists in Custom Task table
def checkCTExist():
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT * FROM CustomTask WHERE Completed=0") 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        return True
    else:
        return False

#Check if uncompleted task exists in Production Task table
def checkProdExist():
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT * FROM ProductionTask WHERE Completed=0") 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        return True
    else:
        return False 
def getIPList():
    iplist=[]
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT RobotIP FROM Configuration") 
    row = cursor2.fetchone() 

    while row: 
        #print(row[0])
        iplist.append(row[0])
        row = cursor2.fetchone()
    cursor2.close()
    return iplist

def getIP(rid):
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT RobotIP FROM Configuration WHERE RobotID=?",rid) 
    row = cursor2.fetchone() 
    cursor2.close()
    return row[0]


def insertReq(plcid,reqid,destloc,priority,reqtime,tskmodno):
    cursor.execute("INSERT INTO PLCRequest(PLCID,ReqID,DestLoc,Priority,ReqTime,TaskModelNo) VALUES (?,?,?,?,?,?)",plcid,reqid,destloc,priority,reqtime,tskmodno)
    cursor.commit()


def insertRbtTask(destloc,tskmod,task,reqid=100):
    cursor.execute("SELECT EndStep FROM SubTask WHERE TaskModelID=?",tskmod) 
    row=cursor.fetchone()
    es=row[0]
    cursor.execute("INSERT INTO ProductionTask(RobotID,Completed,TaskCode,CurrStep,EndStep,DestLoc,Executing,TaskModelID,ReqID,MoveStep,HSMsg) VALUES (?,?,?,?,?,?,?,?,?,?,?)",1,0,0,1,es,destloc,0,tskmod,reqid,0,task)
    cursor.commit()
    print('<DB> Write to robot task destination {}'.format(destloc))

#Insert custom task from WMS
def insertCustomTask(destloc,tskmod,wmsreq,wmstsk,action):
    cursor.execute("SELECT EndStep FROM SubTask WHERE TaskModelID=?",tskmod) 
    row=cursor.fetchone()
    es=row[0]
    cursor.execute("INSERT INTO CustomTask(RobotID,Completed,TaskCode,CurrStep,EndStep,DestLoc,Executing,TaskModelID,WMSReqID,WMSTID,HSMsg,MoveStep) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",1,0,0,1,es,destloc,0,tskmod,wmsreq,wmstsk,action,0)
    cursor.commit()
    print('<DB> Write to robot task destination {}'.format(destloc))

#Write movestep
def incMoveStep(tid,table):
    cursor3=cnxn.cursor()
    if table=='production':
        
        cursor3.execute("SELECT MoveStep FROM ProductionTask WHERE TaskID=?",tid) 
        row = cursor3.fetchone() 
        newstep=row[0]+1
        cursor3.execute("UPDATE ProductionTask SET MoveStep = ? WHERE TaskID=?",newstep,tid) 
        cursor3.commit()
    else:
        cursor3.execute("SELECT MoveStep FROM CustomTask WHERE TaskID=?",tid) 
        row = cursor3.fetchone() 
        newstep=row[0]+1
        cursor3.execute("UPDATE CustomTask SET MoveStep = ? WHERE TaskID=?",newstep,tid) 
        cursor3.commit()
    cursor3.close()

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
        cursor.execute("INSERT INTO SubTask (TaskModelID,ActionType,Step,EndStep,Command) VALUES (?,?,?,?,?)",tsk.tmid,tsk.cmd,tsk.currstep,len(tsklist),tsk.cmd)
        cursor.commit()

def updateReqStatus(status,reqid):
    cursor.execute("UPDATE PLCRequest SET Status = ? WHERE ReqID=?",status,reqid) 
    cursor.commit()

def updateReqDest(loc,reqid):
    cursor.execute("UPDATE PLCRequest SET DestLoc = ? WHERE ReqID=?",loc,reqid) 
    cursor.commit()

def updateRbtStatus(status,rbtid):
    cursor2=cnxn.cursor()
    cursor2.execute("UPDATE Robot SET Avail = ? WHERE RobotID=?",status,rbtid) 
    cursor2.commit()
    cursor2.close()

#Update robot charging
def updateRbtCharge(rbtid,state):
    cursor.execute("UPDATE Robot SET Charging = ? WHERE RobotID=?",state,rbtid) 
    cursor.commit()

def checkCharging(rbtid):
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT * FROM Robot WHERE Charging = 1 AND RobotID=?",rbtid) 
    row=cursor2.fetchone()
    cursor2.close()
    if row:
        return True
    else:
        return False

def updateRbtLoc(rbtid,currloc):
    cursor2=cnxn.cursor()
    cursor2.execute("UPDATE Robot SET CurrentLoc=? WHERE RobotID=?",currloc,rbtid) 
    cursor2.commit()
    cursor2.close()

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
    cursor2=cnxn.cursor()
    cursor2.execute("UPDATE Robot SET BattLvl=? WHERE RobotID=?",battlvl,rbtid) 
    cursor2.commit()
    cursor2.close()

#Update position status to database
def updateRbtMsg(rbtid,msg):
    cursor2=cnxn.cursor()
    cursor2.execute("UPDATE Robot SET msg=? WHERE RobotID=?",msg,rbtid) 
    cursor2.commit()
    cursor2.close()

#Delete task based on request id
def deltask(reqid):
    cursor.execute("DELETE FROM ProductionTask WHERE ReqID = ?",reqid) 
    cursor.commit()

#Increment step to task customtask
def incStep(tid,step,comp=False,table=None):
    print(f'<DB>Increase for {tid} for {table} ')
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
    cursor3=cnxn.cursor()
    print(f'<DB>Set Execute for {tid} for {table} ')
    if table=='production':
        cursor3.execute("UPDATE ProductionTask SET Executing=? WHERE TaskID=?",exec,tid) 
    else:
        cursor3.execute("UPDATE CustomTask SET Executing=? WHERE TaskID=?",exec,tid) 
    cursor3.commit()
    cursor3.close()

#Write to log
def writeLog(type='ms',msg='',disp=True):
    #logging.info(msg)

    if disp:
        print(msg)
    if(type=='ms'):
        cursor2=cnxn.cursor()
        cursor2.execute("UPDATE MessageTable SET MSMsg=? WHERE MsgID=1",msg) 
        cursor2.commit()
        cursor2.close()
#Read from log
def readLog(type):
    if(type=='ms'):
        cursor2=cnxn.cursor()
        cursor2.execute("SELECT MSMsg FROM MessageTable WHERE MsgID=1") 
        row = cursor2.fetchone() 
        cursor2.close()
        return row[0]
        

#Find available work order in each station
def findWO(stn,type):
    
    cursor2 = cnxn.cursor()
    statement="SELECT TOP 1 * FROM wo_stn{} WHERE status='{}' ORDER BY wo_number asc".format(stn,type)
     
    #print (statement)
    cursor2.execute(statement)
    row=cursor2.fetchone()
    cursor2.close()
    # time.sleep(1)
    return row


#Set work order completed
def setWODBComplete(stn,wonum):
    cursor2 = cnxn.cursor()
    statement="UPDATE wo_stn{} SET status='COMPLETED' WHERE wo_number='{}'".format(stn,wonum)   
    print(statement)
    cursor2.execute(statement) 
    cursor2.commit()
    cursor2.close()

#Set work order start
def setWODBStart(stn,wonum):
    cursor2 = cnxn.cursor()
    statement="UPDATE wo_stn{} SET status='STARTED' WHERE wo_number='{}'".format(stn,wonum)   
    print(statement)
    cursor2.execute(statement) 
    cursor2.commit()
    cursor2.close()

#Check if last work order
def checkWOLast(stn,batchnum):
    cursor2 = cnxn.cursor()
    statement="SELECT * FROM wo_stn{} WHERE batch_number='{}' AND status='NEW'".format(stn,batchnum)   
    print(statement)
    cursor2.execute(statement) 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        return False
    else:
        return True
        
#Void work orders
def voidWO():
    for i in range(1,7):
        cursor2=cnxn.cursor()
        statement="UPDATE wo_stn{} SET status='VOID' WHERE status='NEW' OR status='STARTED' ".format(i)
        print(statement)
        cursor2.execute(statement)
        cursor2.commit()
        cursor2.close()

#Cancel work orders
def cancelWO():
    for i in range(1,7):
        statement="UPDATE wo_stn{} SET status='CANCELLED' WHERE status='NEW' ".format(i)
        print(statement)
        cursor.execute(statement)
        cursor.commit()

#Check if work order all completed or no order is in the table
def checkWOComplete(stn):
    statement="SELECT CASE WHEN COUNT(*) = 0 THEN 'true'WHEN COUNT(*) = SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) THEN 'true' ELSE 'false' END AS all_completed FROM {}".format(stn)


#Get work order
def writeWO(wolist):
    reqqty=int( os.environ['reqqty'])
    
    
    for wo in wolist:
        cursor2=cnxn.cursor()
        cursor2.execute("INSERT INTO wo_stn1 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque,order_num) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque,wo.ordernum)
        cursor2.commit()
        cursor2.close()

        cursor2=cnxn.cursor()
        cursor2.execute("INSERT INTO wo_stn2 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor2.commit()
        cursor2.close()

        cursor2=cnxn.cursor()
        cursor2.execute("INSERT INTO wo_stn3 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor2.commit()
        cursor2.close()

        cursor2=cnxn.cursor()
        cursor2.execute("INSERT INTO wo_stn4 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque,expiry_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque,wo.expdate)
        cursor2.commit()
        cursor2.close()

        cursor2=cnxn.cursor()
        cursor2.execute("INSERT INTO wo_stn5 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor2.commit()
        cursor2.close()

        cursor2=cnxn.cursor()
        cursor2.execute("INSERT INTO wo_stn6 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
        cursor2.commit()
        cursor2.close()

#Overwrite station 6 required quantity in respect to rejected qty
def writeStn6Qty(newqty,bnum,wolast):
    wolast=wolast+1
    statement=f"""UPDATE wo_stn6
        SET required_qty = {newqty}
        WHERE batch_number = '{bnum}'
        AND wo_id = (SELECT wo_id
        FROM (SELECT wo_id, ROW_NUMBER() OVER (ORDER BY wo_id DESC) AS row_num
            FROM wo_stn6
            WHERE batch_number = '{bnum}') subq
        WHERE subq.row_num = {wolast});"""
    cursor.execute(statement)
    cursor.commit()
     


#Write into Work Order
# def writeWO(wolist):
#     reqqty=12
    
#     for wo in wolist:
#         cursor.execute("INSERT INTO wo_stn1 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
#         cursor.commit()
#         cursor.execute("INSERT INTO wo_stn2 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
#         cursor.commit()
#         cursor.execute("INSERT INTO wo_stn3 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
#         cursor.commit()
#         cursor.execute("INSERT INTO wo_stn4 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
#         cursor.commit()
#         cursor.execute("INSERT INTO wo_stn5 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
#         cursor.commit()
#         cursor.execute("INSERT INTO wo_stn6 (batch_number,wo_number,manufacture_date,fnp_date,init_serial_number,required_qty,processed_qty,start_time,end_time,status,fill_volume,target_torque) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",wo.batchid,wo.wolist,wo.mfgdate,wo.fnpdate,wo.sn,reqqty,0,'','','NEW',wo.fillvol,wo.torque)
#         cursor.commit()

#     print('<DB> Write Work Order to all stations')
#         # cursor.execute("INSERT INTO WOQueue (WOID) VALUES (?)",wo.woid)
#         # cursor.commit()

def getWO():
    wo_list=[]
    cursor.execute("SELECT * FROM WOList") 
    row = cursor.fetchone() 
    while row:
        wo=WO(row[1],row[2],row[3])
        wo_list.append(wo)
        row = cursor.fetchone()

    return wo_list

def getWOID(wo_id):
    wo_list=[]
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

#Check if work order exist in the system
def checkWOExist(batchnum):
    cursor2=cnxn.cursor()
    cursor2.execute('SELECT * FROM wo_stn1 WHERE batch_number = ?',batchnum)
    row=cursor2.fetchone()
    if(row):
        return True
    else:
        return False
#Get work order list based on stn number
def getWOList(WOStn):
    if int(WOStn) > 6 or int(WOStn) < 1:
        print('No such station!')
    else:
        wo_per_stn_list=[]
        
        if int(WOStn) == 1:
            sqlmsg = "SELECT * FROM wo_stn1 WHERE status = 'NEW'"
        elif int(WOStn) == 2:
            sqlmsg = "SELECT * FROM wo_stn2 WHERE status = 'NEW'"
        elif int(WOStn) == 3:
            sqlmsg = "SELECT * FROM wo_stn3 WHERE status = 'NEW'"
        elif int(WOStn) == 4:
            sqlmsg = "SELECT * FROM wo_stn4 WHERE status = 'NEW'"
        elif int(WOStn) == 5:
            sqlmsg = "SELECT * FROM wo_stn5 WHERE status = 'NEW'"
        else:
            sqlmsg = "SELECT * FROM wo_stn6 WHERE status = 'NEW'"

        cursor.execute(sqlmsg)
        row = cursor.fetchone() 

        if int(WOStn) == 1:
            while row:
                wo_line = WOPerStn(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],None)
                wo_per_stn_list.append(wo_line)
                row = cursor.fetchone()
        elif int(WOStn) == 4:
            while row:
                wo_line = WOPerStn(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],None,row[13])
                wo_per_stn_list.append(wo_line)
                row = cursor.fetchone()
        else:
            while row:
                wo_line = WOPerStn(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],None,None)
                wo_per_stn_list.append(wo_line)
                row = cursor.fetchone()

    return wo_per_stn_list
def writeWOState(stn,wo,state):
    statement=f"UPDATE wo_stn{stn} SET state = '{state}' WHERE wo_number = '{wo}'"
    cursor.execute(statement)
    cursor.commit()         
    
#Delete work order
def deleteWOByStn(woStn,woID):
    sqlmsg = "DELETE FROM wo_stn" + str(woStn) + " WHERE wo_id = " + str(woID)
    cursor.execute(sqlmsg) 
    cursor.commit()

#Delete custom request
def deleteCusReq(cID):
    sqlmsg = "DELETE FROM CustomRequest" + " WHERE cid = " + str(cID)
    cursor.execute(sqlmsg) 
    cursor.commit()

#Delete custom task
def deleteCusTask(taskID):
    sqlmsg = "DELETE FROM CustomTask" + " WHERE TaskID = " + str(taskID)
    cursor.execute(sqlmsg) 
    cursor.commit()

#Delete production task
def deleteProductionTask(taskID):
    sqlmsg = "DELETE FROM ProductionTask" + " WHERE TaskID = " + str(taskID)
    cursor.execute(sqlmsg) 
    cursor.commit()

#Delete robot
def deleteRobot(robotID):
    sqlmsg = "DELETE FROM Robot" + " WHERE RobotID = " + str(robotID)
    cursor.execute(sqlmsg) 
    cursor.commit()

#Create custom request queue
def writeCustomReq(reqid,priority):
    cursor.execute("INSERT INTO CustomRequest (reqid,priority,status) VALUES (?,?,?)",reqid,priority,'NEW')
    cursor.commit()
    pass
 #Get priority task id
def getCustomTaskID(priority):
    cursor.execute("SELECT TOP 1 * FROM CustomRequest WHERE priority=? AND status='NEW' ORDER BY cid DESC",priority) 
    row = cursor.fetchone() 
    return row[1]

 #Get normal task id
def getCustomNTaskID():
    cursor.execute("SELECT TOP 1 * FROM CustomRequest WHERE priority=0 AND status='NEW' ORDER BY cid DESC") 
    row = cursor.fetchone() 
    return row[1]

#Check if priority task is active   
def checkPriorityTask():
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT * FROM CustomRequest WHERE priority=1 AND status='NEW'") 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        return True
    else:
        
        return False
    
#Check if there is any normal custom request
def checkNormalTask():
    cursor2=cnxn.cursor()
    cursor2.execute("SELECT * FROM CustomRequest WHERE priority=0 AND status='NEW'") 
    row = cursor2.fetchone() 
    cursor2.close()
    if row:
        return True
    else:
        return False

#Change Custom Request status
def setCRStatus(status,reqid):
    cursor.execute("UPDATE CustomRequest SET status=? WHERE reqid = ?",status,reqid)
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
    
def getAccount(username):
    # Check if account exists using SQL
    cursor.execute("SELECT * FROM UserTable WHERE username=?", username)
    account = cursor.fetchone()
    if account:
        print("Account exist in database with id = {0} and username = {1}".format(account[0], account[1]))  #print user id
        return account
    
def updateRip(rip, rid):
    cursor.execute("UPDATE Configuration SET RobotIP = ? WHERE RobotID = ?",rip,rid)
    cursor.commit()
    
#DANGER OF MISUSE
#Delete from production table
def deleteAllProduction():
    cursor.execute("DELETE FROM ProductionTask") 
    cursor.commit()
#Delete from custom table
def deleteAllCustom():
    cursor.execute("DELETE FROM CustomRequest") 
    cursor.commit()
    cursor.execute("DELETE FROM CustomTask") 
    cursor.commit()

#Get all data from prod/custom table
def getTask(table):
    tasklist=[]
    match table: 
        case 'production':
            cursor.execute("SELECT * FROM ProductionTask") 
            row = cursor.fetchone() 
            while row:
                tasklist.append(row)
                row = cursor.fetchone()

            pass
        case 'custom':
            cursor.execute("SELECT * FROM CustomTask") 
            row = cursor.fetchone() 
            while row:
                tasklist.append(row)
                row = cursor.fetchone()
            pass
    return tasklist

# Delete work order
def deleteWO(wo):
    for i in range(1,7):
        statement="DELETE FROM wo_stn{} WHERE wo_number = '{}' ".format(i,wo)
        print(statement)
        cursor.execute(statement)
        cursor.commit()
    

#Delete everything from WO
def deleteAllWO():
    for i in range(1,7):
        statement="DELETE FROM wo_stn{} ".format(i)
        print(statement)
        cursor.execute(statement)
        cursor.commit()

def registerRbt(RobotID, Alias,TaskAcceptanceThres,DefaultLoc,RobotIP, ChargeThres, IdleTime):
    cursor.execute("SELECT * FROM Configuration WHERE RobotID=?", RobotID)
    row = cursor.fetchone()
    if row:
        return "Register unsuccessful! Robot(ID: {0}) already exist in database!".format(RobotID)
    else:
        cursor.execute("INSERT INTO Configuration (RobotID, Alias,TaskAcceptanceThres,DefaultLoc,RobotIP, ChargeThres, IdleTime) VALUES (?,?,?,?,?,?,?)", RobotID, Alias,TaskAcceptanceThres,DefaultLoc,RobotIP, ChargeThres, IdleTime)
        cursor.commit()
        return "Robot successfully registered!"
    # 