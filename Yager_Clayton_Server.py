run = True
#CLAYTON YAGER
from _thread import start_new_thread
from socket import *
from subprocess import getoutput
from sys import getsizeof
from time import sleep
ss = socket(AF_INET, SOCK_STREAM)
server = gethostname()
port = 5000
while True:
	try:
		ss.bind((server, port))
		x = open("port","w")
		x.write(str(port))
		x.close()
		break
	except:
		port += 1
ss.listen(5)
users = {}
activePlayers = []
activeSocs = []
PlayerandSocs = []
#username : [health,attck, def, rec, desc,started (bool),room(0-9)]
rooms = ["Foyer","Hall","Ball Room","Kitchen","Dining Hall","Green House","Basement","Guest Room","Narrow Hallway","Master Bedroom"]
roomDesc = ["Compared to the outside of the old creepy house the foyer is really nice. Lots of creepy paintings of cats in pajamas though.","Just a hallway. Perfectly normal I guess","You would think a ball room would be for dancing and stuff... but this is just a giant ball pit... The residents of this house sure are weird.", "Just a Kitchen","There seems to be more cat food in here than human food...","Cat Grass, Lemongrass, Cat tails, and catnip are all you can see in the planters","Just a basement...", "Everything is covered in animal hair. Hope you do not have allergies.","Small hallways are always awkward","Dats a big bed."]
connections = ["Hall","Foyer|Ball Room","Hall|Kitchen","Ball Room|Dining Hall","Kitchen|Green House","Dining Hall|Basement","Green House|Guest Room","Basement|Narrow Hallway","Guest Room|Master Bedroom","Narrow Hallway"]

monsters = [\
[[""]],\
[[""]],\
[["Ball Monster","Its only purpose is to attempt to drown you in a ball pit...",90,10,0,"Monster",200]],\
[["Leftovers","EAT YOUR BRUSSEL SPROUTS",10,10,80,"Monster",150]],\
[["Chair","I'm already out of ideas",10,10,0,"Monster",900]],\
[["Oddly Sized Venus Fly Trap","Looks Sticky",50,40,10,"Monster",80]],\
[["Swarm of Bats","You don't GUANO stay down here too long",60,40,0,"Monster",200]],\
[["Dander Monster","Benadryl is your best friend in this fight",10,80,10,"Monster",150]],\
[["Door","Why is there a door in the hallway... I dunno",0,100,0,"Monster",1000]],\
[["Cat Wizard","A Cat... I think",80,10,10,"Monster",100],["Cat Titan","A Cat... I think",80,10,10,"Monster",100],["Cat Hunter","A Cat... I think",80,10,10,"Monster",100]]
]

gameDescr="GameDescription: Your car broke down outside an old creepy house (sounds super cliche I know, but it happened to you so deal with it). It's getting dark and god knows that winter in these parts could freeze something that is generally considered really hard to freeze under normal circumstances. You enter the foyer of the house and turn to close the door... BUT IT DISAPPEARED. You have 100 points to allocate to attack, defense, and regeneration. Good luck\nExtension: MSG2A\nNiceName: yell\nType: MESSAGE\nDescription: Send a message to all players!\nParameter: None\nExtension: DELET\nNiceName: delete\nType: MESSAGE\nDescription: Delete players from the server!\nParameter: Player Name"

def updateMonsters():
	won = False
	global monsters
	while True:
		if monsters[-1] == [[""],[""],[""]]:
			if not won:
				toSend = "NOTIF CONGRATS> The Cat Lords Have Been Slain. You Win!"
				won = True
				for soccc in activeSocs:
					soccc.send(toSend.encode())
		
		for roomNumber in range(len(monsters)):
			if type(monsters[roomNumber][0]) == type([]):
				for monster in range(len(monsters[roomNumber])):
					if monsters[roomNumber][monster][-1] != "" and monsters[roomNumber][monster][-1] <= 0:
						print(str(monsters[roomNumber][monster][0])+" has been killed")
						monsters[roomNumber][monster] = [""]
						print(monsters)

