#Main class for task 
import json 

class Task:
    def __init__(self,tid,rid,reqid,completed,mcstep,currstep,endstep,destloc,hsmsg,lastupd,exec,tskmodno,processing) -> None:
        self.tid=tid
        self.rid=rid
        self.reqid=reqid
        self.completed=completed
        self.mcstep=mcstep
        self.currstep = currstep
        self.destloc=destloc
        self.endstep=endstep
        self.hsmsg=hsmsg
        self.lastupd=lastupd
        self.exec=exec
        self.tskmodno=tskmodno
        self.processing=processing

    def __str__(self) -> str:
        text="{} {} {} {} {} {} {}".format(self.tid,self.rid,self.reqid,self.completed,self.mcstep,self.currstep,self.endstep)
        return text
        
    def to_dict(self):
        self_dict = self.__dict__
        self_dict['completed'] = 'Completed Task' if self_dict['completed'] else 'Active Task'
        return self_dict