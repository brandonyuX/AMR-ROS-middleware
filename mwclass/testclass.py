import json
class testclass():
    def __init__(self,x,y,z) -> None:
        self.x=x
        self.y=y
        self.z=z

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)