def getPlayers(soc,room = "",monst = False):
	toSend = ""
	for play in activePlayers:
		pInfo = users[play]
		n = "\nName: "+str(play)+"\n"
		d = "Description: "+str(pInfo[4])+"\n"
		at = "Attack: "+str(pInfo[1])+"\n"
		deff = "Defense: "+str(pInfo[2])+"\n"
		reg = "Regen: "+str(pInfo[3])+"\n"
		loc = "Location: "+str(rooms[pInfo[-1]])+"\n"
		
		hh = pInfo[0]
		h = "Health: "+str(hh)+"\n"
		s = "Status: ALIVE\n"
		if hh <= 0:
			s = "Status: DEAD\n"
		aa = pInfo[5]
		a = "Started: YES\n"
		if aa == False:
			a = "Started: NO\n"
		if room == "" or str(pInfo[-1]) == str(room):
			toSend += n+d+at+deff+reg+s+loc+h+a
	
	if monst:
		monsList = monsters[room]
		for mons in monsList:
			if mons != [""] and mons[2] > 0:
				n = "Name:  "+str(mons[0])+"\n"
				d = "Description: "+str(mons[1])+"\n"
				a = "Attack: "+str(mons[2])+"\n"
				deff = "Defense: "+str(mons[3])+"\n"
				r = "Regen: "+str(mons[4])+"\nMonster\n"
				h = "Health: "+str(mons[6])+"\n"
				mInfo = n+d+a+deff+r+h
				toSend += mInfo

	
	soc.send(toSend.encode())
	
def Battle(userName):
	status = ""
	global users
	global monsters
	userInfo = users[userName]
	battleRoom = userInfo[-1]
	battleMonsters = monsters[battleRoom]
	userHealth = userInfo[0]
	userAttck = userInfo[1]
	userDefns = userInfo[2]
	userRegen = userInfo[3]
	if battleMonsters != [[""]]:
		for monz in range(len(battleMonsters)):
			if status != "PLAYER DIED":
				monzHealth = battleMonsters[monz][6]
				monzAttck = battleMonsters[monz][2]
				monzDefns = battleMonsters[monz][3]
				monzRegen = battleMonsters[monz][4]
				if monzDefns < userAttck:
					monzHealth -= userAttck-monzDefns
				else:
					monzHealth -= userAttck%10
				if monzHealth > 0:
					monzHealth += monzRegen%10
				else:
					status += "NOTIF "+battleMonsters[monz][0]+" Killed"
				if userDefns <monzAttck:
					userHealth -= monzAttck-userDefns
				if userHealth > 0:
					userHealth += userRegen%10
					status += "NOTIF Health "+str(userHealth)
				else:
					status = "PLAYER DIED"
				
				battleMonsters[monz][-1]= monzHealth
				#GOD MODEEEEEE
				#battleMonsters[monz][-1] = 0
				#userHealth = 100
		monsters[battleRoom] = battleMonsters
		userInfo[0] = userHealth
		users[userName] = userInfo

	return status
		
		
def makeRoomInfo(userName,soc,toMove = ""):
	global users
	userInfo = users[userName]
	currentRoom = userInfo[-1]
	if toMove == "FIGHT":
		newRoom = currentRoom
	elif currentRoom == 0 and toMove == "":
		newRoom = 0
	elif currentRoom == 0 and toMove == "Hall":
		newRoom = 1
	elif currentRoom == 9 and toMove == "Narrow Hallway":
		newRoom = 8
	else:
		viableConnections = connections[currentRoom].split("|")
		numberOfConn = len(viableConnections)
		if toMove == viableConnections[0]:
			newRoom = currentRoom- 1
		elif numberOfConn == 2 and toMove == viableConnections[1]:
			newRoom =currentRoom+ 1
		else:
			soc.send("REJEC No Connection".encode())
			return
		
	userInfo[-1] = newRoom
	users[userName] = userInfo
	if toMove != "FIGHT":
		soc.send("RESLT Enter No Gold".encode())
	toSend = "Name: "+str(rooms[newRoom])+"\n"
	toSend += "Description: "+str(roomDesc[newRoom])+"\n"
	canMove = connections[newRoom].split("|")
	for each in canMove:
		toSend += "Connection:  "+str(each)+"\n"
	

	for each in monsters[newRoom]:
		if each != [""]:
			toSend += "Monster:  "+str(each[0])+"\n"
	sizeTest = "INFOM "+str(int(getsizeof(toSend.encode())))
	soc.send(sizeTest.encode())
	soc.send(toSend.encode())
	getPlayers(soc,newRoom,True)
	
