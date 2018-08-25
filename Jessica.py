#coding: utf-8
import os, sys, time, ConfigParser, sqlite3
sys.dont_writeBytecode = True
os.system("title Jessica Forums")
# Components
from packets.packetManager import *
from utils.Utils import *
# Log
Utils.printIn("Jessica Forums", "info")
# Twisted
from twisted.internet import protocol, reactor

class JessicaClient(protocol.Protocol):
	def __init__(self):
		self.username = str()
		self.topicID = int()
		self.forumID = int()
		self.isMute = False
		
	def connectionMade(self):
		self.ipAddress = self.transport.getPeer().host
		self.server = self.factory
		self.packetManager = packetManager(self, self.server)
		self.Cursor = self.server.Cursor
		if len(self.server.connectedAddress) >= int(self.server.connectionPerEmu):
			Utils.printIn("[%s] IP Disconnected for Connection Limit Per EMU: %s" %(self.ipAddress, self.ipAddress))
			self.transport.loseConnection()
		else:
			if self.server.connectedAddress.has_key(self.ipAddress):
				self.server.connectedAddress[self.ipAddress] += 1
			else:
				self.server.connectedAddress[self.ipAddress] = 1
			if self.server.connectedAddress[self.ipAddress] >= self.server.connectionPerIP:
				Utils.printIn("[%s] IP Disconnected for Connection Limit:" %(self.ipAddress, self.ipAddress))
			else:
				Utils.printIn("[%s] New Client: %s" %(self.ipAddress, self.ipAddress))

	def connectionLost(self, reason=""):
		self.server.connectedAddress[self.ipAddress] -= 1
		if self.server.connectedAddress[self.ipAddress] <= 0:
			del self.server.connectedAddress[self.ipAddress]
		Utils.printIn("[%s] Client closed: %s" %(self.ipAddress, self.ipAddress))
		
	def dataReceived(self, data):
		self.packetManager.parser(data)
		
	def sendPacket(self, identifiers, data):
		packet = ByteArray()
		packet.writeByte(identifiers[0])
		packet.writeByte(identifiers[1])
		packet.writeBytes(data)
		self.transport.write(packet.toPack())
		#Utils.printIn("[%s] Send - C: %s - CC: %s - packet: %s" %(self.ipAddress, identifiers[0], identifiers[1], repr(packet.toByteArray())))

	def ME_Ping(self):
		packet = ByteArray()
		packet.writeInt(len(self.server.connectedAddress))
		self.sendPacket([40, 40], packet.toByteArray())
		
	def ME_Identification(self, login=False, username=""):
		packet = ByteArray()
		packet.writeByte(int(login))
		if login:
			self.username = username
			packet.writeUTF(str(self.username))
			packet.writeInt(self.server.getPlayerID(self.username))
			packet.writeInt(self.server.checkPrivlevel(self.username))
		self.sendPacket([40, 2], packet.toByteArray())
		self.checkMute()

	def checkMute(self):
		mute = self.server.checkMute(self.username)
		if mute[0]:
			timeCalc = Utils.getHoursDiff(mute[1])
			if timeCalc > 0:
				self.isMute = True
				self.ME_Message(5, mute[2])
			else: self.server.Cursor.execute("DELETE FROM ListeMute WHERE User = ?", [self.username])
		return
		
	def ME_Message(self, code, message):
		packet = ByteArray()
		packet.writeInt(code)
		packet.writeUTF(message)
		self.sendPacket([40, 4], packet.toByteArray())
		
	def ME_ListeForums(self):
		packet = ByteArray()
		packet.writeUTF("br")
		for forums in self.server.forumsList.items():
			packet.writeInt(forums[0])
			packet.writeUTF(forums[1][0])
			packet.writeShort(forums[1][1])
		self.sendPacket([2, 2], packet.toByteArray())
		
	def ME_ListeSujet(self):
		packet = ByteArray()
		if self.username != "" and not self.isMute: # Poder criar tópico
			if self.forumID == 1:
				if self.server.checkPrivlevel(self.username) in [19, 20]:packet.writeBoolean(True)
				else:packet.writeBoolean(False)
			else:packet.writeBoolean(True)
		else:packet.writeBoolean(False)
		packet.writeInt(self.forumID)
		if self.server.forumsList.has_key(self.forumID):
			packet.writeUTF(self.server.forumsList[self.forumID][0])
			packet.writeShort(self.server.forumsList[self.forumID][1])
		packet.writeInt(0)
		packet.writeInt(0)
		packet.writeBoolean(False)
		self.Cursor.execute("SELECT * FROM ListeSujet WHERE Forum = ? ORDER BY Postit DESC,Date DESC", [self.forumID])
		rs = self.Cursor.fetchall()
		for row in rs:
			packet.writeInt(row["Code"])
			packet.writeUTF(row["Titre"])
			packet.writeInt(row["Date"])
			packet.writeUTF(self.server.checkColor(row["Auteur"]))
			packet.writeByte(self.server.checkPrivlevel(row["Auteur"]))
			lastComment = self.server.getLastComment(row["Code"])
			packet.writeUTF(lastComment["Auteur"])
			packet.writeInt(self.server.lenComments(row["Code"]))
			packet.writeByte(row["Type"])
			packet.writeByte(row["Postit"])
			packet.writeInt(row["nombreSignalements"])
		self.sendPacket([2, 4], packet.toByteArray())
		
	def ME_ListeMessages(self):
		packet = ByteArray()
		packet.writeInt(self.forumID)
		packet.writeInt(self.topicID)
		self.Cursor.execute("SELECT * FROM ListeSujet WHERE Code = ?", [self.topicID])
		rs = self.Cursor.fetchone()
		if rs != None:
			if self.server.checkPermission(self.username):packet.writeByte(10)
			elif ["Auteur"] == self.username and rs["Type"] == 0:packet.writeByte(1)
			else:packet.writeByte(0)
			packet.writeBoolean(False)
			if self.username != "" and rs["Type"] == 0 and not self.isMute:
				packet.writeBoolean(True)
			else:
				packet.writeBoolean(False)
			packet.writeBoolean(False)
			packet.writeBoolean(False)
			packet.writeUTF(rs["Titre"])
		packet.writeInt(0)
		packet.writeInt(0)
		packet.writeByte(0)
		self.Cursor.execute("SELECT * FROM ListeMessages WHERE Topic = ?", [self.topicID])
		rs = self.Cursor.fetchall()
		for row in rs:
			packet.writeInt(row["ID"])
			if self.server.checkPermission(self.username):packet.writeByte(10)
			elif self.username == row["Auteur"]:packet.writeByte(1)
			else:packet.writeByte(0)
			packet.writeUTF(self.server.checkColor(str(row["Auteur"])))
			if self.server.checkPermission(self.username):packet.writeByte(10)
			elif self.username == row["Auteur"]:packet.writeByte(1)
			else:packet.writeByte(0)
			packet.writeInt(self.server.getPlayerID(row["Auteur"])) # Avatar
			packet.writeInt(int(row["Date"]))
			packet.writeUTF(row["Texte"])
			packet.writeByte(row["Etat"])
			packet.writeUTF(row["nomModerateur"])
			packet.writeUTF(row["raisonEtat"])
			packet.writeUTF(row["Infos"])
			packet.writeByte(1 if self.forumID == 1 else row["multiLangues"])
			packet.writeByte(row["etatSignalement"])
		self.sendPacket([2, 5], packet.toByteArray())
		
