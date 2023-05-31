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
                print("Storage Node is downloading...")
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
    
    #CONNECT TO STORAGE NODE
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
        s.connect((host,port))
        
        #GENERATE COMMAND MESSAGE FOR STORAGE NODE 
  
        message = json.dumps(message)
        message = message.encode()    
        s.sendall(message)
        
        
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
            
            elif data == "uploading":
                print("Storage Node is uploading...")
                message = str("recvd").encode()
                s.sendall(message)
            
            elif data == "retrieving":
                print("Storage node is retrieving file from storage node...")    
                message = str("recvd").encode()
                s.sendall(message)
                
            else:
                message = str("recvd").encode()
                print(message)
                s.sendall(message)
                raise Exception("FAILED UPLOAD")
            
            
        print("SFTP OPERATION FINISHED")
        
        
        
  

