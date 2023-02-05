#Main class for task 

class Task:
    def __init__(self,tid,rid,reqid,comp,mcstep,currstep,endstep,destloc,hsmsg,lastupd,exec,tskmodno,processing) -> None:
        self.tid=tid
        self.rid=rid
        self.reqid=reqid
        self.comp=comp
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
        text="{} {} {} {} {} {} {}".format(self.tid,self.rid,self.reqid,self.comp,self.mcstep,self.currstep,self.endstep)
        return text
        