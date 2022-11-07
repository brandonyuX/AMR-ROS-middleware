#This file provides interface with the PLC and update the database
#Will use opcua in this example
import socket,datetime,sys

sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface
from opcua import Client
HOST='127.0.0.1'
PORT=65432


decdata=''

if __name__ == "__main__":
    #Connect to opc server
    client = Client("opc.tcp://192.168.1.201:49321")
    try:
        client.connect()
        #print(client.get_values(85))

        print('Successfully connected to OPC Server.')
    except:
        print('Error connecting to OPC')
    # finally:
    #     client.disconnect()
        
    

def decodemsg(testmsg):
    print(testmsg)

    tasktype={'0001': 'CreateTask','0002':'MoveStn','0003':'Custom Command'}

    rcvtsk=testmsg[0:4]
    rcvlen=testmsg[4:8]
    rcvseq=testmsg[8:12]
    rcvtskmod=testmsg[12:15]
    rcvreqid=testmsg[15:19]
    rcvpriority=testmsg[19:21]

    print('Task Type: {} -> {}'.format(rcvtsk,tasktype[rcvtsk]))
    print('Message Length: {}'.format(rcvlen))
    print('Message Sequence Number: {}'.format(rcvseq))
    print('Task Model Number: {}'.format(rcvtskmod))
    print('Priority: {}'.format(rcvpriority))
    
    msglen=int(rcvlen)

    stnmsg=testmsg[21:msglen]
    splitmsg=testmsg[21:msglen].split(';')
    print('The extracted stations are: ')
    for msg in splitmsg:
        print(msg)
    now = datetime.datetime.utcnow()
    formattime=now.strftime('%Y-%m-%d %H:%M:%S')
    dbinterface.insertReq(1,rcvreqid,stnmsg,int(rcvpriority),formattime,int(rcvtskmod))
    # asgrbt=1
    # asgtid=1

    # asgrbt=asgrbt.zfill(4)
    # asgtid=asgtid.zfill(4)
    # print('Task assigned to robot {} with Task ID {}'.format(asgrbt,asgtid))
    # totallen=str(len(rcvtsk)+len(rcvseq)+len(asgrbt)+len(asgtid)+4)
    # totallen=totallen.zfill(4)

    # response=rcvtsk+totallen+rcvseq+asgrbt+asgtid
    # print('Reponse to PLC: {}'.format(response))
def start_receive():
    pass

def start_send():
    pass 

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
            
                if not data:
                    break

                decdata=(data.decode('utf-8'))
                decodemsg(decdata)
                conn.sendall(data)