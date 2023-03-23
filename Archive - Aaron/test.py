import threading 
import time 
import json
import socket
from datetime import datetime


def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # getting the current time
    return current_time
        

def StorageConnection(conn,addr):
    while True:
        msg = "success"
        data = conn.recv(1024)
        dataFromClient = json.loads(data.decode())
        if dataFromClient["command"] == "Register": 
            #----------------- INSERT DB CALL REGISTER-------###### 
            print(f"Comming from: {addr} @ {getCurrTime()} \n ")
            print(f'User Connected: {dataFromClient["SID"]}')
            conn.sendall(msg.encode())
            # db(IP,POrt,SID,ALLOC,Registered)
            print(f"Sent ACK to {addr} ")
            conn.close()    
        
        elif dataFromClient["command"] == "Heartbeat":
                print(f'message:{dataFromClient["message"]} @{getCurrTime()}')
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