
# import paramiko
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# ubuntuIP = "192.168.0.213"
# windowsIP = "192.168.0.225"
# ssh.connect(hostname=windowsIP, username="Sandbox", password="password", port=22)

# with ssh.open_sftp() as sftp_client:



    
#     fileName = "test.txt"
    
#     receivedFile = "received.txt"
#     #ubuntu
#     #sftp_client.get('/home/ssh/scp/'+fileName, receivedFile)

    
#     #windows
#     #sftp_client.get('C:/Users/Sandbox/Desktop/fold/'+fileName, receivedFile)
#     # sftp_client.chdir('C:/Users/Sandbox/Desktop/fold/')
#     # print(sftp_client.getcwd())
#     # sftp_client.get(fileName, receivedFile)
#     sftp_client.chdir('C:/Users/Renji/Desktop/Python Tests/Thesis/Server')
    
#     sftp_client.put("hello.txt", "upload.txt")
    
    
# ssh.close()

import socket
import paramiko
import json
import fileMod
import os
import storageNodeMD
import shutil
import threading
#from RetrieveFile import *

# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30


# fileMod.CreateAlloc(1*GB,"storage")
# storageNodeMD.createMD()


def main(host, port, serverName, password):
    
    storFolder = "storageFolder"
    storName = "storage"
    storageLoc = os.path.join(storFolder, storName)
    #STORAGE ALLOCATION LOCATION
    
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #accept connection from server for an upload request
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        
        print('Connected by', addr)
        
        storFolder = "storageFolder"
        storName = "storage"
        storageLoc = os.path.join(storFolder, storName)
        
        #Receive server request
        data = conn.recv(1024)
        
        message = json.loads(data.decode())
        command = message["command"]
        
        print(message)
        
        if command == "download":
            
            if not os.path.exists(str(message["FID"])):
                os.mkdir(str(message["FID"]))
            #USER REQURIES A DOWNLOAD
                        
            #GET FILE FROM STORAGE ALLOCATION
            #fileMD = storageNodeMD.searchMD([message["FID"]])
            #fileMod.retFile(fileMD, storageLoc)
            
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=addr[0], username=serverName, password=password, port=22)
            #CONNECT TO SERVER
            with ssh.open_sftp() as sftp_client:
                sftp_client.chdir(message["cwd"])
                #UPLOAD TO SERVER
                sftp_client.put( os.path.join(str(message["FID"]),message["fName"]), message["fName"])
            ssh.close()
            
            #SEND UPDATED DB
            conn.sendall(b"ok")
            #os.remove(fName)
            #shutil.rmtree(str(message["FID"]))   
            
            
            
        elif command == "upload":
            if not os.path.exists(str(message["FID"])):
                os.mkdir(str(message["FID"]))
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=addr[0], username=serverName, password="password", port=22)
            #CONNECT TO SERVER
            with ssh.open_sftp() as sftp_client:
                sftp_client.chdir(message["cwd"])
                #DOWNLOAD FROM SERVER
                sftp_client.get(message["fName"], os.path.join(str(message["FID"]),message["fName"]))
            ssh.close()
            
            
            
            #create Lock get
            
            #enter DATABASE MODIFICATION
            
            # fileSize = os.path.getsize(os.path.join(str(message["FID"]), message["fName"]))
            # mdList = storageNodeMD.showMD()
            # start = fileMod.getStartLocation(mdList, fileSize, os.path.getsize(storageLoc))
            # newMD = fileMod.storeFile(message["fName"], message["FID"], start, storageLoc)
            # storageNodeMD.addMD(newMD["FID"], newMD["fileName"], newMD["fileSize"], newMD["start"])
            
            #LOOK FOR THE SMALLEST AVAILABLE LOCATION THAT CAN FIT THE FILE
            
            #SEND UPDATED DB
            mdList = storageNodeMD.showMD()
            maxSize = fileMod.getMaxFile(mdList, os.path.getsize(storageLoc))
            
            messageUp = {
                "start": 1,#start,
                "maxSize": 10000000#maxSize
            }
            print(f"out: {messageUp}")
            messageUp = json.dumps(messageUp).encode()
            print(messageUp)
            conn.sendall(messageUp)
            
            #create Lock release
            #shutil.rmtree(str(message["FID"]))   
            
            
        elif command == "delete":
            #INSERT DATABASE DELETION
            storageNodeMD.delMD([message["FID"]])
            #SEND UPDATED DB
            mdList = storageNodeMD.showMD()
            maxSize = fileMod.getMaxFile(mdList, os.path.getsize(storageLoc))
            
            messageOut = {
                "maxSize": maxSize,
            }
            
            
            messageOut = bytes(json.dumps(messageOut), 'utf-8')
            
            conn.sendall("messageOut")
        
if __name__ == "__main__":
    host = "192.168.100.69"
    port = 5004
    serverName = "aaron"
    password = "aaron"
    while True:
        try:
            main(host, port, serverName, password)
        except Exception as e:
            print(e)