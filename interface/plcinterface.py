#This file provides interface with the PLC and update the database
#Will use opcua in this example
import socket,datetime,sys,signal,math
import time,os
import threading,yaml,random


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
wmsprod=doc['ROBOT']['WMSPROD']
#List of rejects
rejlist=[]

currrejqty=-1

os.environ['reqeb'] ='False'
os.environ['currbatchid']='Null'

decdata=''
try:
    client = Client("opc.tcp://192.168.0.187:49320",timeout=5)
except KeyboardInterrupt:
    print("Interrupted by user")
            
# client = Client("opc.tcp://192.168.0.250:49321")    #Suppose is opc.tcp://192.168.0.253:49321", Alvin temporary change it to prevent interrupt the original system.

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

def startupdemo():
    client.connect()
    print('Connection Successful')
def startup():
    try:
        # client.connect()
        t1=threading.Thread(target=readTags,daemon=True)
        t1.start()
    except KeyboardInterrupt:
        client.close_session()
        print("Interrupted by user")
    except Exception as e:
        print(e)
    

def incProcQty(station):
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(station)
    rejqtypath="ns=2;s=SyngentaPLC.Station5.RejectedQty".format(station)
    procqtystate=client.get_node(procqtypath)
    procqty=procqtystate.get_value()
    
    rejqtystate=client.get_node(rejqtypath)
    rejqty=rejqtystate.get_value()
    #Increase processed quantity by 1
    procqtystate.set_value(ua.DataValue(ua.Variant(procqty+1,ua.VariantType.UInt16)))
    print(f'Increased station {station} processed quantity to {procqty+1}.')
    #Station is inspection
    # if(station==5):
    #     reject = random.choices([True, False], [0.6,0.4])
    #     if(reject[0]):
    #         rejqtystate.set_value(ua.DataValue(ua.Variant(rejqty+1,ua.VariantType.UInt16)))


def checkProcQty(station):
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(station)
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(station)
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)

    procqty=procqtystate.get_value()
    reqqty=reqqtystate.get_value()

    return True if procqty==reqqty else False

def forceComplete(station):
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(station)
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(station)

    reqqtystate=client.get_node(reqqtypath)
    procqtystate=client.get_node(procqtypath)
    procqtystate.set_value(ua.DataValue(ua.Variant(reqqtystate.get_value(),ua.VariantType.UInt16)))



def writeWODetails(station,wonum,wostatus,reqqty,procqty):
    
    if station==0:
        for i in range(1,7):
            wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(i)
            wostatuspath="ns=2;s=SyngentaPLC.Station{}.WorkOrderStatus".format(i)
            reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(i)
            procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(i)

            wonumstate=client.get_node(wonumpath)
            wostatusstate=client.get_node(wostatuspath)
            reqqtystate=client.get_node(reqqtypath)
            procqtystate=client.get_node(procqtypath)

            wonumstate.set_value(ua.DataValue(ua.Variant(wonum,ua.VariantType.String)))
            wostatusstate.set_value(ua.DataValue(ua.Variant(wostatus,ua.VariantType.UInt16)))
            reqqtystate.set_value(ua.DataValue(ua.Variant(reqqty,ua.VariantType.UInt16)))
            procqtystate.set_value(ua.DataValue(ua.Variant(procqty,ua.VariantType.UInt16)))
    else:
        wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(station)
        wostatuspath="ns=2;s=SyngentaPLC.Station{}.WorkOrderStatus".format(station)
        reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(station)
        procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(station)

        wonumstate=client.get_node(wonumpath)
        wostatusstate=client.get_node(wostatuspath)
        reqqtystate=client.get_node(reqqtypath)
        procqtystate=client.get_node(procqtypath)

        wonumstate.set_value(ua.DataValue(ua.Variant(wonum,ua.VariantType.String)))
        wostatusstate.set_value(ua.DataValue(ua.Variant(wostatus,ua.VariantType.UInt16)))
        reqqtystate.set_value(ua.DataValue(ua.Variant(reqqty,ua.VariantType.UInt16)))
        procqtystate.set_value(ua.DataValue(ua.Variant(procqty,ua.VariantType.UInt16)))
 


