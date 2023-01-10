#Interface for WMS
import sys,yaml
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
        res = requests.post('https://63bcd5b8fa38d30d85d2459d.mockapi.io/requesteb',timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WMS Connection timeout!')

#Send empty tote box from unscrambling station to warehouse

def reqstb():
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/production/storeetb',timeout=5)
        print ('response from server:'+res.text)
    except:
        print('WMS Connection timeout!')
    
#Send empty tote box from warehouse to case packing station

def reqsfc():
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

def customop():
    dictToSend = {'WMS Request ID':'12345'}
    try:
        res = requests.post('http://'+wmsip+'/syngenta/mc/wms/startcustomop',json=dictToSend,timeout=5)
        print ('response from server:'+res.text)
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

