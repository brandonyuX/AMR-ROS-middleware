#Main class for robot 

class Robot:
    cost=0
    def __init__(self,rid,currloc,battlvl,x,y,r,avail) -> None:
        self.rid=rid
        self.currloc=currloc
        self.battlvl=battlvl
        self.x=x
        self.y=y
        self.r=r
        self.avail=avail
    
    def setCost(self,cost):
        self.cost=cost

    def __str__(self) -> str:
        tempstr='Robot ID : {}, Current Location : {}, Current Battery Level: {}'.format(self.rid,self.currloc,self.battlvl)
        return tempstr