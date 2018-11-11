import json
import socket
import logging
import binascii
import struct
import argparse
import random
import time
from pprint import pprint
from Tank import Tank
from serverMessageTypes import ServerMessageTypes
from quickPointMaths import *

class ServerComms(object):
	'''
	TCP comms handler
	Server protocol is simple:
	* 1st byte is the message type - see ServerMessageTypes
	* 2nd byte is the length in bytes of the payload (so max 255 byte payload)
	* 3rd byte onwards is the payload encoded in JSON
	'''
	ServerSocket = None
	MessageTypes = ServerMessageTypes()


	def __init__(self, hostname, port):
		self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ServerSocket.connect((hostname, port))

	def readMessage(self):
		'''
		Read a message from the server
		'''
		messageTypeRaw = self.ServerSocket.recv(1)
		messageLenRaw = self.ServerSocket.recv(1)
		messageType = struct.unpack('>B', messageTypeRaw)[0]
		messageLen = struct.unpack('>B', messageLenRaw)[0]

		if messageLen == 0:
			messageData = bytearray()
			messagePayload = {'messageType': messageType}
		else:
			messageData = self.ServerSocket.recv(messageLen)
			logging.debug("*** {}".format(messageData))
			messagePayload = json.loads(messageData.decode('utf-8'))
			messagePayload['messageType'] = messageType

		logging.debug('Turned message {} into type {} payload {}'.format(
			binascii.hexlify(messageData),
			self.MessageTypes.toString(messageType),
			messagePayload))
		return messagePayload

	def sendMessage(self, messageType=None, messagePayload=None):
		'''
		Send a message to the server
		'''
		message = bytearray()

		if messageType is not None:
			message.append(messageType)
		else:
			message.append(0)

		if messagePayload is not None:
			messageString = json.dumps(messagePayload)
			message.append(len(messageString))
			message.extend(str.encode(messageString))

		else:
			message.append(0)

		logging.debug('Turned message type {} payload {} into {}'.format(
			self.MessageTypes.toString(messageType),
			messagePayload,
			binascii.hexlify(message)))
		time.sleep(0.045)
		return self.ServerSocket.send(message)

# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
parser.add_argument('-H', '--hostname', default='127.0.0.1', help='Hostname to connect to')
parser.add_argument('-p', '--port', default=8052, type=int, help='Port to connect to')
parser.add_argument('-n', '--name', default='RandomBot', help='Name of bot')
args = parser.parse_args()

# Set up console logging
if args.debug:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.DEBUG)
else:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)


# Connect to game server
GameServer = ServerComms(args.hostname, args.port)

# Spawn our tank
logging.info("Creating tank with name '{}'".format(args.name))
GameServer.sendMessage(ServerMessageTypes.CREATETANK, {'Name': args.name})

myTank = Tank(args.name)

def update_state(message):
	if "Type" in message and message["Type"] == "Tank" and message["Name"] == args.name:
		myTank.update_tank(message)
	elif "Type" in message and message["Type"] == "Tank":
		id_ = message["Id"]
		ok = 0
		for index in range(len(tanks)):
			if tanks[index]["Id"] == id_:
				tanks[index] = message
				ok = 1

		if ok == 0:
			tanks.append(message);
	elif "Type" in message and message["Type"] == "AmmoPickup":
		id_ = message["Id"]
		ok = 0
		for index in range(len(ammo)):
			if ammo[index]["Id"] == id_:
				ammo[index] = message
				ok = 1

		if ok == 0:
			ammo.append(message);
	elif "Type" in message and message["Type"] == "HealthPickup":
		id_ = message["Id"]
		ok = 0
		for index in range(len(health)):
			if health[index]["Id"] == id_:
				health[index] = message
				ok = 1

		if ok == 0:
			health.append(message);

def move(tank, target):
	[heading, distance] = tank.go_to(target)
	global GameServer
	GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': heading})
	if distance > 4:
		GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': distance})

def go_to_goal(tank):
	blue = get_dist(tank.getPosition(), blue_goal)
	orange = get_dist(tank.getPosition(), orange_goal)
	if blue < orange:
		move(tank, blue_goal)
	else:
		move(tank, orange_goal)

def point_and_shoot(tank, target):
	heading = get_heading(tank.getPosition(), target)
	global GameServer
	GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': heading})
	GameServer.sendMessage(ServerMessageTypes.STOPMOVE)
	GameServer.sendMessage(ServerMessageTypes.FIRE)

def ninonino(tank):
	distances = []
	global health
	for i in health:
		distances.append(get_dist(tank.getPosition(), Point(i['X'], i['Y'])))

	if len(distances) != 0:
		message = health[distances.index(min(distances))]
		if is_not_at_point(tank.getPosition(), Point(message['X'], message['Y'])):
			move(tank, Point(message['X'], message['Y']))
		else:
			health.remove(message)
	else:
		GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 2})
		GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})

def INeedAmmo(tank):
	distances = []
	global ammo
	for i in ammo:
		distances.append(get_dist(tank.getPosition(), Point(i['X'], i['Y'])))

	if len(distances) != 0:
		message = ammo[distances.index(min(distances))]
		if is_not_at_point(tank.getPosition(), Point(message['X'], message['Y'])):
			move(tank, Point(message['X'], message['Y']))
		else:
			ammo.remove(message)
	else:
		GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 2})
		GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})

def shootyTooty(tank):
	distances = []
	global tanks
	tanks = sorted(tanks, key = lambda enemy: enemy['Health'] + get_dist(tank.getPosition(), Point(enemy['X'], enemy['Y']))/50) # could also use enemy['Health']
	tanks = [t for t in tanks if t['Health'] != 0]

	if(len(tanks) != 0):
		enemy = tanks[0]
		point_and_shoot(tank, Point(enemy['X'], enemy['Y']))

	# GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 2})
	# GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})


def is_not_at_point(tankPos, target):
	if get_dist(tankPos, target) < 4:
		return False
	return True



tanks = []
ammo = []
health = []
while True:
	message = GameServer.readMessage()
	# print(message)
	update_state(message)

	# print(myTank.getId())
	# GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 2})
	# GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})
	# print(myTank.getPosition())
	shootyTooty(myTank)
