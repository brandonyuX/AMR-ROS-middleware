#Main class for Station Map
class StationMap:
    def __init__(self,locname,x,y,r,avail) -> None:
        self.locname=locname
        self.x=x
        self.y=y
        self.r=r
        self.avail=avail

    def __str__(self) -> str:
        text= "Location Name:{} X postion:{} Y Position:{} R Position:{} Availability:{}".format(self.locname,self.x,self.y,self.r,self.avail)
        return text