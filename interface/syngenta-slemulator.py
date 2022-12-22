#This file provides interface with the PLC and update the database
#Will use opcua in this example
import socket,datetime,sys,signal,asyncio,yaml
import time
import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'emulator-settings.yaml')
from opcua import Client,ua
with open(filename, 'r') as f:
    doc = yaml.safe_load(f)

HOST=doc['SERVER']['OPCIP']
PORT=doc['SERVER']['PORT']
startstate=[False,False,False,False,False,False,False]
qstr=doc['WO']['QUEUE']
print(qstr)
queue=qstr.split('.')

decdata=''
client = Client("opc.tcp://{}:{}".format(HOST,PORT))
neworder=False



def connectOPC():
    try:
        client.connect()
    except:
        print("Problems connecting to OPC Server")
    

def checkProcQty(station):
    
    procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)
    reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(station)
    stastatuspath="ns=2;s=Syngenta.SmartLab.FNP.Info.Station{}.StationState".format(station)
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    stastatusstate=client.get_node(stastatuspath)

    procqty=procqtystate.get_value()
    reqqty=reqqtystate.get_value()

    if procqty==reqqty:
        startstate[station-1]=False
        stastatusstate.set_value(ua.DataValue(ua.Variant(1,ua.VariantType.UInt16)))
        return True
    else:
        return False

def incProcQty(station):
    time.sleep(0.1)
    procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)
    cmdpausepath="ns=2;s=Syngenta.SmartLab.FNP.Info.Station{}.CmdPause".format(station)
    stastatuspath="ns=2;s=Syngenta.SmartLab.FNP.Info.Station{}.StationState".format(station)

    procqtystate=client.get_node(procqtypath)
    cmdpausetate=client.get_node(cmdpausepath)
    stastatusstate=client.get_node(stastatuspath)

    procqty=procqtystate.get_value()
    cmdpause=cmdpausetate.get_value()
    
    if(procqty<=19) and not cmdpause:
        newqty=procqty+1
        procqtystate.set_value(ua.DataValue(ua.Variant(newqty,ua.VariantType.UInt16)))
        stastatusstate.set_value(ua.DataValue(ua.Variant(2,ua.VariantType.UInt16)))

    elif cmdpause:
        stastatusstate.set_value(ua.DataValue(ua.Variant(3,ua.VariantType.UInt16)))

def writeWODetails(station,wonum,wostatus,reqqty,procqty):
    
    if station==0:
        for i in range(1,7):
            wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(i)
            wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(i)
            reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(i)
            procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(i)
            stastatuspath="ns=2;s=Syngenta.SmartLab.FNP.Info.Station{}.StationState".format(i)

            wonumstate=client.get_node(wonumpath)
            wostatusstate=client.get_node(wostatuspath)
            reqqtystate=client.get_node(reqqtypath)
            procqtystate=client.get_node(procqtypath)
            stastatusstate=client.get_node(stastatuspath)

            wonumstate.set_value(ua.DataValue(ua.Variant(wonum,ua.VariantType.String)))
            wostatusstate.set_value(ua.DataValue(ua.Variant(wostatus,ua.VariantType.UInt16)))
            reqqtystate.set_value(ua.DataValue(ua.Variant(reqqty,ua.VariantType.UInt16)))
            procqtystate.set_value(ua.DataValue(ua.Variant(procqty,ua.VariantType.UInt16)))
            stastatusstate.set_value(ua.DataValue(ua.Variant(2,ua.VariantType.UInt16)))
            neworder=True
    else:
        wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)
        wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(station)
        reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(station)
        procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)
        stastatuspath="ns=2;s=Syngenta.SmartLab.FNP.Info.Station{}.StationState".format(station)

        wonumstate=client.get_node(wonumpath)
        wostatusstate=client.get_node(wostatuspath)
        reqqtystate=client.get_node(reqqtypath)
        procqtystate=client.get_node(procqtypath)
        stastatusstate=client.get_node(stastatuspath)

        wonumstate.set_value(ua.DataValue(ua.Variant(wonum,ua.VariantType.String)))
        wostatusstate.set_value(ua.DataValue(ua.Variant(wostatus,ua.VariantType.UInt16)))
        reqqtystate.set_value(ua.DataValue(ua.Variant(reqqty,ua.VariantType.UInt16)))
        procqtystate.set_value(ua.DataValue(ua.Variant(procqty,ua.VariantType.UInt16)))
        stastatusstate.set_value(ua.DataValue(ua.Variant(2,ua.VariantType.UInt16)))
 


def startWOACK(station):
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)

    woackstate=client.get_node(woackpath)
    woackstate.set_value(ua.DataValue(ua.Variant('RDYORD',ua.VariantType.String)))
 
def getWOACK(station):      
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)
    wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)

    woackstate=client.get_node(woackpath)
    wonumstate=client.get_node(wonumpath)

    currwo=wonumstate.get_value()
    ack=woackstate.get_value()
    
    if ack==currwo:
        return True
    else:
        return False



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


def getNextWO(station):
    wopath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)
    wostate=client.get_node(wopath)

    currwo=wostate.get_value()
    woindex=queue.index(currwo)
   
    if(woindex>=len(queue)-1):
        return 'end'
    else:
        return queue[woindex+1]



def startWOS():
    connectOPC()
    wonum=1
    
    writeWODetails(0,queue[0],1,20,0)
    while True:
        try:
            
            for i in range(1,7):
                incProcQty(i)
                
                if(checkProcQty(i)):
                    woval=getNextWO(i)
                    if(woval=='end'):
                        print('End of Work Order for station {}'.format(i))
                        writeWODetails(i,'END',1,20,0)
                    else:
                        if(getWOACK(i)!=True):
                            startWOACK(i)
                        if(getWOACK(i)):
                            print('Detected order completion, sending {} to station {}'.format(woval,i))
                            writeWODetails(i,woval,1,20,0)
                            startstate[i]=True

                        
                        
        except KeyboardInterrupt:
            
            client.disconnect()

async def procqtyinc():
    while True:
        for i in range(0,6):
            print(i)
            if(startstate[i]):
                incProcQty(i)

# async def multiple_tasks():
#   input_coroutines = [startWOS(), procqtyinc()]
#   res = await asyncio.gather(*input_coroutines, return_exceptions=True)
#   return res

# loop = asyncio.get_event_loop()

# loop.run_until_complete(multiple_tasks())

startWOS()