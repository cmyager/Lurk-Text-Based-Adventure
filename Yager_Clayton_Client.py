#!/usr/bin/env python3
import re
from socket import *
from _thread import start_new_thread
from sys import exit
from time import sleep
from unicurses import *
command = ""
CONNECTED = False
STARTED = False
URL = gethostname()
PORT = int(open("port","r").read())
connection = socket(AF_INET, SOCK_STREAM)
connection.connect((URL,PORT))
connection.settimeout(0.5)
ACTIONS = ["CHROM","FIGHT","MESSG"]
EXTS = []
DEAD = False
def update():
	box(inputWindow)
	update_panels()
	doupdate()
	
def send(toSend):
	connection.send(toSend.encode())
	
def recieveData():
	totalInput = ""
	while True:
		try:
			x = connection.recv(1000000000).decode()
			totalInput += x
		except:
			break
	return totalInput

def createNewPlayer():
	writeOutput("Player Must Select Stats")
	attack = ["Attack",0,"ATTCK"]
	defense = ["Defense",0,"DEFNS"]
	regen = ["Regeneration",0,"REGEN"]
	counter = -1
	stats_ = [attack,defense,regen]
	for toUse in stats_:
		while True:
			try:
				toUse[1] = int((getInput("Enter "+toUse[0]+" Stat: ")))
			except:
				toUse[1] = -1
			if toUse[1] < 0:
				toUse[1] = 0
				writeOutput("Invalid "+toUse[0]+" stat\n")
			else:
				connection.send((str(toUse[2])+" "+str(toUse[1])).encode())
				recieved = recieveData()
				if recieved[:5] == "REJEC":
					writeOutput(str(toUse[0]+" Stat Rejected: "+recieved[6:]+"\n"))
					toUse[1] = 0
				else:
					writeOutput(str(toUse[0]+" Stat Accepted"))
					break
	while True:
		descr = str(getInput("Enter Character Description: "))
		send("DESCR "+descr)
		recieved = recieveData()
		if recieved[:5] == "REJEC":
			writeOutput("Description Rejected\n")
			toUse[1] = 0
		else:
			writeOutput(str("Description Accepted\n"))
			break

	
	   
def recieve(run = True):
	global command
	toReturn = ""
	serverMessages = ["ACEPT","REJEC","RESLT","INFOM","MESSG","NOTIF"]
	CURRENTROOM = ""
	xMount = maxX-2
	while True:
		recieved = recieveData()
		if recieved != "":
			writeOutput("*"*xMount)
			lineSplit = recieved.splitlines()
			data = recieved.split("INFOM ")
			names = recieved.split("Nam")
			for dat in range(len(data)):
				if "ACEPT" in data[dat]:
					if "ACEPT New Player" in data[dat]:
						createNewPlayer()
						toReturn = True
						data[dat] = ""
						
					if "ACEPT Reprising Player" in data[dat]:
						toReturn = True
						data[dat] = ""
			
			
			if "CHROM" in command:
				if "RESLT" in recieved:
					command = ""
					res = recieved.splitlines()
					#writeOutput(res)
					for i in res:
						if "RESLT" in i:
							e = i.split("INFOM")
							result = e[0].replace("RESLT ","")
							roomName = e[1].split("Name: ")[1]
							writeOutput("Moving to "+roomName+"\n"+"Result: "+result)
			
			
			users = []
			userCounter = 0
			for each in names:
				user_ = []
				uName = "Name: (null)"
				uDesc = "Description: (null)"
				uStat = "Status: (null)"
				uHealth = "Health: (null)"
				uGold = "Gold: (null)"
				if each[:3] == "e: ":
					u = each.splitlines()
					#writeOutput(u)
					if "Connection: " not in u[2]:
						if command != "QUERY":
							#writeOutput(u)
							if  "e: " in u[0] and u[5] != "Monster":
								uName = u[0].replace("e: ","")
								for n in u:
									if "Description: " in n:
										uDesc = n
									if "Status: " in n:
										uStat = n
									if "Health: " in n:
										uHealth = n
									if "Gold: " in n:
										uGold = n
									if "Started:  YES" in n:
										global STARTED
										STARTED = True
								user_ = ["Name: "+uName+" "+uDesc+" "+uHealth+" "+uGold+" "+uStat]
								#writeOutput(user_)
								if user_ not in users:
									users.append(user_)
					elif "e: " in u[0]:
						CURRENTROOM = u
			if users != [] and STARTED:		
				writeOutput("\nEntered Current Room")
			for userr in users:
				for info_ in userr:
					writeOutput(info_)
				
			if CURRENTROOM != "":
				room = CURRENTROOM[0].split("e: ")[1]
				desc = CURRENTROOM[1]
				conn = ""
				mons = "\nNONE"
				for each in CURRENTROOM:
					if "Connection:  " in each:	
						conn += each.replace("Connection:  ","\n")
					if "Monster:  " in each:
						if mons == "\nNONE":
							mons = "\n"
						monn = each.replace("Monster:  ","")
						for n in names:
							if monn in n and "Health: " in n:
								n = n.splitlines()
								for stat_ in n:
									if "Health: " in stat_:
										monn += " "+stat_
						
						mons += monn+"\n"
				toWrite = "\nCurrently in the "+room+"\n"+desc+"\n\nMonsters In "+room+mons+"\n\nConnecting Rooms"+conn+"\n"
				writeOutput(toWrite)
				
			if recieved[:5] == "REJEC":
				writeOutput("Error: "+recieved[6:])
			elif recieved[:5] =="MESSG":
				writeOutput("Message: "+recieved[6:])
			
			
			#######
			#fix this	
			if "MESSG" in command:
				if "ACEPT Fine" in recieved:
					writeOutput("Message Sent")
					command = ""

					
			if command == "QUERY":
				command = ""
				gameDesc = lineSplit[0].split("GameDescription: ")[1]
				exts = "\nNONE"
				findexts = recieved.split("Extensio")
				for each in findexts:
					if each[:3]== "n: ":
						if exts == "\nNONE":
							exts = ""
						exLines = each.splitlines()
						exName = exLines[0].replace("n: ","")
						exType = exLines[2]
						global EXTS
						if exName not in EXTS:
							EXTS.append(exName)
						if "ACTON" in exType:
							global ACTIONS
							if exName not in ACTIONS:
								ACTIONS.append(exName)
						exName += ": "
						exDesc = exLines [3]
						exPara = exLines [4]
						exInfo = exName+" "+exType+" "+exDesc+" "+exPara+"\n"
						exts += exInfo
				writeOutput("GAME INFO\n"+gameDesc+"\n\nSupported Extensions\n"+exts+"\n")
			

			if "FIGHT" in command:
				writeOutput("Results From Fight")
				command = ""
				for line in lineSplit:
					if "NOTIF" in line:
						lineToWrite = line.replace("NOTIF ","|")
						if lineToWrite[0] == "|":
							lineToWrite = lineToWrite[1:]
						lineToWrite = lineToWrite.replace("|","\n")
						writeOutput(lineToWrite)
						
			if "NOTIF " in recieved:
				if len(recieved.split("NOTIF ")) == 2:
					pass
					#writeOutput(recieved.replace("NOTIF ",""))
					
				if "NOTIF You were attacked" in recieved:
					for each in lineSplit:
						if "NOTIF You were attacked" in each:
							writeOutput(each.replace("NOTIF ",""))
					pass
				if "NOTIF Death" in recieved:
					writeOutput("\n\n\n\n\nYOU DIED\n\n\n\n\nPress Any Key To Exit")
					global DEAD
					DEAD = True
				
			for ext in EXTS:
				if ext in command:
					command = ""
					writeOutput(recieved.replace("NOTIF ","").replace("ACEPT ",""))
			#writeOutput(len(recieved))
			#writeOutput(lineSplit)
		if run == False:
			return toReturn
			break
			
	


