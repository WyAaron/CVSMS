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
        messageToNode= {
            "fName": fName,
            "FID" : fID,
            "command" : message["command"],
            "cwd" : message["cwd"]
            }
        
        #SEND COMMAND TO STORAGE NODE
        messageToNode = json.dumps(messageToNode)
        messageToNode = messageToNode.encode()    
        s.sendall(messageToNode)
        
            
        print("Storage Node is downloading...")
        
        #WAIT FOR STORAGE NODE TO FINISH DOWNLOADING
        data = s.recv(1024)
        data = data.decode()
        #DELETE FILE AFTER STORAGE NODE FINISH DOWNLOADING
        if data:
            data = json.loads(data)
            serverDButil.updateMaxSize(data["maxSize"], storageNode["SID"])
            serverDButil.updateFileStartMD(data["start"], fID)
            print("Storage Node successful download")
            
            #os.remove(os.path.join(message["cwd"],fName))

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


def delete(message,storageNode, isRaid = False):
    host = storageNode["IP"]
    port = storageNode["port"]
    
    fID = message["FID"]
    
    #CONNECT TO STORAGE NODE
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
        s.connect((host,port))
        
        #GENERATE COMMAND MESSAGE FOR STORAGE NODE 
        message = {
                "FID" : fID,
                "command" : message["command"],
                }
        message = json.dumps(message)
        message = message.encode()    
        s.sendall(message)
        
        print("Storage Node is Deleteing")
        
        #WAIT FOR STORAGE NODE's REPLY THAT IT IS DONE UPLOADING
        data = s.recv(1024)
        data = data.decode()
        
        #ONCE STORAGE NODE IS DONE UPLOADING 
        #INFORM USER THAT UPLOADING IS DONE AND FILE THE CAN BE DOWNLOADED
        if data:
            data = json.loads(data)
            if not isRaid:
                serverDButil.delMD([fID])
            print(fID)
            serverDButil.updateMaxSize(data["maxSize"], storageNode["SID"])
            print("Storage Node successful delete")
        else:
            print("ERROR FROM STORANGE NODE UPLOAD")

