#Main class for robot 
import json

class Robot:
    cost=0
    def __init__(self,rid,currloc,battlvl,x,y,r,avail,msg) -> None:
        self.rid=rid
        self.currloc=currloc
        self.battlvl=battlvl
        self.x=x
        self.y=y
        self.r=r
        self.avail=avail
        self.msg=msg
    
    def setCost(self,cost):
        self.cost=cost

    def __str__(self) -> str:
        tempstr='Robot ID : {}, Current Location : {}, Current Battery Level: {}, Availability: {}'.format(self.rid,self.currloc,self.battlvl,self.avail)
        return tempstr

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)