#This file will provide the interface to communicate with the robot and update database 
import roslibpy
import pyodbc
import sys
import threading


sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface




#Specify connection to ros host
#ros = roslibpy.Ros(host='localhost', port=9090)
#ros.run()

def get_single_info():
    client = roslibpy.Ros(host="172.23.44.12", port=8080)
    client.run()
    listener = roslibpy.Topic(client, '/robot_pose', 'geometry_msgs/Pose')
    listener.subscribe(receive_message)

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
    def start_receive_pose():
        listener = roslibpy.Topic(client, '/robot_pose', 'geometry_msgs/Pose')
        listener.subscribe(receive_message)
    
    t1 = threading.Thread(target=start_receive_pose)
    t1.start()
    t1.join()
   

    try:
        while True:
            pass
    except KeyboardInterrupt:
            client.terminate()
    # for ip in iplist:
    #     #Subscribe to topic in ros robot
    #     client = roslibpy.Ros(host=ip, port=8080)
    #     client.run()
    #     cmdsrv = roslibpy.Service(client,'/web_cmd','htbot/mqueue')
    #     cmdreq=roslibpy.ServiceRequest(values={
    #                     cmd : 1,
    #                     LP : 0,
    #                     GN : 0,
    #                     gps : "",
    #                     lps : "POWER",
    #                         pw : "",
    #                     tx : 1.0,
    #                     ty : 2.0,
    #                     tz : 3.0,
    #                     rx : 0.0,
    #                         ry : 0.0,
    #                     rz : 0.0,
    #                     rw : 0.0,
    #                     prd : 0.0,
    #                         pra : 0.0,
    #                     psd : 0.0,
    #                     psa : 0.0,
    #                     prd1 : 0.0,
    #                     pra1 : 0.0,
    #                     psd1 : 0.0,
    #                     psa1 : 0.0,
    #                     align : 0.0,
    #                     func : 0.0 
    #                 })
    #     listener = roslibpy.Topic(client, '/rosout', 'std_msgs/String')
    #     listener.subscribe(lambda message: print('rosout: ' + message['data']))

def test_async():
    pass

def start_async():
    t1 = threading.Thread(target=test_async)
    t1.start()
    t1.join()

    
def receive_message(message):
    print(message)       

def publish_info(rid):
    
    print('<RI>Publish goal information to robot {}'.format(rid))

def publish_cmd(rid):  
    ip=dbinterface.getIP(rid)
    client = roslibpy.Ros(host=ip, port=8080)
    client.run()
    cmdsrv = roslibpy.Service(client,'/web_cmd','htbot/mqueue')
    cmdreq=roslibpy.ServiceRequest(values={
                    cmd : 1,
                    LP : 0,
                    GN : 0,
                    gps : "",
                    lps : "POWER",
                        pw : "",
                    tx : 1.0,
                    ty : 2.0,
                    tz : 3.0,
                    rx : 0.0,
                        ry : 0.0,
                    rz : 0.0,
                    rw : 0.0,
                    prd : 0.0,
                        pra : 0.0,
                    psd : 0.0,
                    psa : 0.0,
                    prd1 : 0.0,
                    pra1 : 0.0,
                    psd1 : 0.0,
                    psa1 : 0.0,
                    align : 0.0,
                    func : 0.0 
                })
    cmdreq.cmd=11
    cmdreq.LP=0
    cmdreq.lps=0
    cmdsrv.call(cmdreq)
#Get task list from database
def get_task_list():
    
    pass

