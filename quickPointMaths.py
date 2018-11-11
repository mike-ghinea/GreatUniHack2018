import math

#def radToDeg(angle):
    #return angle * (180.0 / math.pi)

class Point(object):
    """docstring for Point."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return float(self.x)

    def getY(self):
        return float(self.y)

    def __str__(self):
        return "Point(%s,%s)"%(self.x, self.y)

def get_dist(pointA, pointB):
    headingX = pointB.getX() - pointA.getX()
    headingY = pointB.getY() - pointA.getY()
    return math.hypot(headingX, headingY)

def get_heading(pointA, pointB):
    heading = math.atan2(pointB.getY() - pointA.getY(), pointB.getX() - pointA.getX())
    heading = math.degrees(heading)
    heading = - heading % 360
    return math.fabs(heading)

def is_turn_left(currentHeading, desiredHeading):
    diff = desiredHeading - currentHeading
    if (diff > 0):
        return (diff > 180)
    else:
        return (diff >= -180)


# Important Points
centre = Point(0, 0)
blue_goal = Point(0,100)
orange_goal = Point(0, -100)

#test values
'''
somePoint = Point(69.420, 13.37)
anotherPoint = Point(73.31, 24.96)

print(getHeading(somePoint, anotherPoint))
print(getDist(somePoint, anotherPoint))
'''
