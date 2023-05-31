import socket
import os
import json
import shutil
import threading
import modules.sqlite3.serverDButil as serverDButil
import time


def put(message,storageNode):
    host = storageNode["IP"]
    port = storageNode["port"]
    
    fName = message["fName"]
    fID = message["FID"]

    #CONNECTING TO STORAGE NODE
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
        s.connect((host,port))
        
        #GENERATE COMMAND MESSAGE FOR STORAGE NODE 
        messageToNode= message
        
        #SEND COMMAND TO STORAGE NODE
        messageToNode = json.dumps(messageToNode)
        messageToNode = messageToNode.encode()    
        s.sendall(messageToNode)
        
            
        print("Storage Node is downloading...")
        s.settimeout(10)
        
        
        
        #STORAGE NODE HEARTBEAT
        while True:
            
            data = s.recv(1024)
            data = data.decode()
            
            
            #DELETE FILE AFTER STORAGE NODE FINISH DOWNLOADING
            if data == "done":
                print("Storage Node Successful Download")
                
                message = str("recvd").encode()
                s.sendall(message)
                break
            
            elif data == "downloading":
                print("Storage Node is Still downloading...")
                message = str("recvd").encode()
                s.sendall(message)
            
            elif data == "storing":
                print("Storage node is writing file in storage node...")    
                message = str("recvd").encode()
                s.sendall(message)
                
            else:
                message = str("recvd").encode()
                print(message)
                s.sendall(message)
                raise Exception("FAILED UPLOAD")
            
            
            

            
        print("SFTP OPERATION FINISHED")
            
            
def get(message,storageNode):
    host = storageNode["IP"]
    port = storageNode["port"]
    
    fName = message["fName"]
    fID = message["FID"]
    
    #CONNECT TO STORAGE NODE
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
        s.connect((host,port))
        
        #GENERATE COMMAND MESSAGE FOR STORAGE NODE 
        message = {
                "fName": fName,
                "FID" : fID,
                "command" : message["command"],
                "cwd" : message["cwd"]
                }
        message = json.dumps(message)
        message = message.encode()    
        s.sendall(message)
        
        print("Storage Node is Uploading to server...")
        
        #WAIT FOR STORAGE NODE's REPLY THAT IT IS DONE UPLOADING
        data = s.recv(1024)
        
        
        #ONCE STORAGE NODE IS DONE UPLOADING 
        #INFORM USER THAT UPLOADING IS DONE AND FILE THE CAN BE DOWNLOADED
        if data.decode() == "ok":
            print("Storage Node successful upload")
            
                
        else:
            print("ERROR FROM STORANGE NODE UPLOAD")

