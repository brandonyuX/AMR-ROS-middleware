#This file provides interface with the PLC and update the database
#Will use opcua in this example
import socket,datetime,sys,signal
import time,os
import threading


sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface
import interface.wmsinterface as wmsinterface
import logic.pathcalculate as pathcalculate
from opcua import Client,ua
HOST='127.0.0.1'
PORT=65432



decdata=''
client = Client("opc.tcp://192.168.0.253:49321")

graphdict={"CHR":1,
            "Stn1":2,
            "TPUp":3,
            "TPDown":4,
            "TPLeft":5,
            "WH":6,
            "Stn6":7,
            "CL1":8,
            "CL2":9
            }


def startup():
    try:
        client.connect()
        print('Connection to OPC Server successful!')
        t1=threading.Thread(target=readTags,daemon=True)
        t1.start()
    except:
        print("Problems connecting to OPC Server")
    

def checkProcQty(station):
    procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)
    reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(station)
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)

    procqty=procqtystate.get_value()
    reqqty=reqqtystate.get_value()

    return True if procqty==reqqty else False

def incProcQty(station):
    procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)
    procqtystate=client.get_node(procqtypath)

    procqty=procqtystate.get_value()
    newqty=procqty+1
    procqtystate.set_value(ua.DataValue(ua.Variant(newqty,ua.VariantType.UInt16)))

def writeWODetails(station,wonum,wostatus,reqqty,procqty):
    
    if station==0:
        for i in range(1,7):
            wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(i)
            wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(i)
            reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(i)
            procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(i)

            wonumstate=client.get_node(wonumpath)
            wostatusstate=client.get_node(wostatuspath)
            reqqtystate=client.get_node(reqqtypath)
            procqtystate=client.get_node(procqtypath)

            wonumstate.set_value(ua.DataValue(ua.Variant(wonum,ua.VariantType.String)))
            wostatusstate.set_value(ua.DataValue(ua.Variant(wostatus,ua.VariantType.UInt16)))
            reqqtystate.set_value(ua.DataValue(ua.Variant(reqqty,ua.VariantType.UInt16)))
            procqtystate.set_value(ua.DataValue(ua.Variant(procqty,ua.VariantType.UInt16)))
    else:
        wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)
        wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(station)
        reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(station)
        procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)

        wonumstate=client.get_node(wonumpath)
        wostatusstate=client.get_node(wostatuspath)
        reqqtystate=client.get_node(reqqtypath)
        procqtystate=client.get_node(procqtypath)

        wonumstate.set_value(ua.DataValue(ua.Variant(wonum,ua.VariantType.String)))
        wostatusstate.set_value(ua.DataValue(ua.Variant(wostatus,ua.VariantType.UInt16)))
        reqqtystate.set_value(ua.DataValue(ua.Variant(reqqty,ua.VariantType.UInt16)))
        procqtystate.set_value(ua.DataValue(ua.Variant(procqty,ua.VariantType.UInt16)))
 


def startWOACK(station):
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)

    woackstate=client.get_node(woackpath)
    woackstate.set_value(ua.DataValue(ua.Variant('RDYORD',ua.VariantType.String)))
 
def getWOACK(station):      
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)

    woackstate=client.get_node(woackpath)
    ack=woackstate.get_value()
    
    if ack=="MESACK":
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
queue=['WO001','WO002','WO003','WO004']

def getNextWO(station):
    wopath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)
    wostate=client.get_node(wopath)

    currwo=wostate.get_value()
    woindex=queue.index(currwo)
   
    if(woindex>=len(queue)-1):
        return 'end'
    else:
        return queue[woindex+1]

def writePLC(type,value,loc):
    if(loc=="Stn1"):
        if type=="rts":
            rtspath="ns=2;s=SyngentaPLC.Station1.AMR.RequestToSend"
            rtsstate=client.get_node(rtspath)
            rtsstate.set_value(ua.DataValue(ua.Variant(value,ua.VariantType.Boolean)))
        if type=="rtr":
            rtrpath="ns=2;s=SyngentaPLC.Station1.AMR.RequestToReceive"
            rtrstate=client.get_node(rtrpath)
            rtrstate.set_value(ua.DataValue(ua.Variant(value,ua.VariantType.Boolean)))
    if(loc=="WH"):
        if type=="rts":
            rtspath="ns=2;s=SyngentaPLC.Warehouse.AMR.RequestToSend"
            rtsstate=client.get_node(rtspath)
            rtsstate.set_value(ua.DataValue(ua.Variant(value,ua.VariantType.Boolean)))
        if type=="rtr":
            rtrpath="ns=2;s=SyngentaPLC.Warehouse.AMR.RequestToReceive"
            rtrstate=client.get_node(rtrpath)
            rtrstate.set_value(ua.DataValue(ua.Variant(value,ua.VariantType.Boolean)))
        if type=="resetwmsoutrdy":
            wmsoutpath="ns=2;s=SyngentaPLC.Warehouse.ItemReadyToOut"
            wmsoutstate=client.get_node(wmsoutpath)
            wmsoutstate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))