def startWOACK(station):
    woackpath="ns=2;s=SyngentaPLC.Station{}.StartAck".format(station)

    woackstate=client.get_node(woackpath)
    woackstate.set_value(ua.DataValue(ua.Variant('RDYORD',ua.VariantType.String)))
 
def getWOACK(station):      
    woackpath="ns=2;s=SyngentaPLC.Station{}.StartAck".format(station)

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
    wopath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(station)
    wostate=client.get_node(wopath)

    currwo=wostate.get_value()
    woindex=queue.index(currwo)
   
    if(woindex>=len(queue)-1):
        return 'end'
    else:
        return queue[woindex+1]

def writePLC(type,value,loc):
    try:
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
    except:
        print('<PLC> Write exception')
        pass

#Read plc tag
def readPLC(type,loc):
    try:
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
    except:
        print('<PLC> Read exception')
def divmod(a, b):
    quotient = a // b
    remainder = a % b
    return quotient, remainder
os.environ['prevrej']= str(0)
def checkStnDone(stn,check,bcode=None,wonum=None):
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(stn)
    wostatuspath="ns=2;s=SyngentaPLC.Station{}.WorkOrderStatus".format(stn)
    
    
    
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    wocmpstate=client.get_node(wocmppath)
    wostatusstate=client.get_node(wostatuspath)

    

    procqty=procqtystate.get_value()
    #Monitor rejected quantity
    if stn==5 and bcode!=None:
        rejqtypath="ns=2;s=SyngentaPLC.Station5.RejectedQty"
        stn6reqqty='ns=2;s=SyngentaPLC.Station6.RequiredQty'
        rejstate=client.get_node(rejqtypath)
        currrej=rejstate.get_value()

        stn6reqstate=client.get_node(stn6reqqty)
        
        reqqty=stn6reqstate.get_value()
        prevrej=int(os.environ['prevrej'])
        if currrej!=prevrej:
            #Overwrite previous reject quantity to prevent loop
            os.environ['prevrej']=str(currrej)
            #Get bottles to reject and which WO to cancel
            wocancel,qtycancel=divmod(currrej,reqqty)
            newqty=reqqty-qtycancel
            wo2cancelfromlast=math.floor(wocancel)
            #If WO is last on station 6, if last WO set the current quantity, else write the last WO in DB
            if dbinterface.checkWOLast(stn=6,batchnum=bcode):
                #If last WO, check how many bottles were rejected previously
                currreqqty=stn6reqstate.get_value()
                prevrejbtl=int(os.environ['reqqty'])-currreqqty
                #Do not count previously rejected bottles and add previously rejected bottles back to newqty
                newqty=newqty+prevrejbtl
                stn6reqstate.set_value(ua.DataValue(ua.Variant(newqty,ua.VariantType.UInt16)))
            else:
                dbinterface.writeStn6Qty(newqty,bcode,wo2cancelfromlast)

    #Handle bottle torque out of range   
    if stn==3 and wonum!=None:
        tofrpath="ns=2;s=SyngentaPLC.Station3.TorqueOutOfRange"
        
        tofrstate=client.get_node(tofrpath)
        tofr=tofrstate.get_value()
        
        if tofr:
            tofrstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            #Need to confirm when the processed quantity is increased
            time.sleep(0.1)
            rejdict={"WO":wonum,"index":procqty}
            rejlist.append(rejdict)

            
            
    #Check the list of rejects and reject the bottles marked from station 3
    if stn==5 and bcode !=None:
        rejwo=[item['index'] for item in rejlist if item['WO']==wonum]
        for rej in rejwo:
            print(rej)
        
        #Check if procqty for the given wo is in the rejected list and if reject next bottle is previously set
        if procqty+1 in rejwo and currrejqty!=procqty:
            rnbpath="ns=2;s=SyngentaPLC.Station5.RejectNextBottle"
            rnbstate=client.get_node(rnbpath)
            rnbstate.set_value(ua.DataValue(ua.Variant(True,ua.VariantType.Boolean)))
            currrejqty=procqty
        pass




    
    #If work order status is empty
    if wocmpstate.get_value()==0:
        pass
    
    #When station done criteria is met
    if procqty==reqqtystate.get_value() or checkBypassMode(stn)==1 :
        if(check):
            #Reset station 5 current reject qty
            if stn==5:
                currrejqty=-1
                #Detect if both is 0
            if(reqqtystate.get_value()==0):
                return 2
            else:
                return 1
    
        else:
            #Reset station 5 current reject qty
            if stn==5:
                currrejqty=-1
            
            
            wocmpstate.set_value(ua.DataValue(ua.Variant('CMPORD',ua.VariantType.String)))
            wostatusstate.set_value(ua.DataValue(ua.Variant(4,ua.VariantType.UInt16)))
            return 1
    else:
        #Check for tote if not completed

        if stn==1:
            #reqeb()
            #Interlock call by setting flag
            #os.environ['reqeb-call']='True'
            pass
        return 0

