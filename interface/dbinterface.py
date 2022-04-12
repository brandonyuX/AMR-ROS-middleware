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



#Set database parameters
server = 'NEL-PC\WINCC' 
database = 'M8MMiddlewareDB' 
username = 'sa' 
password = 'saadm1n@m8m' 

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

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
        req=PLCReq(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        req_list.append(req)
        row = cursor.fetchone()

    #Fetch Robot current status
    cursor.execute("SELECT * FROM Robot") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        rbt=Robot(row[0],row[1],row[2],row[3],row[4],row[5])
        rbt_list.append(rbt)
        row = cursor.fetchone()
    #print('Updated variable from DB!')
    #time.sleep(3)
    
    return rc_list,sm_list,req_list,rbt_list
        
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
        tsk=SubTask(row[1],row[2],row[3],row[5])
        
        subtsk_list.append(tsk)
        row = cursor.fetchone()
    return subtsk_list

def getTaskList():
     #Fetch Robot task list
    tsk_list.clear()
    cursor.execute("SELECT * FROM Task") 
    row = cursor.fetchone() 
    while row: 
        #print(row[0])
        tsk=Task(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        
        tsk_list.append(tsk)
        row = cursor.fetchone()

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


def insertReq(plcid,reqid,pickup,destloc,priority,reqtime):
    

    cursor.execute("INSERT INTO PLCRequest(PLCID,ReqID,PickUp,DestLoc,Priority,ReqTime) VALUES (?,?,?,?,?,?)",plcid,reqid,pickup,destloc,priority,reqtime)
    cursor.commit()

def writeTask(finalrid,reqid,rbt_list,req_list):
    cost=(next((x for x in rbt_list if x.rid == finalrid), None).cost)
    startloc=(next((x for x in rbt_list if x.rid == finalrid), None).currloc)
    destloc=(next((x for x in req_list if x.reqid == reqid), None).destloc)
    print(startloc)
    print(destloc)
    now = datetime.datetime.utcnow()
    cursor.execute("INSERT INTO Task (RobotID,ReqID,Completed,TaskCode,TaskDur,StartLoc,EndLoc,LastUpd) VALUES (?,?,?,?,?,?,?,?)",finalrid,reqid,0,000,cost,startloc,destloc,now.strftime('%Y-%m-%d %H:%M:%S'))
    cursor.commit()

def writeSubTask(tsklist):
    
    for tsk in tsklist:
        cursor.execute("INSERT INTO SubTask (TaskModelID,ActionType,Step,EndStep,Command) VALUES (?,?,?,?,?)",tsk.tskmodno,tsk.action,tsk.step,len(tsklist),tsk.cmd)
        cursor.commit()


print(getIP(1))

#insertReq(101,2,1,'Station 3',2,now.strftime('%Y-%m-%d %H:%M:%S'))

