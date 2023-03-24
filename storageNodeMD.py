import sqlite3
import json

########## Create table ##########
def createMD():
	conn = sqlite3.connect('storageNodeMD.db')
	c = conn.cursor()

	c.execute("""CREATE TABLE IF NOT EXISTS snMD (
			FID INTEGER,
			fileName TEXT,
			fileSize INTEGER,
			start INTEGER
		)""")

	conn.commit()
	conn.close()


########## Add 1 entry ##########
# storageNodeMD.addSN("2","abcs.png","2500","1501")
# storageNodeMD.addSN("3","hello.mp4","5000","4000")
# storageNodeMD.addSN("4","file.txt","1000","5000")
# storageNodeMD.addSN("5","sound.mp4","3000","6000")
def addMD(FID, fileName, fileSize, start):
	conn = sqlite3.connect('storageNodeMD.db')
	c = conn.cursor()

	c.execute("INSERT INTO snMD VALUES (?,?,?,?)", (FID, fileName, fileSize, start))
	print("\nEntry added successfully\n")

	conn.commit()
	conn.close()


########## Show all content of table ##########
def showMD():
	conn = sqlite3.connect('storageNodeMD.db')
	c = conn.cursor()

	c.execute("SELECT * FROM snMD")
	items = c.fetchall()

	columnName = [description[0] for description in c.description]

	keyValue = []

	for item in items:
		data = {}

		for i in range(len(columnName)):
			data[columnName[i]] = item[i]
		keyValue.append(data)
	
	conn.close()
	return keyValue
	

########## Delete 1 entry - per FID ##########
def delMD(id):
	conn = sqlite3.connect('storageNodeMD.db')
	c = conn.cursor()

	c.execute("DELETE from snMD WHERE FID = (?)", id)

	conn.commit()
	conn.close()


########## Look up 1 entry - per FID ##########
def searchMD(id):
	conn = sqlite3.connect('storageNodeMD.db')
	c = conn.cursor()

	c.execute("SELECT * FROM snMD WHERE FID = (?)", id)
	columnName = [description[0] for description in c.description]
	items = c.fetchall()

	keyValue = []

	for item in items:
		data = {}
		for i in range(len(columnName)):
			data[columnName[i]] = item[i]
		keyValue.append(data)
	
	conn.close()
	return data