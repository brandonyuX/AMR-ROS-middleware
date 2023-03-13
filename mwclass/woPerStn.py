import json
import pyodbc
import datetime

class WOPerStn:
    def __init__(self, woid=None, batchNum=None, woNum=None, manufactureDate=None, fnpDate=None, initSerialNum=None, requireQty=None, processedQty=None, startTime=None, endTime=None, status=None, fillVol=None, targetTor=None, orderNum=None, expDate=None) -> None:
        self.woid=woid
        self.batchNum=batchNum
        self.woNum=woNum
        self.manufactureDate=manufactureDate
        self.fnpDate=fnpDate
        self.initSerialNum=initSerialNum
        self.requireQty=requireQty
        self.processedQty=processedQty
        self.startTime=startTime.strftime("%Y-%m-%d %H:%M:%S")
        self.endTime=endTime.strftime("%Y-%m-%d %H:%M:%S")
        self.status=status
        self.fillVol=fillVol
        self.targetTor=targetTor
        self.orderNum=orderNum
        self.expDate = expDate

    def __str__(self) -> str:
        text="{} {} {} {} {} {}".format(self.woid,self.batchNum,self.woNum,self.manufactureDate,self.fnpDate,self.initSerialNum)
        return text
        
    # def to_dict(self):
    #     self_dict = self.__dict__
    #     self_dict['completed'] = 'Completed Task' if self_dict['completed'] else 'Active Task'
    #     return self_dict
    