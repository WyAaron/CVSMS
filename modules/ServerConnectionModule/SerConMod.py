import threading
import time
import json
import socket
import sqlite3
from datetime import datetime
from manage import stop_threads


def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # getting the current time
    return current_time


def storageRegister(data):
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()  # {}
    c.execute("INSERT INTO CVSMS_storageNodeInfo VALUES (?,?,?,?,?,?,?,?)", (None,
              data["SID"], data["allocSize"], data["storageIp"], data["heartbeatPort"], data["allocSize"], True, data['SFTPport']))
    conn.commit()
    print(f'{data["SID"]} - {data["storageIp"]} inserted at table')
    conn.close()


def updateMaxSize(storageNode):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("UPDATE CVSMS_storagenodeinfo SET maxSize = ? WHERE SID = ?",
              (storageNode["maxSize"], storageNode["SID"]))
    conn.commit()
    conn.close()


def storageHeartbeat(data):
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("INSERT INTO CVSMS_storageNodeStatus VALUES (?,?,?,?,?)",
              (None, data["SID"], data["port"], data["status"], getCurrTime()))
    conn.commit()
    # print(f'{data["SID"]} active @ {getCurrTime()} ')
    conn.close()


def storageStatus(SID, status):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute(
        "UPDATE CVSMS_storagenodeinfo SET status = ? WHERE SID = ?", (status, SID))
    # print(f'{SID} - offline')
    conn.commit()
    conn.close()


def StorageConnection(conn, addr):

    # data = conn.recv(1024)
    # # print(data)
    # dataFromClient = json.loads(data.decode())

    while True:

        try:
            msg = "connected @ " + getCurrTime()
            data = conn.recv(1024)
            # print(data.decode())
            dataFromClient = json.loads(data.decode())
            # print(f'command: {dataFromClient["command"]}')
            if dataFromClient["command"] == "Register":
                print(f'Entered Registration in DB')
                # ----------------- INSERT DB CALL REGISTER-------######
                storageRegister(dataFromClient)
                print(f'User Connected: {dataFromClient}')
                conn.sendall(msg.encode())
                # db(IP,POrt,SID,ALLOC,Registered)
                print(f"Sent ACK to {addr} ")

            elif dataFromClient["command"] == "Heartbeat":
                # print(f'Client Alive - {dataFromClient["SID"] } {addr}')
                storageHeartbeat(dataFromClient)
                storageStatus(dataFromClient["SID"], True)
                conn.sendall(msg.encode())
                # print(f'ACK {dataFromClient["SID"] } {addr}   \n')
                # time.sleep(5)
            # ---- Reconnection -----------
            SID = dataFromClient["SID"]
        except Exception as e:
            storageStatus(SID, False)
            print(f'------Storage Node {SID} Has Disconnected---------')
            break


def main():
    IP = "172.16.2.142"
    PORT = 5000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((IP, PORT))
        server.listen()
        while True:
            try:
                print(f'server listening on {PORT}')
                conn, addr = server.accept()
                print(f'Server Success')
                # ---- Threading -----###
                t1 = threading.Thread(target=StorageConnection, args=(
                    conn, addr,))  # once finished fixing commands
                t1.start()
            except:
                print(f'ERROR SerConMod did not start')


if __name__ == '__main__':
    main()
