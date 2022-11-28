#This file will provide the interface to communicate with the robot and update database 

import roslibpy
import pyodbc
import sys
import threading
import time

from sqlalchemy import true


sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface

#Define ros connection
client = roslibpy.Ros(host="192.168.0.110", port=8080)

taskid=0

def connect():
    print('<RI>Connecting to ROS robot')
    try:
        
        client.run(timeout=1)
        dbinterface.updateRbtStatus(True,1)
        print('<RI>Connection suceeded')
    except:
        dbinterface.writeLog('ms','<ERR>No connection to ROS robot',True)
        dbinterface.updateRbtStatus(False,1)

        #sys.exit(0)

#Specify connection to ros host
#ros = roslibpy.Ros(host='localhost', port=9090)
#ros.run()

def get_single_info():
    #client = roslibpy.Ros(host="172.23.44.12", port=8080)
    posmsg=''
    #client.run()
    listener = roslibpy.Topic(client, '/rosout', 'rosgraph_msgs/Log')
    listener.subscribe(receive_single_message)
    

def receive_single_message(message):
            print(message)

def get_info():
    # Loop through ip in configuration file
    pos={}
    iplist=dbinterface.getIPList()
    try:
        #Connect and check for connection before proceeding
        
       

        def start_receive_info():
            #Throttle pose received to 1 per sec
            listener2 = roslibpy.Topic(client, '/rosout','rosgraph_msgs/Log',throttle_rate=2000)
            listener2.subscribe(store_rosout)
            listener = roslibpy.Topic(client, '/robot_pose', 'geometry_msgs/Pose',throttle_rate=3000)
            listener.subscribe(store_pose)
            listener3=roslibpy.Topic(client,'/move_completed','htbot/status')
            listener3.subscribe(move_complete)
            #statlisterner=roslibpy.Topic(client,'/stat','htbot/stat')
            #statlisterner.subscribe(stat_callback)
        
        t1 = threading.Thread(target=start_receive_info)
        t1.start()
        t1.join()
    except:
        print('No connection to ROS Robot')
    
    
   
#Heartbeat function
def stat_callback(message):
    
    print(message)


   
#Move completed callback function
def move_complete(message):
    tsklist=dbinterface.getTaskListTop()
    #print(message)
    
    dbinterface.setExecute(0,tsklist[0].tid)
    print('<RI>Move Completed')
   
    # tsk_list=dbinterface.getTaskList()
    # req_list=dbinterface.getReqList()
    
    # dbinterface.updateRbtMsg(tsk_list[0].rid,'Robot Reached Station')
    # dbinterface.updateRbtStatus('AVAILABLE',tsk_list[0].rid)
    # dbinterface.updateReqStatus('Request Completed',tsk_list[0].reqid)
    # #print(req_list[0].destloc)
    # dbinterface.updateRbtLoc(tsk_list[0].reqid,req_list[0].destloc)
    # dbinterface.setExecute(0,tsk_list[0].tid)
    

    
    
def store_pose(message):
    
    #print(message)
    x=message['position']['x']
    y=message['position']['y']
    r=message['orientation']['w']
    x=round(x,5)
    y=round(y,5)
    r=round(r,5)
    #dbinterface.updateRbtPosStatus(1,x,y,r)       

def store_rosout(message):
    rosmsg=message['msg']
    #print(rosmsg)
    # if rosmsg=='------------ jstate 21 : down cmd completed. -----------':
    #     print('Jack down completed')
    # elif rosmsg=='------------ jstate 11 : up cmd completed. -----------':
    #     print('Jack Up Completed')
    dbinterface.updateRbtMsg(1,rosmsg)

def jack_up(rid):
    ip=dbinterface.getIP(rid)
    #print(ip)
    #client = roslibpy.Ros(host=ip, port=8080)
    #client.run()
    
    button = roslibpy.Topic(client, '/button','std_msgs/UInt16')
    msg=roslibpy.Message({'data':400})
    button.publish(msg)
    #client.terminate()

def jack_down(rid):
    ip=dbinterface.getIP(rid)
    #print(ip)
    #client = roslibpy.Ros(host=ip, port=8080)
    #client.run()
    button = roslibpy.Topic(client, '/button','std_msgs/UInt16')
    msg=roslibpy.Message({'data':401})
    
    button.publish(msg)
    #client.terminate()

def publish_info(rid):
    
    print('<RI>Publish goal information to robot {}'.format(rid))

#Publish move command to robot through robot interface
#Input: rid - Robot ID, stn - Station
def publish_cmd(rid,stn): 
    stnmap={0:'REF',1:'STN1',2:'STN2',3:'STN3'} 
    ip=dbinterface.getIP(rid)
    
    try:
        #client = roslibpy.Ros(host=ip, port=8080)
        #client.run(timeout=1)
        cmdsrv = roslibpy.Service(client,'/web_cmd','htbot/mqueue')
        #print(stn)
        cmdreq=roslibpy.ServiceRequest(dict(cmd=15, lps=stn))
       
        
        result=cmdsrv.call(cmdreq)
        print(result)
        print('<RI>Command successfully sent to robot {}'.format(rid))
        return True
    except:
        print("<ERR>Fail to connect to robot")
        return False
    #client.terminate()

def abort():
    try:
        #client = roslibpy.Ros(host=ip, port=8080)
        #client.run(timeout=1)
        cmdsrv = roslibpy.Service(client,'/web_cmd','htbot/mqueue')
        
       
        cmdreq=roslibpy.ServiceRequest(dict(cmd=29))
        
        
        result=cmdsrv.call(cmdreq)
        print(result)
        print('<RI>Robot movement aborted')
        return True
    except:
        print("<ERR>Fail to connect to robot")
        return False

def localize(rid):
    # ip=dbinterface.getIP(rid)
    # print(ip)
    #client = roslibpy.Ros(host=ip, port=8080)
    #client.run()
    pm=roslibpy.Param(client,'mapflag')
    pm.name='ZeroLocalisation'
    pm.set(True)
    #client.terminate()

#Get task list from database
def get_task_list():
    
    pass

def startup():
    
    print('<RI>Robot Interface stack start up')
    #Start connection
    connect()
    get_info()
#publish_cmd(1,2)
#localize(1)
#get_single_info()

#jack_down(1)
#get_single_info()
def movetoloc(stn):
    print('<RI> Moving to {}'.format(stn))
    time.sleep(5)
    return True