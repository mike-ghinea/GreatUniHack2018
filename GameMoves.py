import quickPointMaths
import Tank

#centre of arena
centrePoint = Point(0,0)
#Boundaries of the arena
xAxisMax = Point(70,0)
xAxisMin = Point(-70,0)
yAxisMax = Point(0,100)
yAxisMin = Point(0,-100)

#Move from start to end point 
def move(tank, endPoint):
    startPoint = tank.getPosition()
    currentPos = startPoint
    if (endPoint.getX() - startPoint.getX() < 0):
        xspeed = -1
    elif (endPoint.getX() - startPoint.getX() > 0):
        xspeed = 1
    else:
        pass
    if (endPoint.getY() - startPoint.getY() < 0):
        yspeed = -1
    elif (endPoint.getY() - startPoint.getY() > 0):
        yspeed = 1
    else:
        pass
    for x in range(1, getDist(startPoint, endPoint)):
        currentPos.setX(currentPos.getX() + xspeed)
        currentPos.setY(currentPos.getY() + yspeed)
        tank.setPosition(currentPos)