def setWoStatus(stn,state):
    wostatuspath="ns=2;s=SyngentaPLC.Station{}.WorkOrderStatus".format(stn)
    wostatusstate=client.get_node(wostatuspath)
    wostatusstate.set_value(ua.DataValue(ua.Variant(state,ua.VariantType.UInt16)))

def setLastWO(state):
    wostatuspath="ns=2;s=SyngentaPLC.Station6.LastWorkOrder"
    wostatusstate=client.get_node(wostatuspath)
    if state:
        wostatusstate.set_value(ua.DataValue(ua.Variant(1,ua.VariantType.UInt16)))
    else:
        wostatusstate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))

def checkBypassMode(stn):
    bppath="ns=2;s=SyngentaPLC.Station{}.BypassMode".format(stn)
    bpstate=client.get_node(bppath)
    bp=bpstate.get_value()

    return bp
def checkStnStatus(stn):
    try:
        reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
        procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
        wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(stn)
        wostatuspath="ns=2;s=SyngentaPLC.Station{}.WorkOrderStatus".format(stn)
        sstatuspath="ns=2;s=SyngentaPLC.Station{}.StationState".format(stn)
        # print(sstatuspath)
        procqtystate=client.get_node(procqtypath)
        reqqtystate=client.get_node(reqqtypath)
        wocmpstate=client.get_node(wocmppath)
        wostatusstate=client.get_node(wostatuspath)
        sstatusstate=client.get_node(sstatuspath)
        ss=sstatusstate.get_value()
        ws=wostatusstate.get_value()
        #Return station state so scheduler knows the current status of he work order
        return ss,ws
    except Exception as e:
        # print(f'Exception on plc tag reader (Check Stn)')
            
        # print('<PLC> Exception found in opc tag reader.')
        return 0,4
        
        #Tries to connect to opc server after 10 seconds
        # client.disconnect()
        # time.sleep(10)
        # client.connect()
    # print(ss)
    
