#Main class for task 
import json 

class Task:
    def __init__(self,tid,rid,reqid,completed,mcstep,currstep,endstep,destloc,hsmsg,lastupd,exec,tskmodno,processing,datecreated) -> None:
        self.tid=tid                    #task id
        self.rid=rid                    #robot id
        self.reqid=reqid                #request id
        self.completed=completed        #complete status
        self.mcstep=mcstep              #task code
        self.currstep = currstep        #current step
        self.endstep=endstep            #end step
        self.destloc=destloc            #destination location
        self.hsmsg=hsmsg                #hs msg
        self.lastupd=lastupd            #last Upd
        self.exec=exec                  #Executing
        self.tskmodno=tskmodno          #task model ID
        self.processing=processing
        self.datecreated=str(datecreated)
        
    

    def __str__(self) -> str:
        text="{} {} {} {} {} {} {}".format(self.tid,self.rid,self.reqid,self.completed,self.mcstep,self.currstep,self.endstep)
        return text
        
    def to_dict(self):
        self_dict = self.__dict__
        self_dict['completed'] = 'Completed Task' if self_dict['completed'] else 'Active Task'
        return self_dict
    