def deal_with_client(cs, caddr):
	global users
	global PlayerandSocs
	userName = ""
	health = 100
	attack = 0
	defense = 0
	regen = 0
	descr = ""
	started = False
	roomNum = -1
	while True:
		try:
			recieve = cs.recv(1000000000).decode()
			header = recieve[:5]
			message = recieve [6:]
			if header == "CNNCT":
				userName = message
				if userName in activePlayers:
					cs.send("REJEC Name Already Taken".encode())
				else:
					activePlayers.append(userName)
					PlayerandSocs.append((userName,cs))
					if userName in users:
						temp = users[userName]
						health = temp[0]
						attack = temp[1]
						defense = temp[2]
						regen = temp[3]
						descr = temp[4]
						started = temp[5]
						roomNum = temp[6]
						if health <= 0:
							cs.send("REJEC Dead Without Health".encode())
						else:
							cs.send("ACEPT Reprising Player".encode())
					else:
						users[userName] = [100,0,0,0,"",False,-1]
						cs.send("ACEPT New Player".encode())
			elif header == "ATTCK":
				if not started:
					try:
						newAtck = int(message)
						if newAtck + defense + regen <= 100:
							attack = newAtck
							users[userName] = [health,attack,defense,regen,descr,started]
							cs.send("ACEPT Fine".encode())
						else:
							cs.send("REJEC Stats Too High".encode())
					except:
						cs.send("REJEC Incorrect State".encode())
				else:
					cs.send("REJEC Incorrect State".encode())
			elif header == "DEFNS":
				if not started:
					try:
						newDef = int(message)
						if newDef + attack + regen <= 100:
							defense = newDef
							users[userName] = [health,attack,defense,regen,descr,started]
							cs.send("ACEPT Fine".encode())
						else:
							cs.send("REJEC Stats Too High".encode())
					except:
						cs.send("REJEC Incorrect State".encode())
				else:
					cs.send("REJEC Incorrect State".encode())
			elif header == "REGEN":
				if not started:
					try:
						newReg = int(message)
						if newReg + attack + defense <= 100:
							regen = newReg
							users[userName] = [health,attack,defense,regen,descr,started]
							cs.send("ACEPT Fine".encode())
						else:
							cs.send("REJEC Stats Too High".encode())
					except:
						cs.send("REJEC Incorrect State".encode())
				else:
					cs.send("REJEC Incorrect State".encode())
						
			elif header == "DESCR":
				if not started:
					descr = str(message)
					users[userName] = [health,attack,defense,regen,descr,started]
					cs.send("ACEPT Fine".encode())
				else:
					cs.send("REJEC Incorrect State".encode())

			elif header == "LEAVE":
				activeSocs.remove(cs)
				PlayerandSocs.remove((userName,cs))
				if userName in activePlayers:
					activePlayers.remove(userName)
				cs.send("ACEPT Fine".encode())
				cs.close()
				break
				
			elif header == "QUERY":
				toSend = gameDescr
				cs.send(toSend.encode())
				getPlayers(cs)

			elif header == "START":
				if not started:
					started = True
					if roomNum == -1:
						users[userName] = [health,attack,defense,regen,descr,started,0]
					else:
						users[userName] = [health,attack,defense,regen,descr,started,roomNum]
					cs.send("RESLT Game Started".encode())
					makeRoomInfo(userName,cs)
					
			elif header == "ACTON":
				if started:
					actHeader = message[:5]
					actMessage = message[6:]
					if actHeader == "CHROM":
						makeRoomInfo(userName,cs,actMessage)
					
					if actHeader == "FIGHT":
						rezzz = Battle(userName)
						makeRoomInfo(userName,cs,"FIGHT")
						if "PLAYER DIED" == rezzz:
							activeSocs.remove(cs)
							PlayerandSocs.remove((userName,cs))
							if userName in activePlayers:
								activePlayers.remove(userName)
							cs.send("NOTIF DEATH".encode())
							started = False
							break
						else:
							cs.send(rezzz.encode())
							
					
					if actHeader == "MESSG":
						if "MSG2A" == actMessage[:5]:
							toSend = "MESSG "+userName+"Yelled> "+actMessage[6:]
							for soccc in activeSocs:
								if soccc != cs:
									soccc.send(toSend.encode())
							cs.send("ACEPT Fine".encode())
						elif "DELET" == actMessage[:5]:
							nameToDelete = actMessage[6:]
							if nameToDelete in activePlayers:
								cs.send("REJEC Player Is Active".encode())
							else:
								try:
									userInfo = users[nameToDelete]
									del users[nameToDelete]
									for each in PlayerandSocs:
										if each[0] == nameToDelete:
											PlayerandSocs.remove(each)
									cs.send("ACEPT Player Deleted".encode())
								except:
									cs.send("REJEC Not A Valid Player".encode())
						else:
							toMessage = actMessage.split(" ")[0]
							messagee = "MESSG "+userName+": "+actMessage[len(toMessage):]
							for p in PlayerandSocs:
								if p[0] == toMessage:
									p[1].send(messagee.encode())
								
				else:
					cs.send("REJEC Incorrect State".encode())
					
		except Exception as ex:
			global ss
			print("Exception\n"+str(ex))
			cs.close()
			ss.close()
			break

print("Server Active\n%s : %s\n"%(server,port))
start_new_thread(updateMonsters,())
while run:
	try:
		cs, caddr = ss.accept()
		activeSocs.append(cs)
		start_new_thread(deal_with_client, (cs, caddr))
	except:
		ss.close()
		break