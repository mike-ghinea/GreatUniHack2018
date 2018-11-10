import math

def radToDeg(angle):
    return angle * (180.0 / math.pi)

def getHeading(x1, y1, x2, y2):
    heading = math.atan2(y2-y1, x2-x1)
    heading = radToDeg(heading)
    heading = (heading - 360) % 360
    return math.fabs(heading)

def isTurnLeft(currentHeading, desiredHeading):
    diff = desiredHeading - currentHeading
    if (diff > 0):
        return (diff > 180)
    else:
        return (diff >= -180)

def calcDist(thisX, thisY, thatX, thatY):
    headingX = thatX - thisX
    headingY = thatY - thisY
    return math.sqrt(headingX*headingX + headingY*headingY)

#test values
'''
print "radToDeg pi = \n"
print(radToDeg(math.pi))
print "\ngetHeading(420, 69, 1337, 80) = \n"
print(getHeading(420, 69, 1337, 80))
print "\ncalcDist(420, 69, 1337, 80) = \n"
print(calcDist(420, 69, 1337, 80))
'''
