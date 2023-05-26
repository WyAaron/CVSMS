import sqlite3
#import serverDButil
# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30
def storageRegister(data): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeInfo VALUES (?,?,?,?,?,?,?)",(None,data["SID"],data["allocSize"],data["storageIp"],data["storagePort"],data["allocSize"],True))
    conn.commit()
    print(f'{data["SID"]} - {data["storageIp"]} inserted at table')
    conn.close()
    





# def getStorageNodes():
# 	conn = sqlite3.connect('db.sqlite3')
# 	c = conn.cursor()

# 	c.execute("SELECT * FROM CVSMS_storageNodeInfo")
# 	items = c.fetchall()

# 	columnName = [description[0] for description in c.description]

# 	keyValue = []

# 	for item in items:
# 		data = {}

# 		for i in range(len(columnName)):
# 			data[columnName[i]] = item[i]
# 		keyValue.append(data)
	
# 	conn.close()
# 	return keyValue
where = "pbkdf2_sha256$390000$tYx5oCl3x4NRh8j08QTF6q$vL+0WQkwYKjNt5lSTkqTM8Co0ZFAOUCOCqL6yZkXbuI="

renjipw = "pbkdf2_sha256$390000$QOG8BE2aqxzYcImxnV6tXv$WszepFpOWQ9+cZucWW6EADm/TjpnmL7sv/UmVQbiuE0="




import sqlite3

# def edit_entry_id(new_id, old_id):

#     conn = sqlite3.connect("db.sqlite3")  
#     cursor = conn.cursor()
#     query = "UPDATE auth_user SET password = ? WHERE username = ?"
#     cursor.execute(query, (new_id, old_id))

#     # Commit the changes and close the connection
#     conn.commit()
#     conn.close()

# # Usage example
# edit_entry_id(where,"aaron" )  # Edit entry with old ID 5 and set new ID as 10

values = "(1, 'pbkdf2_sha256$390000$QOG8BE2aqxzYcImxnV6tXv$WszepFpOWQ9+cZucWW6EADm/TjpnmL7sv/UmVQbiuE0=', '2023-03-23 05:39:47.825409', 1, 'renji', '', '', 1, 1, '2023-03-14 06:52:22.084104', '')"
columns = "('id', 'password', 'last_login', 'is_superuser', 'username', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'first_name')"

def add_superUser():
    # Connect to the database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Execute the query
    query = f"INSERT INTO auth_user {columns} VALUES {values}"
    cursor.execute(query)

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()


# add_entry_to_table()


# def getAllMDfromDB():
    
#     conn = sqlite3.connect('db.sqlite3')
#     c = conn.cursor()

#     c.execute("SELECT * FROM CVSMS_files")
#     items = c.fetchall()

#     columnName = [description[0] for description in c.description]

#     keyValue = []

#     for item in items:
#         data = {}

#         for i in range(len(columnName)):
#             data[columnName[i]] = item[i]
#         keyValue.append(data)

#     conn.close()
#     return keyValue


# def getCurrentFileStorageNodes(FID):
#     fileList = serverDButil.searchMD([FID])
    
#     storageSIDlist = []
    
#     for i in fileList:
#         storageSIDlist.append(i["SID"])
    
#     return storageSIDlist


# entry = 147

# db = "SERVER.sqlite3"
# # print(serverDButil.getStorageNode(["Storage-1"]))
# def getStorageNode(SID):
# 	conn = sqlite3.connect(db)
# 	c = conn.cursor()
# 	c.execute("SELECT * FROM CVSMS_storagenodeinfo WHERE SID = (?)", SID)
# 	items = c.fetchall()
 
# 	columnName = [description[0] for description in c.description]

# 	keyValue = []

# 	for item in items:
# 		data = {}

# 		for i in range(len(columnName)):
# 			data[columnName[i]] = item[i]
# 		keyValue.append(data)
  
# 	conn.commit()
# 	conn.close()
	
# 	print(f"key {keyValue}")
 
# 	return keyValue[0]

# getStorageNode(["Storage-2"])

# import math

# val = 52428799  

# MB = 2 ** 20
# print( math.ceil(val/25*MB%2) )

# possibleParts = set([0, 1, "p"])
# parts = set ([0,1])


# print(list(possibleParts - parts )[0])


storageNodeUploadList = [
                {        
                    "SID":"Storage-1",
                    "allocSize":1*GB,
                    "MaxSize": 1*GB,
                    "storageIp":"192.168.100.59",
                    "storagePort":5004,
                    "online":True
                }
                # {        
                #     "SID":"Storage-2",
                #     "allocSize":1*GB,
                #     "MaxSize": 1*GB,
                #     "storageIp":"192.168.0.146",
                #     "storagePort":5004,
                #     "online":False
                # },
            ]   

##### UNCOMMENT TO ADD STORAGE NODES
for i in storageNodeUploadList:
    storageRegister(i)


# def delete(IP): 
#     conn = sqlite3.connect("db.sqlite3")
#     c = conn.cursor()
#     c.execute("DELETE FROM CVSMS_storageNodeInfo WHERE IP = ?", (IP,))
#     conn.commit()
#     conn.close()
# delete("192.168.0.146")

#ADD SUPERUSER USERNAME:renji PW:renji
add_superUser()