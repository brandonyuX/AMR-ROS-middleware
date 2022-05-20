from typing import final
import pyodbc
import sys
import time
import datetime
# setting path
sys.path.append('../Middleware Development')

from mwclass.robotconfig import RobotConfig
from mwclass.stationmap import StationMap
from mwclass.plcrequest import PLCReq
from mwclass.subtask import SubTask
from mwclass.task import Task
from mwclass.robot import Robot
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


def startup():
    global cursor
    print('<DB>Database stack start up')
    #Set database parameters
    server = 'NEL-PC\WINCC' 
    database = 'M8MMiddlewareDB' 
    username = 'sa' 
    password = 'saadm1n@m8m' 

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
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
    cursor.execute("SELECT * FROM Task") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])
        
        tsk_list.append(tsk)
        row = cursor.fetchone()

    return tsk_list


#Get the latest task that is not completed
def getTaskListTop():
     #Fetch Robot task list
    tsk_list.clear()
    cursor.execute("SELECT * FROM Task WHERE Completed=0") 
    row = cursor.fetchone() 
    if row:
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])  
        tsk_list.append(tsk)

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

def writeTask(finalrid,reqid,rbt_list,req_list):
    
    startloc=(next((x for x in rbt_list if x.rid == finalrid), None).currloc)
    destloc=(next((x for x in req_list if x.reqid == reqid), None).destloc)
    tskmodno=(next((x for x in req_list if x.reqid == reqid), None).tskmodno)
    print(startloc)
    print(destloc)
    now = datetime.datetime.utcnow()
    cursor.execute("INSERT INTO Task (RobotID,ReqID,Completed,TaskCode,CurrStep,LastUpd,Executing,TaskModelID,DestLoc,Processing) VALUES (?,?,?,?,?,?,?,?,?)",finalrid,reqid,0,000,1,now.strftime('%Y-%m-%d %H:%M:%S'),0,tskmodno,destloc,0)
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

def updateRbtLoc(rbtid,currloc):
    cursor.execute("UPDATE Robot SET CurrentLoc=? WHERE RobotID=?",currloc,rbtid) 
    cursor.commit()

#Update position status to database
def updateRbtPosStatus(rbtid,x,y,r):
    cursor.execute("UPDATE Robot SET x=?,y=?,r=? WHERE RobotID=?",x,y,r,rbtid) 
    cursor.commit()

#Update position status to database
def updateRbtMsg(rbtid,msg):
    cursor.execute("UPDATE Robot SET msg=? WHERE RobotID=?",msg,rbtid) 
    cursor.commit()

#Delete task based on request id
def deltask(reqid):
    cursor.execute("DELETE FROM Task WHERE ReqID = ?",reqid) 
    cursor.commit()

#Increment step to task 
def incStep(tid,step,comp):
    if comp:
        cursor.execute("UPDATE Task SET Completed=? WHERE TaskID=?",1,tid) 
        cursor.commit()
    cursor.execute("UPDATE Task SET CurrStep=? WHERE TaskID=?",step,tid) 
    cursor.commit()

#Set execution bit for task
def setExecute(exec,tid):
    cursor.execute("UPDATE Task SET Executing=? WHERE TaskID=?",exec,tid) 
    cursor.commit()

#Write to log
def writeLog(type,msg,disp):
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
    
#print(getIP(1))

#insertReq(101,2,1,'Station 3',2,now.strftime('%Y-%m-%d %H:%M:%S'))


