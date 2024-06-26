#Interface for WMS
import sys,yaml,os,json
sys.path.append('../Middleware Development')


import requests
import interface.dbinterface as dbinterface

with open('server-config.yaml', 'r') as f:
    doc = yaml.safe_load(f)

wmsip=doc['SERVER']['WMSIP']

#Request empty bottle from WMS

def reqEb():
    try:
        print('<WI>Request bottle from WMS')
        #res = requests.post('http://'+wmsip+'/syngenta/mc/production/requesteb',timeout=5)
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/requesteb',timeout=5)
        data = json.loads(res.text)
        # os.environ['tempBID']=data['WMSTaskID']
        print('reponse code from server: {}'.format(res.status_code))

        print ('response from server:'+res.text)
    except Exception as e:
        print(str(e))

#Send empty tote box from unscrambling station to warehouse

def reqstb():
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/storeetb',timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except Exception as e:
        print(str(e))


#Send empty tote box from warehouse to case packing station

def reqetb():
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/requestetb',timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))

#Check if WMS is available for operation

def chkwmsrdy():
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/status',timeout=5)
        #print('<WMS>reponse code from server: {}'.format(res.status_code))
        #print ('<WMS>response from server:'+res.text)
        if res.text=='Ready':
            return True
        else:
            return False
    except Exception as e:
        print(str(e))

#Inform WMS to start the custom operation. WMS subsequently create the tasks required for the custom operation. E.g. Retrieve multiple Tote Box

def customop(reqid):
    reqid=(str(reqid).strip())
    dictToSend = {'WMSRequestID':reqid}
    print('<WMS> Send custom operation with request id {}'.format(reqid))
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/startcustomop',json=dictToSend,timeout=5)
        print ('<WMS> response from server:'+res.text)
        if(res.status_code==401):
            print('<WMS> WMS unable to generate task')
            os.environ['CUSTORDERSTATUS']='ERROR'
        elif res.status_code==200:
            
            print('<WMS>Task response from MES:'+res.text)
            data = json.loads(res.text)
            if len(data)>1:
                os.environ['CUSTORDERSTATUS']='OK'
            else:
                os.environ['CUSTORDERSTATUS']='NO DATA'

            for item in data:
                print("WMSRequestID:", item["WMSRequestID"])
                print("WMSTaskID:", item["WMSTaskID"])
                print("Action:", item["Action"])
                print("Destination:", item["Destination"])
                
                action=item["Action"]
                dest=item["Destination"]
                tskid=item["WMSTaskID"]
                reqid=item["WMSRequestID"]
                
                match action:
                    case 'Retrieve':
                        print('<SVR> Write retrieval action to custom task table')
                        dbinterface.insertCustomTask('WH;{}'.format(dest),7,reqid,tskid,action)
                        pass
                    case 'Store':
                        print('<SVR> Write store action to custom task table')
                        dbinterface.insertCustomTask('{};WH;CHR'.format(dest),8,reqid,tskid,action)
                        pass
                    case 'Custom':
                        print('<SVR> Write custom action to db')
                        
                        dbinterface.insertCustomTask(dest,9,reqid,tskid,action)
                        
                        pass
                    case 'Manual':
                        print('<SVR> Received manual task')
                        print('<WMS> Detected manual entry, reflect to WMS ready')
                        os.environ['manualtask']='True'
                        informManualTask(item["WMSTaskID"])
                        pass
                
                
                
                
            
    except Exception as e:
        print(str(e))
        


#AMR to retrieve tote box with WMS task ID

def reqrtb(wmsid):
    wmsid=(str(wmsid).strip())
    dictToSend = {'WMSTaskID':wmsid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/amr/custom/retrievetb',json=dictToSend,timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))

#AMR to store tote box with WMS task ID

def reqstbwid(wmsid):
    wmsid=(str(wmsid).strip())
    print('<WMS> WMS Task ID: {}'.format(wmsid))
    dictToSend = {'WMSTaskID':wmsid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/amr/custom/storetb',json=dictToSend,timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))

#AMR to retrieve custom carton with WMS task ID

def reqrcc():
    dictToSend = {'WMSTaskID':'12345'}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/amr/custom/retrievecarton',json=dictToSend,timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))

#AMR to store filled carton to WMS
os.environ['currentBatch']='Null'
def reqsfc(batchid):
    print(batchid)
    # print(os.environ['currentBatch'])
    dictToSend = {"BatchID":batchid,"ItemType":os.environ['currentBatch']}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/storefc',json=dictToSend,timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))
        
#Inform WMS ready for manual task
def informManualTask(tid):
    
    dictToSend = {"WMSTaskID":tid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/manualtask',json=dictToSend,timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e)) 
        
#Signal WMS bin is at tail sensor of warehouse
def signalBinAtWH():
    print('<WMS> Bin at station')
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/binatstation',timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))
        

#Signal WMS bin to sending into the station
def signalBinToWH():
    print('<WMS> Sending bin into station')
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/binentering',timeout=5)
        print('<WMS>reponse code from server: {}'.format(res.status_code))
        print ('<WMS>response from server:'+res.text)
    except Exception as e:
        print(str(e))