def sendWO2PLC(stn,wo):
    
    # uint16_wonum = [c.to_bytes(2, byteorder='big') for c in map(ord, wo[2])]  
    procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(stn)
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(stn)
    bcodepath="ns=2;s=SyngentaPLC.Station{}.BatchCode".format(stn)
    wostatuspath="ns=2;s=SyngentaPLC.Station{}.WorkOrderStatus".format(stn)
    wostartackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(stn)
    #Init reject qty to 0 for new wo
    # rejqtypath="ns=2;s=SyngentaPLC.Station5.RejectedQty"
    # rejqtystate=client.get_node(rejqtypath)
    # rejqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    
    
    
    procqtystate=client.get_node(procqtypath)
    reqqtystate=client.get_node(reqqtypath)
    wonumstate=client.get_node(wonumpath)
    wostatusstate=client.get_node(wostatuspath)
    wostartackstate=client.get_node(wostartackpath)
    bcodestate=client.get_node(bcodepath)

    wonumstate.set_value(ua.DataValue(ua.Variant(wo[2],ua.VariantType.String)))
    bcodestate.set_value(ua.DataValue(ua.Variant(wo[1],ua.VariantType.String)))
    reqqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
    #Write fill volume
    if(stn==2):
        fvpath="ns=2;s=SyngentaPLC.Station2.FillVolume"
        fvstate=client.get_node(fvpath)
        finalvol=0
        if(wo[11]==100):
            finalvol=1
        else:
            finalvol=2
        fvstate.set_value(ua.DataValue(ua.Variant(finalvol,ua.VariantType.UInt16)))
    #Write target torque
    if(stn==3):
        ttpath="ns=2;s=SyngentaPLC.Station3.TargetTorque"
        ttstate=client.get_node(ttpath)
        ttstate.set_value(ua.DataValue(ua.Variant(float(wo[12]),ua.VariantType.Float)))

    #Set label information for station 4
    if(stn==4):
        pdpath="ns=2;s=SyngentaPLC.Station4.ProductionDate"
        edpath="ns=2;s=SyngentaPLC.Station4.ExpirationDate"

        pdstate=client.get_node(pdpath)
        edstate=client.get_node(edpath)

        pdstate.set_value(ua.DataValue(ua.Variant(wo[3],ua.VariantType.String)))
        edstate.set_value(ua.DataValue(ua.Variant(wo[13],ua.VariantType.String)))


    time.sleep(1)
    wostatusstate.set_value(ua.DataValue(ua.Variant(2,ua.VariantType.UInt16)))
    wostartackstate.set_value(ua.DataValue(ua.Variant('RDYORD',ua.VariantType.String)))
    
    
    
    print('<PI>Sending {} to PLC and wait for MES acknowledgement'.format(wo[2]))
    
def setWOStart():
    for i in range(1,7):
        procqtypath="ns=2;s=SyngentaPLC.Station{}.ProcessedQty".format(i)
        procqtystate=client.get_node(procqtypath)
        procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))


     
def startWO(stn,wo):
    reqqtypath="ns=2;s=SyngentaPLC.Station{}.RequiredQty".format(stn)
    reqqtystate=client.get_node(reqqtypath)
    #Change back to variable
    reqqtystate.set_value(ua.DataValue(ua.Variant(wo[6],ua.VariantType.UInt16)))
    #If station 1 did not detect any tote box, request for empty bottle
    if(stn==1):
        reqeb()
    

    # if(checkStnStatus(stn))==3 or (checkStnStatus(stn))==1:
    #Set all station to start
    setStnState(stn,'Start')

#Start station command
def setStnState(stn,state):
    statepath='ns=2;s=SyngentaPLC.Station{}.Cmd{}'.format(stn,state)
    statestate=client.get_node(statepath)
    statestate.set_value(ua.DataValue(ua.Variant(True,ua.VariantType.Boolean)))

def setNewBatch():
    for i in range(1,6):
        reqqtypath="ns=2;s=SyngentaPLC.Station{}.NewBatch".format(i)
        reqqtystate=client.get_node(reqqtypath)
        reqqtystate.set_value(ua.DataValue(ua.Variant(True,ua.VariantType.Boolean)))

#Write AMR Information to tag
def writeAMRBatt(battlvl):
    battpath='ns=2;s=Syngenta.SmartLab.FNP.AMR.BatteryLevel'
    battstate=client.get_node(battpath)
    battstate.set_value(ua.DataValue(ua.Variant(battlvl,ua.VariantType.UInt16)))

#Write AMR Location to tag
def writeAMRLocation(location):
    locpath='ns=2;s=Syngenta.SmartLab.FNP.AMR.CurrentDestination'
    locstate=client.get_node(locpath)
    locstate.set_value(ua.DataValue(ua.Variant(location,ua.VariantType.String)))
#Write AMR absolute location
def writeAMRABSLocation(x,y):
    xpath='ns=2;s=Syngenta.SmartLab.FNP.AMR.LocationX'
    ypath='ns=2;s=Syngenta.SmartLab.FNP.AMR.LocationY'
    xstate=client.get_node(xpath)
    ystate=client.get_node(ypath)

    xstate.set_value(ua.DataValue(ua.Variant(x,ua.VariantType.Float)))
    ystate.set_value(ua.DataValue(ua.Variant(y,ua.VariantType.Float)))
