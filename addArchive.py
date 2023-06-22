import sqlite3
import modules.archive.fileMod as file_module
#import serverDButil
# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30
def storageRegister(data): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeInfo VALUES (?,?,?,?,?,?,?,?)",(None,
                                                                          data["SID"],
                                                                          data["allocSize"],
                                                                          data["storageIp"],
                                                                          data["storagePort"],
                                                                          data["allocSize"],
                                                                          True, 
                                                                          data["SFTPport"]))
    conn.commit()
    print(f'{data["SID"]} - {data["storageIp"]} inserted at table')
    conn.close()
    




where = "pbkdf2_sha256$390000$tYx5oCl3x4NRh8j08QTF6q$vL+0WQkwYKjNt5lSTkqTM8Co0ZFAOUCOCqL6yZkXbuI="

renjipw = "pbkdf2_sha256$390000$QOG8BE2aqxzYcImxnV6tXv$WszepFpOWQ9+cZucWW6EADm/TjpnmL7sv/UmVQbiuE0="




import sqlite3



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



storageNodeUploadList = [
                {        
                    "SID":"Storage-1",
                    "allocSize":1*GB,
                    "MaxSize": 1*GB,
                    "storageIp":"192.168.0.213",
                    "storagePort":5004,
                    "online":True
                },
                {        
                    "SID":"Storage-2",
                    "allocSize":1*GB,
                    "MaxSize": 1*GB,
                    "storageIp":"192.168.0.213",
                    "storagePort":5003,
                    "online":True
                },
                {        
                    "SID":"Storage-3",
                    "allocSize":1*GB,
                    "MaxSize": 1*GB,
                    "storageIp":"192.168.0.213",
                    "storagePort":5002,
                    "online":True
                },
            ]   



import modules.sqlite3.serverDButil as serverDButil


def create_archive():

    size = 1*GB
    try:
        data = {        
                        "SID":"ARCHIVE",
                        "allocSize":size,
                        "MaxSize": size,
                        "storageIp":"N/A",
                        "storagePort":0,
                        "online":True,
                        "SFTPport":0
        }
        
        file_module.CreateAlloc(size)
        
        storageRegister(data)
        print("ARCHIVE STORAGE SUCCESSFULLY CREATED")
    except Exception as e:
        print(e)
  


#ADD SUPERUSER USERNAME:renji PW:renji
#add_superUser()


#size = int(input("ENTER ARCHIVE SIZE"))
create_archive()
