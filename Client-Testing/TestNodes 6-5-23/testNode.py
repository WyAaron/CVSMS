

import socket
import paramiko
import json
import fileMod as file_module
import os
import shutil
import threading
import time
from datetime import datetime
import multiprocessing
# from RetrieveFile import *

# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30

thread_crashed = False

# file_module.CreateAlloc(1*GB, "storage")
# storageNodeMD.createMD()


def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # getting the current time
    return current_time


def Registration(client, config):
    print(f'entered Registration ')
    try:
        Register = {
            "SID": config["SID"],
            # Multiplying the allocated size to GB
            "allocSize": config["AllocSize"],
            "storageIp": config["storageIP"],
            "storagePort": config["storagePort"],
            "SFTPport": config["SFTPport"],
            "command": "Register"
        }
        Register.update()
        client.sendall(json.dumps(Register).encode())
        data = client.recv(1024)
        # TODO: {StorageIP,storageport,allocsize,SID}
        with open(os.path.join(os.getcwd(), "Config.json"), 'w', encoding='utf-8-sig') as f:
            config["Registered"] = True
            json.dump(config, f)
            f.close()
        print(f'Entering AllocSize creation')
        file_module.CreateAlloc(config["AllocSize"], "storage")
        print(f' total Size {config["AllocSize"] * GB}')
        client.close()
    except Exception as e:
        print(repr(e))


