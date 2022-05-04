#Main class for task 

class Task:
    def __init__(self,tid,rid,reqid,comp,taskcode,currstep,endstep,startloc,endloc,hsmsg,exec) -> None:
        self.tid=tid
        self.rid=rid
        self.reqid=reqid
        self.comp=comp
        self.taskcode=taskcode
        self.currstep = currstep
        self.startloc=startloc
        self.endstep=endstep
        self.endloc=endloc
        self.hsmsg=hsmsg
        self.exec=exec

    def __str__(self) -> str:
        text="{} {} {} {} {} {} {} {} {}".format(self.tid,self.rid,self.reqid,self.comp,self.taskcode,self.currstep,self.endstep,self.startloc,self.endloc)
        return text
        