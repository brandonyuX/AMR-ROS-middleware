#Main class for PLC request 

class PLCReq:
    def __init__(self,plcid,reqid,pickup,destloc,priority,reqtime,srcloc,tskmodno,tranid) -> None:
        self.plcid=plcid
        self.reqid=reqid
        self.pickup=pickup
        self.destloc=destloc
        self.priority=priority
        self.reqtime=reqtime
        self.srcloc=srcloc
        self.tskmodno=tskmodno
        self.tranid=tranid

    def __str__(self) -> str:
        tempStr='Request from PLC {} to {} with priority {}'.format(self.plcid,self.destloc,self.priority)
        return tempStr

        