import quickPointMaths
import TankObject

#centre of arena
centrePoint = Point(0,0)
#Boundaries of the arena
xAxisMax = Point(70,0)
xAxisMin = Point(-70,0)
yAxisMax = Point(0,100)
yAxisMin = Point(0,-100)

def move(tank, endPoint):
    startPoint = tank.getPosition()
