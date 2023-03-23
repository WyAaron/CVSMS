#######SERVER############
import socket
import threading
import time
import json
host = "localhost"
port = 1000

def StorageConnection(conn,addr):
    while True: 
        msg = "success"
        data = conn.recv(1024)
        dataFromClient = json.loads(data.decode())
        if dataFromClient["command"] == "Heartbeat":
            print(f'message:{dataFromClient["message"]} ')
            conn.sendall(msg.encode())
            print(f'SENT ACK to {addr}   \n')


def main(): 
    ctr = 1
    IP= "192.168.1.9"
    PORT= 7777
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: 
        server.bind((IP,PORT))
        server.listen()
        while True: 
            print(f'server listening on {IP}: {PORT}')
            conn, addr = server.accept()
            #---- Threading -----###
            t1 = threading.Thread(target= StorageConnection, args=(conn,addr,))# once finished fixing commands 
            t1.start()
            #---- to down place in a function ----###
                
            # t1 = threading.Thread(target=func1,args=(conn,ctr))
            # t1.start()

    

if __name__ == '__main__':
    main()