#Write AMR Charging tag

def writeAMRCharging(charging):
    reqqtypath="ns=2;s=Syngenta.SmartLab.FNP.AMR.Charging"
    reqqtystate=client.get_node(reqqtypath)
    reqqtystate.set_value(ua.DataValue(ua.Variant(charging,ua.VariantType.Boolean)))


def informDocked(dock,stn):
    try:
        if stn==6:
            reqqtypath="ns=2;s=SyngentaPLC.Station6.AMRDocked"
            reqqtystate=client.get_node(reqqtypath)
            reqqtystate.set_value(ua.DataValue(ua.Variant(dock,ua.VariantType.Boolean)))
        elif stn==1:
            reqqtypath="ns=2;s=SyngentaPLC.Station1.AMRDocking"
            reqqtystate=client.get_node(reqqtypath)
            reqqtystate.set_value(ua.DataValue(ua.Variant(dock,ua.VariantType.UInt16)))
    except:
        print('<PLC> Exception found in opc tag reader (Dock)')
        # time.sleep(10)
        # client.connect()

def checkCMPAck(station):      
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(station)
    wocncpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CancelledAck".format(station)
    wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(station)

    woackstate=client.get_node(woackpath)
    wonumstate=client.get_node(wonumpath)
    wocmpstate=client.get_node(wocmppath)
    wocncstate=client.get_node(wocncpath)

    currwo=wonumstate.get_value()
    startack=woackstate.get_value()
    wocmp=wocmpstate.get_value()

    
    
    if wocmp==currwo:
        print(f'Completed acknowledgement matched for station{station}, {currwo}')
        wocmpstate.set_value(ua.DataValue(ua.Variant('',ua.VariantType.String)))

       
        return True
    else:
        return False    
def checkStartAck(station):      
    woackpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.StartAck".format(station)
    wocmppath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CompleteAck".format(station)
    wocncpath="ns=2;s=Syngenta.SmartLab.FNP.WO.Station{}.CancelledAck".format(station)
    wonumpath="ns=2;s=SyngentaPLC.Station{}.WorkOrderNumber".format(station)

    woackstate=client.get_node(woackpath)
    wonumstate=client.get_node(wonumpath)
    wocmpstate=client.get_node(wocmppath)
    wocncstate=client.get_node(wocncpath)

    currwo=wonumstate.get_value()
    startack=woackstate.get_value()
    wocmp=wocmpstate.get_value()

    
    
    if startack==currwo:
        print('Start Work Order acknowledgement matched')
        woackstate.set_value(ua.DataValue(ua.Variant('',ua.VariantType.String)))

       
        return True
    else:
        return False
    
#Initialize tag for new batch
def initTag():
    #Add wasted qty by 2 to current tag
    wastedqtypath="ns=2;s=Syngenta.SmartLab.FNP.BO.TotalWastedQty"
    wastedqtystate=client.get_node(wastedqtypath)
    currwastedqty=wastedqtystate.get_value()
    wastedqtystate.set_value(ua.DataValue(ua.Variant(currwastedqty+2,ua.VariantType.UInt16)))
    #Init reject qty to 0 for new batch
    rejqtypath="ns=2;s=SyngentaPLC.Station5.RejectedQty"
    rejqtystate=client.get_node(rejqtypath)
    rejqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))




    setLastWO(False)
    setNewBatch()

    pass
#Check station is empty
def checkEmpty(stn):
      
    if not readPLC('he',stn) and not readPLC('te',stn):
        return True
    else:
        return False
def reqeb():
    if readPLC("te","Stn1")==0 and os.environ['reqeb'] =='False':
        dbinterface.writeLog(msg='<PLC> Request Empty Bottles')

        #Generate robot path and insert as a robot task
        # pathinfo=pathcalculate.generate_path('WH','Stn1','')
        
        randreqid=random.randrange(100000000,999999999)
        dbinterface.insertRbtTask("WH;Stn1;CHR",1,'REB',randreqid)
        #Set wms ready bit to false
        os.environ['wmsrdy'] = 'False'
        os.environ['reqeb'] = 'True'
        # reqbotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
        return True
    else:
        return False

