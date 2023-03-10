import json
import pyodbc
import datetime

class CustomRequest:
    def __init__(self, cid=None, reqid=None, dest=None, priority=None, status=None, datetime=None) -> None:
        self.cid=cid                
        self.reqid=reqid         
        self.dest=dest           
        self.priority=priority    
        self.status=status       
        self.datetime = datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        text="{} {} {} {} {} {}".format(self.cid,self.reqid,self.dest,self.priority,self.status,self.datetime)
        return text
        
    # def to_dict(self):
    #     self_dict = self.__dict__
    #     self_dict['completed'] = 'Completed Task' if self_dict['completed'] else 'Active Task'
    #     return self_dict
    