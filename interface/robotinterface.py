#This file will provide the interface to communicate with the robot and update database 
import roslibpy
import pyodbc
import sys
import threading
import time

from sqlalchemy import true


sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface




#Specify connection to ros host
#ros = roslibpy.Ros(host='localhost', port=9090)
#ros.run()

def get_single_info():
    client = roslibpy.Ros(host="172.23.44.12", port=8080)
    posmsg=''
    client.run()
    listener = roslibpy.Topic(client, '/rosout', 'rosgraph_msgs/Log')
      
    listener.subscribe(receive_single_message)
    

def receive_single_message(message):
            print(message)

def get_info():
    # Loop through ip in configuration file
    pos={}
    iplist=dbinterface.getIPList()
    client = roslibpy.Ros(host="172.23.44.12", port=8080)
    client.run()
    cmdsrv = roslibpy.Service(client,'/web_cmd','htbot/mqueue')
    # cmdreq=roslibpy.ServiceRequest(values={
    #                 cmd : 1,
    #                 LP : 0,
    #                 GN : 0,
    #                 gps : "",
    #                 lps : "POWER",
    #                     pw : "",
    #                 tx : 1.0,
    #                 ty : 2.0,
    #                 tz : 3.0,
    #                 rx : 0.0,
    #                     ry : 0.0,
    #                 rz : 0.0,
    #                 rw : 0.0,
    #                 prd : 0.0,
    #                     pra : 0.0,
    #                 psd : 0.0,
    #                 psa : 0.0,
    #                 prd1 : 0.0,
    #                 pra1 : 0.0,
    #                 psd1 : 0.0,
    #                 psa1 : 0.0,
    #                 align : 0.0,
    #                 func : 0.0 
    #             })
    

    #print('Subcribed')
    def start_receive_pose():
       #Throttle pose received to 1 per sec
        listener2 = roslibpy.Topic(client, '/rosout','rosgraph_msgs/Log',throttle_rate=1000)
        listener2.subscribe(store_rosout)
        listener = roslibpy.Topic(client, '/robot_pose', 'geometry_msgs/Pose',throttle_rate=1000)
        listener.subscribe(store_pose)
        listener3=roslibpy.Topic(client,'/move_completed','htbot/status')
        listener3.subscribe(move_complete)
        
    
    t1 = threading.Thread(target=start_receive_pose)
    t1.start()
    t1.join()
   

   
#Move completed callback function
def move_complete(message):
    print(message)
    tsk_list=dbinterface.getTaskList()
    req_list=dbinterface.getReqList()
    
    dbinterface.updateRbtMsg(tsk_list[0].rid,'Robot Reached Station')
    dbinterface.updateRbtStatus('AVAILABLE',tsk_list[0].rid)
    dbinterface.updateReqStatus('Request Completed',tsk_list[0].reqid)
    print(req_list[0].destloc)
    dbinterface.updateRbtLoc(tsk_list[0].reqid,req_list[0].destloc)

    
    
def store_pose(message):
    
    #print(message)
    x=message['position']['x']
    y=message['position']['y']
    r=message['orientation']['w']
    #dbinterface.updateRbtPosStatus(1,x,y,r)       

def store_rosout(message):
    rosmsg=message['msg']
    print(rosmsg)
    #dbinterface.updateRbtMsg(1,rosmsg)

def jack_up(rid):
    ip=dbinterface.getIP(rid)
    print(ip)
    client = roslibpy.Ros(host=ip, port=8080)
    client.run()
    button = roslibpy.Topic(client, '/button','std_msgs/UInt16')
    msg=roslibpy.Message(data=400)
    button.publish(msg)

def jack_down(rid):
    ip=dbinterface.getIP(rid)
    print(ip)
    client = roslibpy.Ros(host=ip, port=8080)
    client.run()
    button = roslibpy.Topic(client, '/button','std_msgs/UInt16')
    msg=roslibpy.Message(data=401)
    button.publish(msg)

def publish_info(rid):
    
    print('<RI>Publish goal information to robot {}'.format(rid))

def publish_cmd(rid,stn): 
    stnmap={0:'REF',1:'STN1',2:'STN2',3:'STN3'} 
    ip=dbinterface.getIP(rid)
    print(ip)
    client = roslibpy.Ros(host=ip, port=8080)
    client.run()
    cmdsrv = roslibpy.Service(client,'/web_cmd','htbot/mqueue')
    print(stn)
    if(stn!=0):
        cmdreq=roslibpy.ServiceRequest(dict(cmd=11, LP=stn+1, lps=stnmap[stn]))
    else:
        cmdreq=roslibpy.ServiceRequest(dict(cmd=11, LP=stn, lps=stnmap[stn]))
    
    result=cmdsrv.call(cmdreq)
    print(result)
    #client.terminate()


def localize(rid):
    ip=dbinterface.getIP(rid)
    print(ip)
    client = roslibpy.Ros(host=ip, port=8080)
    client.run()
    pm=roslibpy.Param(client,'mapflag')
    pm.name='ZeroLocalisation'
    pm.set(True)
    #client.terminate()

#Get task list from database
def get_task_list():
    
    pass

def startup():

    print('Robot interface basic stack start up')
#publish_cmd(1,2)
#localize(1)
#get_single_info()