#Function to return totebox from station 1
def returnEmptyTote():
    #Call WMS to store tote box
    #Set request bottle flag to false when returning empty tote
    #os.environ['reqeb-call']='False'
    
    # pathinfo=pathcalculate.generate_path('Stn1','WH','')
    randreqid=random.randrange(100000000,999999999)
    dbinterface.insertRbtTask('Stn1;WH;CHR',1,'STB',randreqid)
    # rettotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

def readTags():
    client.connect()
    # print('Connection to OPC Server successful!')
    while True:
        try:
            time.sleep(0.2)
            
            #print('Connection to OPC Server successful!')
            
            #Station 1 tote request and store
            reqbotpath="ns=2;s=SyngentaPLC.Station1.AMR.RequestBottle"
            rettotpath="ns=2;s=SyngentaPLC.Station1.AMR.ReturnToteBox"
            
            
            #Station 6 tote retrieval and store
            # rtbpath="ns=2;s=SyngentaPLC.Station6.RetrieveToteBox"
            rtbpath="ns=2;s=SyngentaPLC.Station6.RetrieveToteBox"
            stbpath="ns=2;s=SyngentaPLC.Station6.StoreToteBox"

            #Start/Pause signal from MES
            startpath="ns=2;s=Syngenta.SmartLab.FNP.BO.Start"
            pausepath="ns=2;s=Syngenta.SmartLab.FNP.BO.Paused"
            cancelpath="ns=2;s=Syngenta.SmartLab.FNP.BO.Cancelled"

            #Monitor rejected qty and write into sys var
            rejqtypath="ns=2;s=SyngentaPLC.Station5.RejectedQty"

            #LWO Reset Signal
            lworesetpath="ns=2;s=SyngentaPLC.Station6.LWOReset"
            

            


            reqbotstate=client.get_node(reqbotpath)
            rettotstate=client.get_node(rettotpath)
            rtbstate=client.get_node(rtbpath)
            stbstate=client.get_node(stbpath)

            startstate=client.get_node(startpath)
            pausestate=client.get_node(pausepath)
            cancelstate=client.get_node(cancelpath)

            lworesetstate=client.get_node(lworesetpath)

            reqbot=False
            rettot=False
            rtb=False
            stb=False
            reqbot=reqbotstate.get_value()
            # print("<PLC> read lwreset")
            rettot=rettotstate.get_value()
            rtb=rtbstate.get_value()
            stb=stbstate.get_value()
            lworeset=lworesetstate.get_value()
            # print("<PLC> read lwreset")

            bostart=startstate.get_value()
            bopause=pausestate.get_value()
            bocancel=cancelstate.get_value()

            

            


        
            #Precedure to reset last work order
           
            if(lworeset):
                print("<PLC> Last work order reset detected!")
                wostatuspath="ns=2;s=SyngentaPLC.Station6.LastWorkOrder"
                procqtypath="ns=2;s=SyngentaPLC.Station6.ProcessedQty"
                reqqtypath="ns=2;s=SyngentaPLC.Station6.RequiredQty"
                wostatusstate=client.get_node(wostatuspath)
                procqtystate=client.get_node(procqtypath)
                reqqtystate=client.get_node(reqqtypath)
                wostatusstate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
                procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
                reqqtystate.set_value(ua.DataValue(ua.Variant(12,ua.VariantType.UInt16)))
                time.sleep(1)
                wostatusstate.set_value(ua.DataValue(ua.Variant(1,ua.VariantType.UInt16)))
                lworesetstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            

            
        
            #Procedure to request bottles
            if(reqbot):
                #Call WMS to retrieve bottles bottles
                # if production:
                #     print('<PLC> Call WMS interface to request empty bottle')
                #     wmsinterface.reqEb()
                
                #Generate robot path and insert as a robot task
                pathinfo=pathcalculate.generate_path('WH','Stn1','')
                print('<PLC> Write request empty bottle task')
                reqeb()
                # dbinterface.insertRbtTask("WH;Stn1;TPLeft",1,'REB',randreqid)
                #Set wms ready bit to false
                os.environ['wmsrdy'] = 'False'
                reqbotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

            #Procedure to return tote box
            if(rettot):
                pass
                #Call WMS to store tote box
                #Set request bottle flag to false when returning empty tote
                returnEmptyTote()
                rettotstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

            # if(cp2):
            #     if production:
            #         wmsinterface.reqsfc()
            #     dbinterface.insertRbtTask('Stn6;WH',1)
            #     cp2state.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))

            # if(cc):
            #     print('<PLC>carton complete')
            #     os.environ['waitcomplete'] = 'True'
                
            
            #Fetch empty tote box from WH and go to Stn 6
            if(rtb):
                
                
            
                #Insert robot task to fetch empty tote
                
                print('<PLC> Write stn 6 task')
                if wmsprod:
                    randreqid=random.randrange(100000000,999999999)
                    dbinterface.insertRbtTask('WH;Stn6;WH;CHR',6,'WAITCARTON',randreqid)
                
                rtbstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            
            if(stb):
                
                os.environ['waitcomplete'] = 'True'
                informDocked(dock=False,stn=6)
                
                #Call WMS to receive item
                if production:
                   #Signal WMS to return tote box
                    final_bid=000000
                    rand_batch=random.randrange(100000,999999)
                    if os.environ['currbatchid']=='Null':
                        final_bid=str(rand_batch)
                    else:
                        final_bid=(os.environ['currbatchid'])
                        os.environ['currbatchid']='Null'
                    wmsinterface.reqsfc(final_bid)
                stbstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            #client.disconnect()

            #Start BO from MES
            if(bostart):
                for i in range(1,7):
                    #Skip station 3 from start
                    if i!=3:
                        setStnState(i,'Start')
                        setWoStatus(i,2)
                startstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
                pass

            #Receive pause from MES
            if(bopause):
                for i in range(1,7):
                    #Skip station 3 from pause
                    if i!=3:
                        setStnState(i,'Pause')
                        setWoStatus(i,3)
                pausestate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
                pass

            if(bocancel):
                dbinterface.cancelWO()
                cancelstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
        except Exception as e:
            pass
            # print(f'Exception on plc tag reader for station 1 {e}')

            lworeset=lworesetstate.get_value()
            if(lworeset):
                print("<PLC> Last work order reset detected!")
                wostatuspath="ns=2;s=SyngentaPLC.Station6.LastWorkOrder"
                procqtypath="ns=2;s=SyngentaPLC.Station6.ProcessedQty"
                reqqtypath="ns=2;s=SyngentaPLC.Station6.RequiredQty"
                wostatusstate=client.get_node(wostatuspath)
                procqtystate=client.get_node(procqtypath)
                reqqtystate=client.get_node(reqqtypath)
                wostatusstate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
                procqtystate.set_value(ua.DataValue(ua.Variant(0,ua.VariantType.UInt16)))
                reqqtystate.set_value(ua.DataValue(ua.Variant(12,ua.VariantType.UInt16)))
                time.sleep(1)
                wostatusstate.set_value(ua.DataValue(ua.Variant(1,ua.VariantType.UInt16)))
                lworesetstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            
            bostart=startstate.get_value()
            bopause=pausestate.get_value()
            bocancel=cancelstate.get_value()

            #Start BO from MES
            if(bostart):
                for i in range(1,7):
                    #Skip station 3 from start
                    if i!=3:
                        setStnState(i,'Start')
                        setWoStatus(i,2)
                startstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
                pass

            #Receive pause from MES
            if(bopause):
                for i in range(1,7):
                    #Skip station 3 from pause
                    if i!=3:
                        setStnState(i,'Pause')
                        setWoStatus(i,3)
                pausestate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
                pass

            if(bocancel):
                dbinterface.cancelWO()
                cancelstate.set_value(ua.DataValue(ua.Variant(False,ua.VariantType.Boolean)))
            
            # print('<PLC> Exception found in opc tag reader (readtag)')

            #Tries to connect to opc server after 10 seconds
            # client.disconnect()
            # time.sleep(10)
            # client.connect()
            

       
        



  