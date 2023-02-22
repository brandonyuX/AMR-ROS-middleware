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
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)

#Send empty tote box from unscrambling station to warehouse

def reqstb():
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/storeetb',timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)


#Send empty tote box from warehouse to case packing station

def reqetb():
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/requestetb',timeout=5)
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)

#Check if WMS is available for operation

def reqwmsrdy():
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/status',timeout=5)
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)

#Inform WMS to start the custom operation. WMS subsequently create the tasks required for the custom operation. E.g. Retrieve multiple Tote Box

def customop(reqid):
    reqid=(str(reqid).strip())
    dictToSend = {'WMSRequestID':reqid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/startcustomop',json=dictToSend,timeout=5)
        print ('<WMS> response from server:'+res.text)
        if(res.status_code==401):
            print('<WMS> WMS unable to generate task')
            os.environ['CUSTORDERSTATUS']='ERROR'
        elif res.status_code==200:
            os.environ['CUSTORDERSTATUS']='OK'
            print('<WMS>Task response from MES:'+res.text)
            data = json.loads(res.text)
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
                        dbinterface.insertCustomTask('{};WH'.format(dest),8,reqid,tskid,action)
                        pass
                    case 'Custom':
                        print('<SVR> Write custom action to db')
                        dbinterface.insertCustomTask(dest,9,reqid,tskid,action)
                        pass
                    case 'Manual':
                        print('<SVR> Write manual task to db')
                        pass
                
                
                
                
            
    except Exception as e:
        print(e)
#AMR to retrieve tote box with WMS task ID

def reqrtb(wmsid):
    wmsid=(str(wmsid).strip())
    dictToSend = {'WMSTaskID':wmsid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/amr/custom/retrievetb',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)

#AMR to store tote box with WMS task ID

def reqstbwid(wmsid):
    wmsid=(str(wmsid).strip())
    print('<WMS> WMS Task ID: {}'.format(wmsid))
    dictToSend = {'WMSTaskID':wmsid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/amr/custom/storetb',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)

#AMR to retrieve custom carton with WMS task ID

def reqrcc():
    dictToSend = {'WMSTaskID':'12345'}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/amr/custom/retrievecarton',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)

#AMR to store filled carton to WMS

def reqsfc(batchid):
    dictToSend = {"BatchID":batchid,"ItemType":"Y01"}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/production/storefc',json=dictToSend,timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)
        
#Inform WMS ready for manual task
def informManualTask(tid):
    
    dictToSend = {"WMS Task ID":tid}
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/manualtask',json=dictToSend,timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except Exception as e:
        print(e) 
        
#Signal WMS bin is at tail sensor of warehouse
def signalBinAtWH():
    
    try:
        res = requests.post('http://'+wmsip+':3000/syngenta/mc/wms/binatstation',timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except Exception as e:
        print(e)