def connect():
	connected = False
	while connected != True:
		wmove(inputWindow,1,1)
		userName = getInput("Enter User Name: ")
		send(("CNNCT "+userName))
		connected = recieve(False)



def writeOutput(messageToDisplay):
	wmove(outputWindow,maxY-2,1)
	waddstr(outputWindow,"\n"+str(messageToDisplay))
	update()
	    
def getInput(messageToDisplay):
	wmove(inputWindow,1,1)
	waddstr(inputWindow," "*int(maxX-2))
	update()
	wmove(inputWindow,1,1)
	waddstr(inputWindow,str((messageToDisplay)))
	c = ""
	totalInput = ""
	while True:
		if c == "\n" or c == 10:
			break
		c=wgetch(inputWindow)
		if c == 127 or c == 263:
			wmove(inputWindow,1,1)
			waddstr(inputWindow," "*int(maxX-2))
			update()
			wmove(inputWindow,1,1)
			totalInput = totalInput[:len(totalInput)-1]
			waddstr(inputWindow,messageToDisplay+totalInput)
		else:
			addstr(str(c))
			totalInput += str(chr(c))
			
	totalInput = totalInput.replace("\n","")
	if totalInput.upper() == "LEAVE":
		send("LEAVE")
		endwin()
		sys.exit()
	return totalInput

########
stdscr = initscr()
keypad(stdscr,True)
maxYX = getmaxyx(stdscr)
maxY = maxYX[0]
maxX = maxYX[1]
outputWindow = newwin(maxY-3,maxX,0,0)
scrollok(outputWindow,True)
inputWindow = newwin(3,maxX,maxY-3,0)
keypad(inputWindow,True)
box(inputWindow)
writeOutput("Welcome To Lurk")
outputpanel = new_panel(outputWindow)
inputPanel = new_panel(inputWindow)
update()
connect()

while True:
	if not STARTED:
		writeOutput("Commands\nStart : Start Game\nStats : Adjust Player Stats\nLeave : Leave Game")
		command = str(getInput("Enter Command: ")).upper()
		if command == "START":
			send("START")
			x =recieve(False)
			break
			
		elif command == "STATS":
			send("ATTCK 1")
			recieved = recieveData()
			if "Incorrect" in recieved:
				writeOutput("\nCannot Edit Stats Once The Game Has Started\nType Start To Play\n")
			else:
				createNewPlayer()

		else:
			writeOutput("\nInvalid Input\n")
	else:
		break

def main():
	global command
	global dead
	start_new_thread(recieve,())
	command = "QUERY"
	send("QUERY")

	while not DEAD:
		toCommand = str(getInput("Enter Command: "))
		if toCommand[:5] in ACTIONS:
			command = "ACTON "+toCommand
		else:
			command = toCommand
		send(command)
	endwin()

main()
