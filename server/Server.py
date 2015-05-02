from pandac.PandaModules import *
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.PyDatagram import PyDatagram
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

class Server(QueuedConnectionManager):
	def __init__(self,p,b):
		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)
		self.port = p
		self.backlog = b
		self.socket = self.cManager.openTCPServerRendezvous(self.port,self.backlog)
		self.cListener.addConnection(self.socket)
		print str(self)
	def tskReaderPolling(self,regClass): #This function listens for any data coming on already established functions
		if self.cReader.dataAvailable():
			self.datagram=NetDatagram()  # catch the incoming data in this instance
		# Check the return value; if we were threaded, someone else could have
		# snagged this data before we did
			if self.cReader.getData(self.datagram):
				regClass.updateData(self.datagram.getConnection(), self.datagram,self)
					
		return Task.cont
	def tskListenerPolling(self,regClass): #This Function checks to see if there are any new clients and adds their connection
		#if theres a new connection add it to our listener
		if self.cListener.newConnectionAvailable():
			self.rendezvous = PointerToConnection()
			self.netAddress = NetAddress()
			self.newConnection = PointerToConnection()
			if self.cListener.getNewConnection(self.rendezvous,self.netAddress,self.newConnection):
				self.newConnection = self.newConnection.p()
				regClass.PlayerList.append(player())
				regClass.PlayerList[regClass.active].connectionID = self.newConnection
				regClass.sendInitialInfo(regClass.active, self)
				regClass.active += 1
				self.cReader.addConnection(self.newConnection)     # Begin reading connection
				print 'connection received'
		return Task.cont

	
class PlayerReg(DirectObject): #This class will hold anything that is related to regulating clients
	def __init__(self):
		self.PlayerList = []
		self.active = 0
		self.timeSinceLastUpdate = 0
		
	
	def updatePlayers(self,serverClass,data,type):
		if (type == "positions"):
			#keep players updated on their position
			self.elapsed = globalClock.getDt()
			self.timeSinceLastUpdate += self.elapsed
			if (self.timeSinceLastUpdate > 0.1):
				if (self.active):
					self.datagram = PyDatagram()
					self.datagram.addString("update")
					#add the number of players
					self.datagram.addFloat64(self.active)
					#add every players current position
					for k in range(self.active):
						self.datagram.addFloat64(self.PlayerList[k].currentPos['x'])
						self.datagram.addFloat64(self.PlayerList[k].currentPos['y'])
						self.datagram.addFloat64(self.PlayerList[k].currentPos['z'])
						self.datagram.addFloat64(self.PlayerList[k].currentPos['h'])
						self.datagram.addFloat64(self.PlayerList[k].currentPos['p'])
						self.datagram.addFloat64(self.PlayerList[k].currentPos['r'])
					for k in self.PlayerList:
						self.conn = k.connectionID
						serverClass.cWriter.send(self.datagram,self.conn)
				self.timeSinceLastUpdate = 0
			return Task.cont
		
		if(type == "chat"):
			#Keep players up to date with all the chat thats goin on
			self.iterator = data
			self.datagram = PyDatagram()
			self.datagram.addString("chat")
			self.text = self.iterator.getString()
			self.datagram.addString(self.text)
			print self.text,' ',str(serverClass)
			for k in self.PlayerList:
				serverClass.cWriter.send(self.datagram,k.connectionID)
				
				
		
	def updateData(self,connection, datagram,serverClass):
		self.iterator = PyDatagramIterator(datagram)
		self.type = self.iterator.getString()
		if (self.type == "positions"):
			for k in self.PlayerList:
				if (k.connectionID == connection):
					k.currentPos['x'] = self.iterator.getFloat64()
					k.currentPos['y'] = self.iterator.getFloat64()
					k.currentPos['z'] = self.iterator.getFloat64()
					k.currentPos['h'] = self.iterator.getFloat64()
					k.currentPos['p'] = self.iterator.getFloat64()
					k.currentPos['r'] = self.iterator.getFloat64()
		if (self.type == "chat"):
			self.updatePlayers(serverClass,self.iterator,"chat")
	
	def sendInitialInfo(self,i,server): #Initialize the new Player
		self.con = self.PlayerList[i].connectionID #set the connection to the player's connection
		self.datagram = PyDatagram() #create a datagram instance
		self.datagram.addString("init") #specify to the client that this is an init type packet
		self.datagram.addUint8(self.active) #specify the player's number (not sure why this is here)
		self.datagram.addFloat64(i) #specify number of players (same as player's number)
		for k in self.PlayerList: #Add the current position of everyone in the game world and send it
			self.datagram.addString(k.username)
			self.datagram.addFloat64(k.currentPos['x'])
			self.datagram.addFloat64(k.currentPos['y'])
			self.datagram.addFloat64(k.currentPos['z'])
		server.cWriter.send(self.datagram,self.con)

class player(DirectObject):
	def __init__(self):
		self.connectionID = 0
		self.username = ""
		self.currentPos = {'x':0,'y':0,'z':0,'h':0,'p':0,'r':0} #also stores rotation
		self.isMoving = False #if its moving the clients will need to know to animate it it (not implemented yet)


		