#Read plc tag
def readPLC(type,loc):
    if(loc=="Stn1"):
        #If type is tail end sensor
        if type=="te":
            itcpath="ns=2;s=SyngentaPLC.Station1.AMR.ItemOnConveyor"
            itcstate=client.get_node(itcpath)
            return itcstate.get_value()
        #If type is head end sensor
        if type=="he":
            irpath="ns=2;s=SyngentaPLC.Station1.AMR.ItemRemoved"
            irstate=client.get_node(irpath)
            return irstate.get_value()
        #If type is ready to receive
        if type=="rtr":
            rtrplcpath="ns=2;s=SyngentaPLC.Station1.AMR.ReadyToReceive"
            rtrplcstate=client.get_node(rtrplcpath)
            return rtrplcstate.get_value()
    if(loc=="WH"):
        #If type is tail end sensor
        if type=="te":
            itcpath="ns=2;s=SyngentaPLC.Warehouse.AMR.ItemOnConveyor"
            itcstate=client.get_node(itcpath)
            return itcstate.get_value()
        #If type is head end sensor
        if type=="he":
            irpath="ns=2;s=SyngentaPLC.Warehouse.AMR.ItemRemoved"
            irstate=client.get_node(irpath)
            return irstate.get_value()
        #If type is ready to receive
        if type=="rtr":
            rtrplcpath="ns=2;s=SyngentaPLC.Warehouse.AMR.ReadyToReceive"
            rtrplcstate=client.get_node(rtrplcpath)
            return rtrplcstate.get_value()
        if type=="wmsoutrdy":
            wmsoutpath="ns=2;s=SyngentaPLC.Warehouse.ItemReadyToOut"
            wmsoutstate=client.get_node(wmsoutpath)
            return wmsoutstate.get_value()
        if type=="wmsinrdy":
            wmsinpath="ns=2;s=SyngentaPLC.Warehouse.ItemReadyToOut"
            wmsinstate=client.get_node(wmsinpath)
            return wmsinstate.get_value()

def checkStnDone(stn):
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    
    
    return procqtystate.get_value()==reqqtystate.get_value()

def sendWO2PLC(stn,wo):
    
    uint16_wonum = [c.to_bytes(2, byteorder='big') for c in map(ord, wo[2])]  
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(stn)
    
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    wonumstate=client.get_node(wonumpath)
    
    reqqtystate.set_value(ua.DataValue(ua.Variant(5,ua.VariantType.UInt16)))
    procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    #wonumstate.set_value(ua.DataValue(ua.Variant(uint16_wonum,ua.VariantType.UInt16)))
    
    
    print('Sending {} to PLC'.format(wo[2]))
    
    
    
    

def readTags():
    while True:

        #Station 1 tote request and store
        reqbotpath="ns=2;s=SyngentaPLC.Station1.AMR.RequestBottle"
        rettotpath="ns=2;s=SyngentaPLC.Station1.AMR.ReturnToteBox"
        
        cp2path="ns=2;s=Syngenta.SmartLab.FNP.Info.Station6.CartonPresent2"
        ccpath="ns=2;s=Syngenta.SmartLab.FNP.CL.CustomComplete"
        
        #Station 6 tote retrieval and store
        rtbpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station6.RetrieveToteBox"
        stbpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station6.StoreToteBox"


        reqbotstate=client.get_node(reqbotpath)
        rettotstate=client.get_node(rettotpath)
        cp2state=client.get_node(cp2path)
        ccstate=client.get_node(ccpath)
        rtbstate=client.get_node(rtbpath)
        stbstate=client.get_node(stbpath)


        reqbot=reqbotstate.get_value()
        rettot=rettotstate.get_value()
        cp2=cp2state.get_value()
        cc=ccstate.get_value()
        rtb=rtbstate.get_value()
        stb=stbstate.get_value()

        #Procedure to request bottles
        if(reqbot):
            #Call WMS to retrieve bottles bottles
            #wmsinterface.reqEb()
            
            #Generate robot path and insert as a robot task
            pathinfo=pathcalculate.generate_path('WH','Stn1','')
            dbinterface.insertRbtTask(pathinfo,1)
            reqbotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

        #Procedure to return tote box
        if(rettot):
            #wmsinterface.reqstb()
            pathinfo=pathcalculate.generate_path('Stn1','WH','')
            dbinterface.insertRbtTask(pathinfo,1)
            rettotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

        if(cp2):
            wmsinterface.reqsfc()
            dbinterface.insertRbtTask('Station6;Warehouse')
            cp2state.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

        if(cc):
            os.environ['waitcomplete'] = 'True'
        
        #Fetch empty tote box from WH and go to Stn 6
        # if(rtb):
        #      #Generate robot path and insert as a robot task
        #     pathinfo=pathcalculate.generate_path('WH','Stn6','WH')
        #     dbinterface.insertRbtTask(pathinfo,6)
        #     reqbotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))



  