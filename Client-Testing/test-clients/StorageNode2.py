import socket
import time  
import json
from datetime import datetime
import os
# import storageNodeMD
# import fileMod

# fileMod.CreateAlloc(500*MB)
# storageNodeMD.createMD()



def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # getting the current time
    return current_time


def Registration(client,config):
    try:
        Register ={
                "SID": config["SID"], 
                "allocSize": config["AllocSize"], 
                "storageIp": config["storageIP"], 
                "storagePort":config["storagePort"],
                "command": "Register"
            }
        Register.update()
        client.sendall(json.dumps(Register).encode())
        data = client.recv(1024)
        #TODO: {StorageIP,storageport,allocsize,SID}
        with open(os.path.join(os.getcwd(),"Config2.json"), 'w', encoding='utf-8-sig') as f:
            config["Registered"] = True
            json.dump(config,f)
            f.close()
    except Exception as e: 
        print(repr(e))

def Reconnection(): 
    pass

def Heartbeat(client,config):
    ctr=0 
    Heart = {
        "command": "Heartbeat",
        "IP": "localhost", 
        "port": 7778, 
        "status": "connected",
        "SID": config["SID"]
    }
    while True:  
        try:
            client.sendall(json.dumps(Heart).encode())
            client.settimeout(3)
            mainrep = client.recv(1024)
            print(f'Server:{mainrep.decode()}')
            if mainrep.decode(): 
                time.sleep(2)
        except:
            ctr +=1
            try: 
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((config["serverIP"],config["serverPort"]))
                client.sendall(json.dumps(Heart).encode())
            except: 
                print('did not enter this zone')
            print("no Response from Server")
            if ctr == 5: 
                client.close()
                print("server no response, shutting down")
                exit()
        time.sleep(2)


def main():
    IP = "localhost"
    PORT = 7777
    bufferSize = 1024 
    with open(os.path.join(os.getcwd(),"Config2.json"), 'r', encoding='utf-8-sig') as f:
            config = json.loads(f.read())  
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client: 
        client.connect((config["serverIP"],config["serverPort"]))
        print(f'Registration status: {config["Registered"]}')
        try:
            if config["Registered"]: 
                print('registered!')
                #reconnecting()
            else:
                print(f'Registration')
                Registration(client,config)
                #---- insert heartbeat----#
                
            Heartbeat(client,config) 
                
        except Exception as e:
            print(repr(e))
    

if __name__ == '__main__': 
    main()