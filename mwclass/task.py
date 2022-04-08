#Main class for task 

class Task:
    def __init__(self,tid,rid,reqid,comp,tc,td,startloc,endloc,hsmsg) -> None:
        self.tid=tid
        self.rid=rid
        self.reqid=reqid
        self.comp=comp
        self.tc=tc
        self.td=td
        self.startloc=startloc
        self.endloc=endloc
        self.hsmsg=hsmsg
        