import sqlite3
def storageRegister(data): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeInfo VALUES (?,?,?,?,?,?,?)",(None,data["SID"],data["allocSize"],data["storageIp"],data["storagePort"],data["allocSize"],True))
    conn.commit()
    print(f'{data["SID"]} - {data["storageIp"]} inserted at table')
    conn.close()
    
def delete(): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("DELETE FROM CVSMS_storageNodeInfo",)
    conn.commit()
    conn.close()

storageNodeUploadList = [
                {        
                    "SID":"Storage-1",
                    "allocSize":1000,
                    "MaxSize": 1000,
                    "storageIp":"192.168.0.225",
                    "storagePort":5002,
                    "online":True
                },
                {        
                    "SID":"Storage-2",
                    "allocSize":1000,
                    "MaxSize": 1000,
                    "storageIp":"192.168.0.225",
                    "storagePort":5003,
                    "online":True
                },
                {        
                    "SID":"Storage-3",
                    "allocSize":1000,
                    "MaxSize": 1000,
                    "storageIp":"192.168.0.225",
                    "storagePort":5004,
                    "online":True
                }
            ]   

def getStorageNodes():
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("SELECT * FROM CVSMS_storageNodeInfo")
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

print(type(getStorageNodes()))