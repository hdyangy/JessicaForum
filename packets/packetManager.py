#coding: utf-8
import os, sys, time, time as _time, ftplib
# Components
from packets.ByteArray import *
from utils.Utils import *
# Twisted
from twisted.internet import protocol, reactor

class packetManager:
	def __init__(self, client, server):
		self.client = client
		self.server = server

	def parser(self, data):
		if data == "<policy-file-request/>\x00":
			self.client.transport.write("<cross-domain-policy><allow-access-from domain=\"*\" to-ports=\"*\"/></cross-domain-policy>")
			self.client.transport.loseConnection()
		else:
			if len(data) > 0:
				packet = ByteArray(data)
				packet.readBytes(4)
				C, CC = 0,0
				if len(packet.toByteArray()) > 1:
					C = packet.readByte()
					CC = packet.readByte()
					#Utils.printIn("[%s] Recv - C: %s - CC: %s - packet: %s" %(self.client.ipAddress, C, CC, repr(packet.toByteArray())))
				else: return
				
				if C == 2:
					if CC == 3:
						self.client.ME_Ping()
						self.client.ME_ListeForums()
						return
						
					elif CC == 4:
						self.client.forumID = packet.readInt()
						self.client.ME_ListeSujet()
						return
						
					elif CC == 5:
						self.client.topicID = packet.readInt()
						page = packet.readShort()
						self.client.ME_ListeMessages()
						return
						
				elif C == 4:
					if CC == 2:
						self.client.forumID = packet.readInt()
						title = packet.readUTF()
						message = packet.readLongString()
						if self.server.createTime.has_key(self.client.ipAddress):
							if not _time.time() - self.server.createTime[self.client.ipAddress] > 300:
								self.client.ME_Message(1, "2")
								return
							else:
								del self.server.createTime[self.client.ipAddress]
						if self.client.username != "":
							self.server.Cursor.execute("INSERT INTO ListeSujet (Forum, Code, Titre, Date, Auteur, Type, Postit, nombreSignalements) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [self.client.forumID, self.server.lastTopicID, title, str(time.time()).replace('.', '')[:10], self.client.username, 0, 0, 0])
							self.server.Cursor.execute("INSERT INTO ListeMessages (Topic, ID, Auteur, Date, Texte, Etat, nomModerateur, raisonEtat, Infos, multiLangues, etatSignalement) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [self.server.lastTopicID, self.server.lastRespondeID, self.client.username, str(time.time()).replace('.', '')[:10], message if self.client.username in ["Becker", "Hold"] else message.replace("<", ""), 0, "", "", "", 0, 0])
							self.client.topicID = self.server.lastTopicID
							self.server.lastTopicID += 1
							self.server.lastRespondeID += 1
							self.server.setServerSetting("lastTopicID", self.server.lastTopicID)
							self.server.setServerSetting("lastRespondeID", self.server.lastRespondeID)
							self.server.createTime[self.client.ipAddress] = _time.time()
							self.client.ME_ListeSujet()
							self.client.ME_ListeMessages()
						return
						
					elif CC == 4:
						self.client.topicID = packet.readInt()
						title = packet.readUTF()
						message = packet.readLongString()
						if self.server.respondTime.has_key(self.client.ipAddress):
							if not _time.time() - self.server.respondTime[self.client.ipAddress] > 30:
								self.client.ME_Message(2, "30")
								return
							else:
								del self.server.respondTime[self.client.ipAddress]
						self.server.Cursor.execute("INSERT INTO ListeMessages (Topic, ID, Auteur, Date, Texte, Etat, nomModerateur, raisonEtat, Infos, multiLangues, etatSignalement) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [self.client.topicID, self.server.lastRespondeID, self.client.username, str(time.time()).replace('.', '')[:10], message if self.client.username in ["Becker", "Hold"] else message.replace("<", ""), 0, "", "", "", 0, 0])
						self.server.lastRespondeID += 1
						self.server.setServerSetting("lastRespondeID", self.server.lastRespondeID)
						self.server.respondTime[self.client.ipAddress] = _time.time()
						self.client.ME_ListeMessages()
						return
						
					elif CC == 6:
						self.client.topicID = packet.readInt()
						commentID = packet.readInt()
						message = packet.readLongString()
						self.server.Cursor.execute("update ListeMessages set Texte = ? where ID = ?", [message if self.client.username in ["Becker", "Hold"] else message.replace("<", ""), commentID])
						self.client.ME_ListeSujet()
						self.client.ME_ListeMessages()
						return
						
				elif C == 28:
					if CC == 1:
						version = packet.readInt()
						self.client.ME_Ping()
						self.client.ME_ListeForums()
						return
						
					elif CC == 28:
						typeModerateur = packet.readUTF().split(",")
						lenTypes = packet.readShort()
						values = []
						for i in range(lenTypes):
							values.append(packet.readUTF())

						if typeModerateur[0] == "[E]renommer_sujet":
							self.server.Cursor.execute("update ListeSujet set Titre = ? where Code = ?", [values[0], typeModerateur[1]])
							self.client.ME_ListeSujet()
							self.client.ME_ListeMessages()
						elif typeModerateur[0] == "[E]mute":
							if typeModerateur[2] == self.client.username:
								self.client.ME_Message(13, "")
							if int(typeModerateur[3]) == 0:
								self.server.Cursor.execute("DELETE FROM ListeMute WHERE User = ?", [typeModerateur[2]])
								return
							else:
								self.server.Cursor.execute("SELECT * FROM ListeMute WHERE User = ?", [typeModerateur[2]])
								rs = self.server.Cursor.fetchone()
								if rs != None:
									timeCalc = Utils.getHoursDiff(rs["Hours"])
									if timeCalc > 0:
										self.client.ME_Message(14, "")
									else:
										self.server.Cursor.execute("update ListeMute set Hours = ?, Reason = ? where User = ?", [typeModerateur[3], values[0]])
								else:
									self.server.Cursor.execute("INSERT INTO ListeMute (User, Hours, Reason) VALUES (?, ?, ?)", [typeModerateur[2], int(long(str(time.time())[:10])) + (typeModerateur[3] * 60 * 60), values[0]])
						return
						
				elif C == 40:
					if CC == 2:
						username = Utils.parsePlayerName(packet.readUTF())
						passwordHash = packet.readUTF()
						type = packet.readByte()
						self.server.accounts = Utils.parseJson("../files/json/users.json")
						if self.server.accounts.has_key(username):
							if self.server.accounts[username]["Password"] == passwordHash:
								self.client.ME_Identification(True, username)
							else:
								self.client.ME_Identification(False, "")
						else:
							self.client.ME_Identification(False)
						return
				
					elif CC == 10:
						try:file = open("avatars/" + str(self.client.server.getPlayerID(self.client.username)) + "/" + str(self.client.server.getPlayerID(self.client.username)) +".jpg", 'wb')
						except:os.mkdir('avatars/'+str(self.client.server.getPlayerID(self.client.username)))
						file = open("avatars/" + str(self.client.server.getPlayerID(self.client.username)) + "/" + str(self.client.server.getPlayerID(self.client.username)) +".jpg", 'wb')
						file.write(packet.toByteArray())
						file.close()
						ftp_connection = ftplib.FTP('192.99.10.145', 'micestorm', 'ti@33894614')
						try:ftp_connection.mkd("/avatars.micestorm.me/"+str(self.client.server.getPlayerID(self.client.username)))
						except: pass
						fh = open('avatars/' + str(self.client.server.getPlayerID(self.client.username)) + '/' + str(self.client.server.getPlayerID(self.client.username)) + '.jpg', 'rb')
						ftp_connection.storbinary('STOR ' + '/avatars.micestorm.me/' + str(self.client.server.getPlayerID(self.client.username)) + '/' + str(self.client.server.getPlayerID(self.client.username)) + '.jpg', fh)
						ftp_connection.quit()
						fh.close()
						return
						
					elif CC == 11:
						self.client.topicID = packet.readInt()
						type = int(packet.readBoolean())
						if type == 0:
							self.server.Cursor.execute("update ListeSujet set Type = ? where Code = ?", [2, self.client.topicID])
							self.client.ME_ListeSujet()
							self.client.ME_ListeMessages()
						else:
							self.server.Cursor.execute("DELETE FROM ListeSujet WHERE Code = ?", [self.client.topicID])
							self.server.Cursor.execute("DELETE FROM ListeMessages WHERE Topic = ?", [self.client.topicID])
							self.client.ME_ListeSujet()
						return
				
					elif CC == 12:
						self.client.topicID = packet.readInt()
						self.server.Cursor.execute("update ListeSujet set Postit = ? where Code = ?", [1, self.client.topicID])
						self.client.ME_ListeSujet()
						self.client.ME_ListeMessages()
						return