import quickPointMaths

class Tank:
    def __init__(self, point):
        self.point = point

    def getPosition(self):
        return Point(self.point)

    def getHealth(self):
        pass

    def setHealth(self):
        pass

    def getAmmo(self):
        pass

    def fire(self):
        pass

                
#centre of arena
centrePoint = Point(0,0)
#Boundaries of the arena
xAxisMax = Point(70,0)
xAxisMin = Point(-70,0)
yAxisMax = Point(0,100)
yAxisMin = Point(0,-100)

def move(tank, endPoint):
    startPoint = tank.getPosition()
