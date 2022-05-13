#Main class for task 

class Task:
    def __init__(self,tid,rid,reqid,comp,taskcode,currstep,endstep,destloc,hsmsg,lastupd,exec,tskmodno,processing) -> None:
        self.tid=tid
        self.rid=rid
        self.reqid=reqid
        self.comp=comp
        self.taskcode=taskcode
        self.currstep = currstep
        self.destloc=destloc
        self.endstep=endstep
        self.hsmsg=hsmsg
        self.lastupd=lastupd
        self.exec=exec
        self.tskmodno=tskmodno
        self.processing=processing

    def __str__(self) -> str:
        text="{} {} {} {} {} {} {} {} {}".format(self.tid,self.rid,self.reqid,self.comp,self.taskcode,self.currstep,self.endstep,self.startloc,self.endloc)
        return text
        