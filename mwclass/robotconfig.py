#Main Class for robot configuration

class RobotConfig:
    def __init__(self,rid,alias,battthres,defloc,rip) -> None:
        self.rid=rid
        self.alias=alias
        self.battthres=battthres
        self.defloc = defloc
        self.rip=rip

    def __str__(self) -> str:
        text="Robot ID:{}, Alias:{}, Battery Threshold:{}, Default Location:{}, Robot IP:{}".format(self.rid,self.alias,self.battthres,self.defloc,self.rip)
        return text

    # def __init__(self,rid) -> None:
    #     self.rid=rid
        

