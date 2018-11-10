import quickPointMaths
import Tank

speed = 10

#centre of arena
centrePoint = Point(0,0)
#Boundaries of the arena
xAxisMax = Point(70,0)
xAxisMin = Point(-70,0)
yAxisMax = Point(0,100)
yAxisMin = Point(0,-100)

def move(tank, endPoint):
    startPoint = tank.getPosition()
    distance = getDist(startPoint, endPoint)
    currentPosition = startPoint
    for x in range(1, distance):
        pass
