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
        

def storageRegister(SID,allocSize,storageIp,port): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeInfo VALUES (?,?,?,?,?)",(None,SID,allocSize,storageIp,port))
    conn.commit()
    print(f'{SID} - {storageIp} inserted at table')
    conn.close()
    
def storageHeartbeat(Ip,port,status,time): 
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeStatus VALUES (?,?,?,?,?)",(None,Ip,port,status,time))
    conn.commit()
    print(f'{Ip} active @ {time} ')
    conn.close()
    pass
    

def StorageConnection(conn,addr):
    while True:
        msg = "success"
        data = conn.recv(1024)
        dataFromClient = json.loads(data.decode())
        if dataFromClient["command"] == "Register": 
            #----------------- INSERT DB CALL REGISTER-------######
            storageRegister(dataFromClient["SID"],dataFromClient["allocSize"],dataFromClient["storageIp"],dataFromClient["storagePort"]) 
            print(f'User Connected: {dataFromClient}')
            conn.sendall(msg.encode())
            # db(IP,POrt,SID,ALLOC,Registered)
            print(f"Sent ACK to {addr} ")
            conn.close()    
        
        elif dataFromClient["command"] == "Heartbeat":
            storageHeartbeat(dataFromClient["IP"],dataFromClient["port"],dataFromClient["status"],getCurrTime())
            conn.sendall(msg.encode())
            print(f'SENT ACK to {addr}   \n')
                


        else: 
        #---- Reconnection ----------- #
            print(f'{dataFromClient["SID"]} has reconnected')

def main(): 
    ctr = 1
    IP= "localhost"
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