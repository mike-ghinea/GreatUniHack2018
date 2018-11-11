from quickPointMaths import *
from serverMessageTypes import ServerMessageTypes

class Tank(object):

    def __init__(self, name):
        self.position = Point(0,0)
        self.health = 5
        self.ammo = 10
        self.heading = 0
        self.turret_heading = 0
        self.id = 0
        self.name = name

    def update_tank(self, message):
        if 'messageType' in message and message['messageType'] == ServerMessageTypes.OBJECTUPDATE:
            if message['Name'] == self.name:
                self.setPosition(Point(message['X'],message['Y']))
                self.setHealth(message['Health'])
                self.setAmmo(message['Ammo'])
                # print("Pre :", self.heading)
                self.setHeading(message['Heading'])
                # print("Post:", self.heading)
                self.setTurretHeading(message['TurretHeading'])
                self.setId(message['Id'])


    def getPosition(self):
        return self.position

    def setPosition(self, point):
        self.position = point

    def getHealth(self):
        self.health

    def setHealth(self, val):
        self.health = val

    def getAmmo(self):
        return self.ammo

    def setAmmo(self, val):
        self.ammo = val

    def getHeading(self):
        return self.heading

    def setHeading(self, val):
        self.heading = val

    def getTurretHeading(self):
        return self.turret_heading

    def setTurretHeading(self, val):
        self.turret_heading = val

    def getId(self):
        return self.id

    def setId(self, val):
        self.id = val

    def go_to(self, target):
        distance = get_dist(self.getPosition(), target)
        heading = get_heading(self.getPosition(), target)
        return [heading, distance]
