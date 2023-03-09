#Main class for PLC request 

class WO:
    def __init__(self,batchid,sn,mfgdate,fnpdate,fillvol,torque,wolist,expdate,ordernum=None,itemtype=None) -> None:
        
        self.batchid=batchid
        self.sn=sn
        self.mfgdate=mfgdate
        self.fnpdate=fnpdate
        self.fillvol=fillvol
        self.torque=torque
        self.wolist=wolist
        self.expdate=expdate
        self.ordernum=ordernum
        self.itemtype=itemtype

 

        