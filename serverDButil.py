import sqlite3

########## Add 1 entry ##########
def addMD(item):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cur ()

	c.execute("SELECT id FROM CVSMS_files ORDER BY id DESC LIMIT 1")
	result = int(c.fetchone()[0]) + 1
	print(result)
	
	FID = item['FID']
	fileName = item['fileName']
	owner = item['owner']
	RAIDid = item['RAIDid']
	RAIDtype = item['RAIDtype']
	SID = item['SID']
	actualSize = item['actualSize']
	start = item['start']
	file = item['file']

	c.execute("INSERT INTO CVSMS_files VALUES (?,?,?,?,?,?,?,?,?,?)", (result,FID, fileName, owner, RAIDid, RAIDtype, SID, actualSize, start, file))
	print("\nEntry added successfully\n")

	conn.commit()
	conn.close()


########## Look up 1 entry - per FID ##########
def searchMD(id):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("SELECT * FROM CVSMS_files WHERE FID = (?)", id)
	columnName = [description[0] for description in c.description]
	items = c.fetchall()

	keyValue = []

	for item in items:
		data = {}
		for i in range(len(columnName)):
			data[columnName[i]] = item[i]
		keyValue.append(data)
	
	conn.close()
	return keyValue


########## Edit entry - per FID ##########
def editMDraid(id, RAIDtype):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("UPDATE CVSMS_files SET RAIDtype = ? WHERE FID = ?", (RAIDtype, id))
	print("\nEntry updated successfully\n")

	conn.commit()
	conn.close()


########## Edit entry - storage Node ##########
def removeStorageNodeFromFileMD(id):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("UPDATE CVSMS_files SET SID = ? WHERE FID = ?", ("NONE", id))
	print("\nEntry updated successfully\n")

	conn.commit()
	conn.close()



########## Edit entry - storage Node ##########
def addStorageNode(SID, id):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("UPDATE CVSMS_files SET SID = ? WHERE FID = ?", (SID, id))
	print("\nEntry updated successfully\n")

	conn.commit()
	conn.close()


def updateMaxSize(maxSize, SID):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("UPDATE CVSMS_storagenodeinfo SET maxSize = ? WHERE SID = ?",(maxSize, SID))
    conn.commit()
    conn.close()

def updateFileStartMD(start, FID):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("UPDATE CVSMS_files SET start = ? WHERE FID = ?",(start, FID))
    conn.commit()
    conn.close()


########## Delete entry - per FID ##########
def delMD(id):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("DELETE from CVSMS_files WHERE FID = (?)", id)

	conn.commit()
	conn.close()

def getAllStorageNodes():
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("SELECT * FROM CVSMS_storagenodeinfo")
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

def getStorageNode(SID):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()
	c.execute("SELECT * FROM CVSMS_storagenodeinfo WHERE SID = (?)", SID)
	items = c.fetchall()
 
	columnName = [description[0] for description in c.description]

	keyValue = []

	for item in items:
		data = {}

		for i in range(len(columnName)):
			data[columnName[i]] = item[i]
		keyValue.append(data)
  
	conn.commit()
	conn.close()
	return keyValue[0]