class JessicaServer(protocol.ServerFactory):
	protocol = JessicaClient
	def __init__(self):
		# Config
		self.config = ConfigParser.ConfigParser()
		self.config.read("./configuration/config.properties")
		self.Cursor = Cursor
		# Config Values
		self.connectionPerEmu = int(self.config.get("Jessica", "connectionPerEmu"))
		self.connectionPerIP = int(self.config.get("Jessica", "connectionPerIP"))
		self.lastTopicID = int(self.config.get("Jessica", "lastTopicID"))
		self.lastRespondeID = int(self.config.get("Jessica", "lastRespondeID"))
		# Dict
		self.clients = {}
		self.connectedAddress = {}
		self.createTime = {}
		self.respondTime = {}
		# Lists
		self.forumsList = Utils.parseJson("./json/forums.json")
		self.staffList = Utils.parseJson("./json/staffList.json")
		self.accounts = Utils.parseJson("../files/json/users.json")
		self.banList = Utils.parseJson("../files/json/banList.json")

	def setServerSetting(self, setting, value):
		self.config.set("Jessica", setting, value)
		with open("./configuration/config.properties", "w") as configfile:
			self.config.write(configfile)
		
	def checkPermission(self, username):
		if self.staffList.has_key(username):
			return True
		else:
			return False
			
	def checkPrivlevel(self, username):
		if self.staffList.has_key(username):return self.staffList[username]
		else:return 0
		
	def checkColor(self, username):
		if self.staffList.has_key(username): return {17:"<CJ>"+username, 17:"<CJ>"+username, 17:"<CJ>"+username, 18:"<CJ>"+username, 14:"<CR>"+username, 20:"<CR>"+username}[self.staffList[username]]
		else: return username

	def checkMute(self, username):
		self.Cursor.execute("SELECT * FROM ListeMute WHERE User = ?", [username])
		rs = self.Cursor.fetchone()
		if rs != None:return True, rs["Hours"], rs["Reason"]
		else: return [False, 0, ""]
		
	def getLastComment(self, topicID):
		self.Cursor.execute("SELECT Auteur, Date FROM ListeMessages WHERE Topic = ? ORDER BY Date DESC", [topicID])
		rs = self.Cursor.fetchall()
		return rs[0]
		
	def lenComments(self, topicID):
		self.Cursor.execute("SELECT * FROM ListeMessages WHERE Topic = ?", [topicID])
		rs = self.Cursor.fetchall()
		return len(rs)
		
	def getPlayerID(self, username):
		if self.accounts.has_key(username): return self.accounts[username]["PlayerID"]
		else: return 2
		
if __name__ == "__main__":
	Utils.printIn("Initializing: Settings.", "info")
	Utils.printIn("Initializing: Files.", "info")
	Utils.printIn("Initializing: Server.", "info")
	Database, Cursor = None, None
	Database = sqlite3.connect("../files/database/forums.db", check_same_thread = False)
	Database.text_factory = str
	Database.isolation_level = None
	Database.row_factory = sqlite3.Row
	Cursor = Database.cursor()
	portList = [443, 44440, 44444, 6112, 3724, 5555]
	ports = []
	for port in portList:
		try:reactor.listenTCP(port, JessicaServer()), ports.append(port)
		except: pass
	Utils.printIn("Server online on ports: %s\n" %(str(ports)), "info")
	reactor.run()