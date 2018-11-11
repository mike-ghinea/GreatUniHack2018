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

	elif "Type" in message and message["Type"] == "Shitch":
		id_ = message["Id"]
		ok = 0
		for index in range(len(snitch)):
			if snitch[index]["Id"] == id_:
				snitch[index] = message
				ok = 1

		if ok == 0:
			snitch.append(message);

def move(tank, target):
	print("Moving")
	[heading, distance] = tank.go_to(target)
	global GameServer
	GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': heading})
	if distance > 4:
		GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': distance})

def move_step_towards(tank, target):
	global GameServer
	GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 1})

def go_to_goal(tank):
	print("Going to goal")
	blue = get_dist(tank.getPosition(), blue_goal)
	orange = get_dist(tank.getPosition(), orange_goal)
	if blue < orange:
		move(tank, blue_goal)
	else:
		move(tank, orange_goal)

def point_and_shoot(tank, target):
	print("Pointing and shooting")
	heading = get_heading(tank.getPosition(), target)
	global GameServer
	GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': heading})
	GameServer.sendMessage(ServerMessageTypes.STOPMOVE)
	GameServer.sendMessage(ServerMessageTypes.FIRE)

def ninonino(tank):
	print("Getting health")
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
	print("Getting ammo")
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
	print("Shooting everyoneeee")
	distances = []
	global tanks
	tanks = sorted(tanks, key = lambda enemy: enemy['Health'] + get_dist(tank.getPosition(), Point(enemy['X'], enemy['Y']))) # could also use enemy['Health']
	tanks = [t for t in tanks if t['Health'] != 0]

	if(len(tanks) != 0):
		enemy = tanks[0]
		if get_dist(tank.getPosition(), Point(enemy['X'], enemy['Y'])) > 40:
			print("here")
			move_step_towards(tank, Point(enemy['X'], enemy['Y']))
		point_and_shoot(tank, Point(enemy['X'], enemy['Y']))
	else:
		GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 2})
		GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})

def get_snitch(tank):
	print('Getting snitch')
	move(tank, Point(snitch[0]['X'], snitch[0]['Y']))

def kill_tank_with_snitch(tank, id):
	print('Trying to kill tank with snitch')
	enemies = [t for t in tanks if t['Id'] == id]
	if len(enemies) != 0:
		enemy = enemies[0]
		point_and_shoot(tank, Point(enemy['X'], enemy['Y']))
		move(tank, Point(enemy['X'], enemy['Y']))
	else:
		shootyTooty(tank)

def is_not_at_point(tankPos, target):
	if get_dist(tankPos, target) < 4:
		return False
	return True



tanks = []
ammo = []
health = []
snitch = []
should_bank = False
snitch_in_game = False
got_snitch = False
unbanked_kills = 0
tank_with_snitch = False
tank_with_snitch_id = 0
while True:
	message = GameServer.readMessage()
	# print(message)
	update_state(message)

	if 'messageType' in message:
		if message['messageType'] == ServerMessageTypes.KILL:
			unbanked_kills += 1
		elif message['messageType'] == ServerMessageTypes.SNITCHAPPEARED:
			snitch_in_game = True
		elif message['messageType'] == ServerMessageTypes.SNITCHPICKUP:
			if message['Id'] == myTank.getId():
				got_snitch = True
			else:
				tank_with_snitch = True
				tank_with_snitch_id = message['Id']
		elif message['messageType'] == ServerMessageTypes.ENTEREDGOAL:
			unbanked_kills = 0

	if got_snitch:
		go_to_goal(myTank)
	elif tank_with_snitch:
		kill_tank_with_snitch(myTank, tank_with_snitch_id)
	elif snitch_in_game:
		get_snitch(myTank)
	elif unbanked_kills > 0:
		go_to_goal(myTank)
	elif myTank.getAmmo() != 0 and len(tanks) != 0:
		shootyTooty(myTank)
	elif myTank.getAmmo() < 8:
		INeedAmmo(myTank)
	else:
		ninonino(myTank)


	# print(myTank.getId())
	# GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 2})
	# GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})
	# print(myTank.getPosition())
