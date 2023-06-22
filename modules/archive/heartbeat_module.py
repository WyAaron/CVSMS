import os
import json
import modules.archive.fileMod as file_module
import time
import socket
import threading


KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30


def Registration(client, config):
    print(f'Status: Proceding with Registration')
    try:
        Register = {
            "SID": config["SID"],
            "allocSize": config["AllocSize"],
            "storageIp": config["storageIP"],
            "heartbeatPort": config["heartbeatPort"],
            "SFTPport": config["SFTPport"],
            "command": "Register"
        }
        Register.update()
        client.sendall(json.dumps(Register).encode())
        data = client.recv(1024)
        print(data.decode())
        # TODO: {StorageIP,storageport,allocsize,SID}
        with open(os.path.join(os.getcwd(), "Config.json"), 'w', encoding='utf-8-sig') as f:
            config["Registered"] = True
            json.dump(config, f)
            f.close()
        print(f'Status: Storage Creation')
        file_module.CreateAlloc(config["AllocSize"], "storage")
        print(f' total Size {config["AllocSize"]} bytes')
        client.close()
    except Exception as e:
        print('Status: Storage Registration Error, Please contact admin')
    
 

def Heartbeat(client, config):

    ctr = 0
    Heart = {
        "command": "Heartbeat",
        "SID": config["SID"],
        "port": config["heartbeatPort"],
        "status": True
    }
    print(f'Status: Proceding with Heartbeat to Server')
    while threading.main_thread().is_alive():
        
        try:
            
            client.sendall(json.dumps(Heart).encode())
            client.settimeout(3)
            mainrep = client.recv(1024)
            # print(f'Server:{mainrep.decode()}')
            # if mainrep.decode():
            #     time.sleep(2)
            ctr = 0
        

            
        except socket.error:
            
            ctr += 1
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((config["serverIP"], config["serverPort"]))
                client.bind((config["storageIP"], config["heartbeatPort"]))
                client.sendall(json.dumps(Heart).encode())
            except:
                print("Status: no Response from Server")
            if ctr == 5:
                client.close()
                print(
                    "Re-Status:server did not response for the alloted time, shutting down")
                exit()
        except:
            exit()
            
        time.sleep(2)
            
        
 
    exit()
    