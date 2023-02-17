#This file provides interface with the PLC and update the database
#Will use opcua in this example
import socket,datetime,sys,signal
import time,os
import threading,yaml


sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface
import interface.wmsinterface as wmsinterface
import logic.pathcalculate as pathcalculate
from opcua import ua,Client
HOST='127.0.0.1'
PORT=65432
with open('server-config.yaml', 'r') as f:
    doc = yaml.safe_load(f)

production=doc['SERVER']['PRODUCTION']



decdata=''
try:
    client = Client("opc.tcp://192.168.0.253:49321",timeout=60*8)
except KeyboardInterrupt:
    print("Interrupted by user")
            
client = Client("opc.tcp://192.168.0.250:49321")    #Suppose is opc.tcp://192.168.0.253:49321", Alvin temporary change it to prevent interrupt the original system.

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
        #client.connect()
        #print('Connection to OPC Server successful!')
        t1=threading.Thread(target=readTags,daemon=True)
        t1.start()
    except KeyboardInterrupt:
        client.close_session()
        print("Interrupted by user")
    except Exception as e:
        print(e)
    

 

def checkProcQty(station):
    procqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.ProcessedQty".format(station)
    reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.RequiredQty".format(station)
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)

    procqty=procqtystate.get_value()
    reqqty=reqqtystate.get_value()

    return True if procqty==reqqty else False


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
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(stn)
    wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(stn)
    
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    wocmpstate=client.get_node(wocmppath)
    wostatusstate=client.get_node(wostatuspath)
    
    #If work order status is empty
    if wocmpstate.get_value()==0:
        pass
    
    if procqtystate.get_value()==reqqtystate.get_value() :
        wocmpstate.set_value(ua.DataValue(ua.Variant('CMPORD',ua.VariantType.String)))
        wostatusstate.set_value(ua.DataValue(ua.Variant(4,ua.VariantType.UInt16)))
        return True
    else:
        return False

def checkStnAvail(stn):
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(stn)
    wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(stn)
    sstatuspath="ns=2;s=Syngenta.SmartLab.FNP.Info.Station{}.StationState".format(stn)
    
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    wocmpstate=client.get_node(wocmppath)
    wostatusstate=client.get_node(wostatuspath)
    sstatuspath=client.get_node(sstatuspath)
    ss=sstatuspath.get_value()
    #Return station state so scheduler knows the current status of he work order
    if(ss==1):
        return 1
    elif(ss==2):
        return 2
    else:
        return 0
def sendWO2PLC(stn,wo):
    
    uint16_wonum = [c.to_bytes(2, byteorder='big') for c in map(ord, wo[2])]  
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(stn)
    wostatuspath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderStatus".format(stn)
    wostartackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(i)
    
    
    
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    wonumstate=client.get_node(wonumpath)
    wostatusstate=client.get_node(wostatuspath)
    wostartackstate=client.get_node(wostartackpath)
    
    wostartackstate.set_value(ua.DataValue(ua.Variant('RDYORD',ua.VariantType.String)))
    reqqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    wonumstate.set_value(ua.DataValue(ua.Variant(wo,ua.VariantType.String)))
    wostatusstate.set_value(ua.DataValue(ua.Variant(2,ua.VariantType.UInt16)))
    
    
    print('<PI>Sending {} to PLC and wait for MES acknowledgement'.format(wo[2]))
    
def setWOStart(stn):
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    procqtystate=client.get_node(procqtypath)
    procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    
        
def startWO(stn,wo):
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    reqqtystate=client.get_node(reqqtypath)
    reqqtystate.set_value(ua.DataValue(ua.Variant(wo[6],ua.VariantType.UInt16)))
  
def checkCMPAck(station):      
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(station)
    wocncpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CancelledAck".format(station)
    wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)

    woackstate=client.get_node(woackpath)
    wonumstate=client.get_node(wonumpath)
    wocmpstate=client.get_node(wocmppath)
    wocncstate=client.get_node(wocncpath)

    currwo=wonumstate.get_value()
    startack=woackstate.get_value()
    wocmp=wocmpstate.get_value()

    
    
    if wocmp==currwo:
        print('Work Order acknowledgement matched')
        woackstate.set_value(ua.DataValue(ua.Variant('',ua.VariantType.String)))

       
        return True
    else:
        return False    
def checkStartAck(station):      
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(station)
    wocncpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CancelledAck".format(station)
    wonumpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.WorkOrderNumber".format(station)

    woackstate=client.get_node(woackpath)
    wonumstate=client.get_node(wonumpath)
    wocmpstate=client.get_node(wocmppath)
    wocncstate=client.get_node(wocncpath)

    currwo=wonumstate.get_value()
    startack=woackstate.get_value()
    wocmp=wocmpstate.get_value()

    
    
    if startack==currwo:
        print('Work Order acknowledgement matched')
        woackstate.set_value(ua.DataValue(ua.Variant('',ua.VariantType.String)))

       
        return True
    else:
        return False
    
#Check station is empty
def checkEmpty(stn):
      
    if not readPLC('he',stn) and not readPLC('te',stn):
        return True
    else:
        return False

def readTags():
    client.connect()
    while True:
        try:
            time.sleep(0.1)
            
            #print('Connection to OPC Server successful!')
            
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
                if production:
                    print('<PLC> Call WMS interface to request empty bottle')
                    wmsinterface.reqEb()
                
                #Generate robot path and insert as a robot task
                pathinfo=pathcalculate.generate_path('WH','Stn1','')
                dbinterface.insertRbtTask(pathinfo,1,4)
                reqbotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

            #Procedure to return tote box
            if(rettot):
                
                #Call WMS to store tote box
                if production:
                    wmsinterface.reqstb()
                pathinfo=pathcalculate.generate_path('Stn1','WH','')
                dbinterface.insertRbtTask(pathinfo,1,4)
                rettotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

            if(cp2):
                if production:
                    wmsinterface.reqsfc()
                dbinterface.insertRbtTask('Station6;Warehouse')
                cp2state.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

            if(cc):
                print('carton complete')
                #os.environ['waitcomplete'] = 'True'
                
            
            #Fetch empty tote box from WH and go to Stn 6
            if(rtb):
                #Call WMS to retrieve empty tote
                if production:
                    wmsinterface.reqetb()
                
                #Generate robot path and insert as a robot task
                pathinfo=pathcalculate.generate_path('WH','Stn6','')
                #Insert robot task to fetch empty tote
                dbinterface.insertRbtTask(pathinfo,6,3)
                #Write second task to move back to Warehouse after complete
                dbinterface.insertRbtTask('WH',2,2)
                rtbstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
                
            if(stb):
                
                os.environ['waitcomplete'] = 'True'
                 
                #Call WMS to receive item
                if production:
                    wmsinterface.reqsfc("123456")
                stbstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            #client.disconnect()
        except KeyboardInterrupt:
            print("Interrupted by user")
        except Exception as e:
            continue
        



  