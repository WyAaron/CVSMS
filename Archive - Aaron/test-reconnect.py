###########CLIENT####################

import socket
import time
import json


def heartbeat(client):
    ctr=0 
    Heart = {
        "command": "Heartbeat",
        "message": "PC"
    }
    print("Hello")
    
    
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
                client.connect(("localhost",7777))
                client.sendall(json.dumps(Heart).encode())
                # print(f'client Socket = {client.connect(("localhost",7777))}')
                # print(f'Test{client.connect(config["StorageIP"],config["Serverport"])}')
                # client.bind(config["StorageIP"],config['storageport'])
                
                
                
            except: 
                print('did not enter this zone')
            print("no Response from Server")
            if ctr == 5: 
                client.close()
                print("server no response, shutting down")
                exit()
        time.sleep(2)
        
def main(): 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost",7777))
    heartbeat(client)

if __name__ == "__main__": 
    main()