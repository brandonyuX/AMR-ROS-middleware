#Interface for WMS
import sys,yaml,os
sys.path.append('../Middleware Development')


import requests

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
        res = requests.post('http://'+wmsip+'/syngenta/mc/production/requestetb',timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WMS Connection timeout!')

#Check if WMS is available for operation

def reqwmsrdy():
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/wms/status',timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WMS Connection timeout!')

#Inform WMS to start the custom operation. WMS subsequently create the tasks required for the custom operation. E.g. Retrieve multiple Tote Box

def customop(reqid):
    dictToSend = {'WMS Request ID':reqid}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/wms/startcustomop',json=dictToSend,timeout=5)
        print ('<WMS> response from server:'+res.text)
        if(res.status_code==401):
            print('<WMS> WMS unable to generate task')
            os.environ['CUSTORDERSTATUS']='ERROR'
        elif res.status_code==200:
            os.environ['CUSTORDERSTATUS']='OK'
            print('<WMS>Task response from MES:'+res.text)
    except:
        print('WNS Connection timeout')
#AMR to retrieve tote box with WMS task ID

def reqrtb():
    dictToSend = {'WMS Request ID':'12345'}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/amr/custom/retrievetb',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WNS Connection timeout')

#AMR to store tote box with WMS task ID

def reqstbwid():
    dictToSend = {'WMS Request ID':'12345'}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/amr/custom/storetb',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WNS Connection timeout')

#AMR to retrieve custom carton with WMS task ID

def reqrcc():
    dictToSend = {'WMS Request ID':'12345'}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/amr/custom/retrievecarton',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WNS Connection timeout')

#AMR to store filled carton to WMS

def reqsfc(batchid):
    dictToSend = {"BatchID":batchid,"ItemType":"Y01"}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/production/storefc',json=dictToSend,timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except:
        print('WNS Connection timeout')
        
#Inform WMS ready for manual task
def informManualTask(tid):
    
    dictToSend = {"WMS Task ID":tid}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/wms/manualtask',json=dictToSend,timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except:
        print('WNS Connection timeout')  
        
#Signal WMS bin is at tail sensor of warehouse
def signalBinAtWH(tid):
    
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/wms/binatstation',timeout=5)
        print('reponse code from server: {}'.format(res.status_code))
        print ('response from server:'+res.text)
    except:
        print('WNS Connection timeout')  