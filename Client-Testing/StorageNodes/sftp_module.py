import socket
import json
import os
import fileMod as file_module
import threading
import shutil
import time
import paramiko

def client_SFTP(host, port, serverName, password):

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


