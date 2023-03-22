import json
import os
from datetime import datetime
import time
import socket
JSONtest = {
    "IP": "192.168.100.240",
    "port": 8000,
    "SID": "Aaron-PC",
    "AllocSize": 1024, 
    "Registered": False
    
}


def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # getting the current time
    return current_time


def Registration(config):
    date = getCurrTime()
    config.update({"time":date})
    try:
        # client.sendall(json.dumps(config).encode())
        # data = client.recv(1024)
        
        with open(os.path.join(os.getcwd(),"test-Config-client.json"), 'w', encoding='utf-8-sig') as f:
            print(config)
            config["Registered"] = True
            del config["command"]
            json.dump(config,f)
            
            
    except Exception as e: 
        print(repr(e))
    
    
def Heartbeat(client,config):
    HB = { 
        "command": "Heartbeat",
        "message": "Connected"
    }
    HB2 = {
        "command": "Heartbeat",
        "message": "[RES]Tzuyu is still connected"
    }
    
    date = getCurrTime()
    HB.update({"time":date})
    ctr=0 
    while True:  
        try:
            client.sendall(json.dumps(HB).encode())
            client.settimeout(3)
            mainrep = client.recv(1024)
            print(f'Server:{mainrep.decode()}')
            if mainrep.decode(): 
                time.sleep(5)
        except:
            ctr +=1
            try: 
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # client.bind(config["StorageIP"],config['storageport'])
                client.connect((config["IP"],config["serverport"]))
                client.sendall(json.dumps(HB).encode())
                
                
                
            except: 
                pass
            print("no Response from Server")
            if ctr == 5: 
                client.close()
                print("server no response, shutting down")
                exit()
        time.sleep(5)


    
    

    
def main(): 
    IP = "localhost"
    bufferSize = 1024 
    HB =False
    with open("./test-Config-Client.json", 'r', encoding='utf-8-sig') as f:
            config = json.loads(f.read())  
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client: 
        # client.bind((config["StorageIP"],config["Storageport"]))
        client.connect((config["StorageIP"],config["Serverport"]))
        
        
        Heartbeat(client,config)
    
if __name__ == '__main__':
    main()