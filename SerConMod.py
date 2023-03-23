import threading 
import time 
import json
import socket
import sqlite3
from datetime import datetime


def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # getting the current time
    return current_time


def storageRegister(data): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeInfo VALUES (?,?,?,?,?,?,?)",(None,data["SID"],data["allocSize"],data["storageIp"],data["storagePort"],data["allocSize"],True))
    conn.commit()
    print(f'{data["SID"]} - {data["storageIp"]} inserted at table')
    conn.close()

def updateMaxSize(storageNode):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("UPDATE CVSMS_storagenodeinfo SET maxSize = ? WHERE SID = ?",(storageNode["maxSize"], storageNode["SID"]))
    print(f'{SID} - offline')
    conn.commit()
    conn.close()


def storageHeartbeat(data): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeStatus VALUES (?,?,?,?,?)",(None,data["SID"],data["port"],data["status"],getCurrTime()))
    conn.commit()
    print(f'{data["SID"]} active @ {getCurrTime()} ')
    conn.close()
    

def storageStatus(SID,status): 
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("UPDATE CVSMS_storagenodeinfo SET status = ? WHERE SID = ?",(status,SID))
    print(f'{SID} - offline')
    conn.commit()
    conn.close()

def StorageConnection(conn,addr):
    
    while True:
        try:
            msg = "success"
            data = conn.recv(1024)
            dataFromClient = json.loads(data.decode())
            if dataFromClient["command"] == "Register": 
                #----------------- INSERT DB CALL REGISTER-------######
                storageRegister(dataFromClient) 
                print(f'User Connected: {dataFromClient}')
                conn.sendall(msg.encode())
                # db(IP,POrt,SID,ALLOC,Registered)
                print(f"Sent ACK to {addr} ")
                conn.close()    
            
            elif dataFromClient["command"] == "Heartbeat":
                storageHeartbeat(dataFromClient)
                storageStatus(dataFromClient["SID"],True)
                conn.sendall(msg.encode())
                print(f' ACK {dataFromClient["SID"] } {addr}   \n')
            #---- Reconnection ----------- 
        except Exception as e:
            print(f'data from SID- {dataFromClient["SID"]}')
            storageStatus(dataFromClient["SID"],False) 
            print(repr(e))
            break
def main(): 
    ctr = 1
    IP= "192.168.1.9"
    PORT= 7777
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: 
        server.bind((IP,PORT))
        server.listen()
        while True: 
            print(f'server listening on {PORT}')
            conn, addr = server.accept()
            #---- Threading -----###
            t1 = threading.Thread(target= StorageConnection, args=(conn,addr,))# once finished fixing commands 
            t1.start()


    

if __name__ == '__main__':
    main()