def Heartbeat(client, config):
    ctr = 0
    Heart = {
        "command": "Heartbeat",
        "SID": config["SID"],
        "port": config["storagePort"],
        "status": True
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
            ctr += 1
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((config["serverIP"], config["serverPort"]))
                client.bind((config["storageIP"], config["storagePort"]))

                client.sendall(json.dumps(Heart).encode())
            except:
                print('did not enter this zone')
            print("no Response from Server")
            if ctr == 5:
                client.close()
                print("server no response, shutting down")
                exit()
        time.sleep(2)


def SFTP(host, port, serverName, password):

    storFolder = "storageFolder"
    storName = "storage"
    storageLoc = os.path.join(storFolder, storName)
    # STORAGE ALLOCATION LOCATION

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # accept connection from server for an upload request
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        conn.settimeout(10)

        print('Connected by', addr)

        storFolder = "storageFolder"
        storName = "storage"
        storageLoc = os.path.join(storFolder, storName)

        # Receive server request
        data = conn.recv(1024)

        message = json.loads(data.decode())
        command = message["command"]

        if command == "download":
            print("SERVER HAS INITIATED DOWNLOAD")

            if not os.path.exists(str(message["FID"])):
                os.mkdir(str(message["FID"]))
            # USER REQURIES A DOWNLOAD
            try:
                def fileStorage():
                    try:

                        global thread_crashed
                        thread_crashed = False

                        # IMPLEMENT FILE MOD

                        file_module.retFile(message, storageLoc)
                        print("FINISHED FILE RETRIEVAL PROCEEDING TO SFTP")

                    except Exception as e:
                        print(e)
                        if os.path.exists(str(message["FID"])):
                            shutil.rmtree(str(message["FID"]))
                            thread_crashed = True

                # START FILE RETIREVAL THREAD
                file_mod_thread = threading.Thread(target=fileStorage)
                file_mod_thread.start()

                while file_mod_thread.is_alive():
                    time.sleep(1)
                    messageUp = str("retrieving").encode()
                    conn.sendall(messageUp)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                # CHECK IF FILE MODULE CRASHED
                    if thread_crashed:
                        messageUp = str("fail").encode()
                        print(messageUp)
                        conn.sendall(messageUp)

                        # CONFIRM THAT SERVER MESSAGE RECEIVED
                        try:
                            data = conn.recv(1024).decode()
                            if data != "recvd":
                                raise Exception("SERVER FAILED")
                        except:
                            raise Exception("SERVER DID NOT REPLY")

                        raise Exception("FILE MODULE FAILED")

                # START SFTP UPLOAD

                def SFTP():
                    try:
                        global thread_crashed
                        thread_crashed = False
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(
                            paramiko.AutoAddPolicy())
                        ssh.connect(
                            hostname=addr[0], username=serverName, password=password, port=22)
                        # CONNECT TO SERVER
                        with ssh.open_sftp() as sftp_client:
                            sftp_client.chdir(message["cwd"])
                            # UPLOAD TO SERVER
                            sftp_client.put(os.path.join(
                                str(message["FID"]), message["fName"]), message["fName"])
                        ssh.close()
                    except Exception as e:
                        print(e)
                        thread_crashed = True

                # START SFTP THREAD
                sftp_thread = threading.Thread(target=SFTP)
                sftp_thread.start()

                # HEARTBEAT WHILE SFTP IS ONGOING
                while sftp_thread.is_alive():
                    time.sleep(1)
                    messageUp = str("uploading").encode()
                    conn.sendall(messageUp)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                # CHECK IF SFTP THREAD CRASHED AND EXIT IF IT DID
                if thread_crashed:
                    endMessage = str("fail").encode()
                    print(endMessage)
                    conn.sendall(endMessage)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                    raise Exception("SFTP FAILED")

                # SEND SUCCESS MESSAGE
                endMessage = str("done").encode()
                print(endMessage)
                conn.sendall(endMessage)

                # CONFIRM THAT SERVER MESSAGE RECEIVED
                try:
                    data = conn.recv(1024).decode()
                    if data != "recvd":
                        raise Exception("SERVER FAILED")
                except:
                    raise Exception("SERVER DID NOT REPLY")

                shutil.rmtree(str(message["FID"]))

            except Exception as e:
                print(e)
                if os.path.exists(str(message["FID"])):
                    shutil.rmtree(str(message["FID"]))
            # SEND UPDATED DB
            # conn.sendall(b"ok")
            # os.remove(fName)
            # shutil.rmtree(str(message["FID"]))

        elif command == "upload":

            print("SERVER HAS INITIATED UPLOAD")

            if not os.path.exists(str(message["FID"])):
                os.mkdir(str(message["FID"]))

            try:
                def SFTP():
                    try:
                        global thread_crashed
                        thread_crashed = False
                        # exit()
                        with paramiko.SSHClient() as ssh:
                            ssh.set_missing_host_key_policy(
                                paramiko.AutoAddPolicy())
                            ssh.connect(
                                hostname=addr[0], username=serverName, password=password, port=22)
                            # CONNECT TO SERVER
                            with ssh.open_sftp() as sftp_client:
                                sftp_client.chdir(message["cwd"])
                                # DOWNLOAD FROM SERVER
                                sftp_client.get(message["fName"], os.path.join(
                                    str(message["FID"]), message["fName"]))
                            # ssh.close()
                        # time.sleep(2) #SIMULATE LONG DOWNLOAD TIME
                    except Exception as e:
                        print(e)
                        thread_crashed = True

                # START SFTP THREAD
                sftp_thread = threading.Thread(target=SFTP)
                sftp_thread.start()

                # HEARTBEAT WHILE SFTP IS ONGOING
                while sftp_thread.is_alive():
                    time.sleep(1)
                    messageUp = str("downloading").encode()
                    conn.sendall(messageUp)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                # CHECK IF SFTP THREAD CRASHED AND EXIT IF IT DID
                if thread_crashed:
                    endMessage = str("fail").encode()
                    print(endMessage)
                    conn.sendall(endMessage)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                    raise Exception("SFTP FAILED")

                def fileStorage():
                    try:
                        global thread_crashed
                        thread_crashed = False

                        # IMPLEMENT FILE MOD

                        file_module.storeFile(
                            message["fName"], message["FID"], message["start"], storageLoc)

                        # REMOVE FILE AFTER STORING
                        shutil.rmtree(str(message["FID"]))

                    except Exception as e:
                        print(e)
                        shutil.rmtree(str(message["FID"]))
                        thread_crashed = True

                # START FILE STORAGE THREAD
                file_mod_thread = threading.Thread(target=fileStorage)
                file_mod_thread.start()

                # CHECK IF FILE MODULE IS STILL ALIVE
                while file_mod_thread.is_alive():
                    time.sleep(1)
                    messageUp = str("storing").encode()
                    conn.sendall(messageUp)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                # CHECK IF FILE MODULE CRASHED
                if thread_crashed:
                    messageUp = str("fail").encode()
                    print(messageUp)
                    conn.sendall(messageUp)

                    # CONFIRM THAT SERVER MESSAGE RECEIVED
                    try:
                        data = conn.recv(1024).decode()
                        if data != "recvd":
                            raise Exception("SERVER FAILED")
                    except:
                        raise Exception("SERVER DID NOT REPLY")

                    raise Exception("FILE MODULE FAILED")

                # SEND SUCCESS MESSAGE
                endMessage = str("done").encode()
                print(endMessage)
                conn.sendall(endMessage)

                # CONFIRM THAT SERVER MESSAGE RECEIVED
                try:
                    data = conn.recv(1024).decode()
                    if data != "recvd":
                        raise Exception("SERVER FAILED")
                except:
                    raise Exception("SERVER DID NOT REPLY")

                # create Lock release
                # shutil.rmtree(str(message["FID"]))
            except Exception as e:
                print(e)
                if os.path.exists(str(message["FID"])):
                    shutil.rmtree(str(message["FID"]))


def main():
    with open(os.path.join(os.getcwd(), "Config.json"), 'r', encoding='utf-8-sig') as f:
        config = json.loads(f.read())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.bind((config["storageIP"], config["storagePort"]))
        print(f'serverIP, port = {config["serverIP"],config["serverPort"]}')
        client.connect((config["serverIP"], config["serverPort"]))

    while True:
        print(f'Registration status: {config["Registered"]}')
        try:
            if config["Registered"]:
                print('registered!')
                # reconnecting()
            else:
                print(f'{type(config["AllocSize"])}')
                Registration(client, config)
                # ---- insert heartbeat----#

                p1 = multiprocessing.Process(
                    target=Heartbeat, args=(client, config,))
                p1.start()

                p2 = multiprocessing.Process(target=SFTP, args=(
                    config["storageIP"], config["SFTPport"], config["username"], config["password"]))
                p2.start()

                p1.join()
                p2.join()
        except Exception as e:
            print(repr(e))


if __name__ == "__main__":
    main()
