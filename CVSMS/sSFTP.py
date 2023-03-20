

# -----------------SFTP INSTRUCTION--------------- DO NOT DELETE
# import paramiko
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# ubuntuIP = "192.168.0.213"
# windowsIP = "192.168.0.225"
# ssh.connect(hostname=windowsIP, username="Sandbox", password="password", port=22)

# with ssh.open_sftp() as sftp_client:


#     fileName = "test.txt"

#     receivedFile = "received.txt"
#     #ubuntu
#     #sftp_client.get('/home/ssh/scp/'+fileName, receivedFile)


#     #windows
#     #sftp_client.get('C:/Users/Sandbox/Desktop/fold/'+fileName, receivedFile)
#     sftp_client.chdir('C:/Users/Sandbox/Desktop/fold/')
#     # print(sftp_client.getcwd())
#     # sftp_client.get(fileName, receivedFile)

#     sftp_client.put("hello.txt", "upload.txt")


# ssh.close()
# ---------------------------------------------------------------------------


import socket
import os
import json
import paramiko


def upload(message, storageNode):
    host = "192.168.0.209"
    port = 5001
    fName = message["fName"]

    # TODO CREATE A DBMS FUNCTION TO STORE THE FILE METADATA RECIEVED

    if data.decode() == "ok":

        # CONNECTING TO STORAGE NODE
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
            s.connect((host, port))

            # GENERATE COMMAND MESSAGE FOR STORAGE NODE
            message = {
                "fName": fName,
                "FID": 1,
                "command": message["command"],
                "cwd": os.getcwd()
            }

            message = json.dumps(message)
            message = message.encode()
            s.sendall(message)

            print("Storage Node is downloading...")

            # WAIT FOR STORAGE NODE TO FINISH DOWNLOADING
            data = s.recv(1024)
            user.sendall(b"ok")

            # DELETE FILE AFTER STORAGE NODE FINISH DOWNLOADING
            if data.decode() == "ok":
                print("Storage Node successful download")
                user.sendall(b"ok")
                os.remove(fName)


def download(user, message):
    host = "192.168.0.209"
    port = 5001
    fName = message["fName"]

    # CONNECT TO STORAGE NODE
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
        s.connect((host, port))

        # GENERATE COMMAND MESSAGE FOR STORAGE NODE
        message = {
            "fName": fName,
            "FID": 1,
            "command": message["command"],
            "cwd": os.getcwd()
        }
        message = json.dumps(message)
        message = message.encode()
        s.sendall(message)

        print("Storage Node is Uploading to server...")

        # WAIT FOR STORAGE NODE's REPLY THAT IT IS DONE UPLOADING
        data = s.recv(1024)

        # ONCE STORAGE NODE IS DONE UPLOADING
        # INFORM USER THAT UPLOADING IS DONE AND FILE THE CAN BE DOWNLOADED
        if data.decode() == "ok":
            print("Storage Node successful upload")

            # GENERATE STATUS MESSAGE FOR USER
            message = {
                "fName": fName,
                "status": "done",
                "cwd": os.getcwd()
            }

            message = json.dumps(message)
            message = message.encode()
            user.sendall(message)

            print("User is now downloading...")

            # WAIT FOR USER TO SEND AN ACK THAT THEY ARE DONE DOWNLOADING
            data = user.recv(1024)

            print("User finished downloading deleteing files from local storage...")
            os.remove(fName)


def main():
    host = "192.168.0.213"
    port = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((host, port))
    s.listen(1)
    user, addr = s.accept()
    print('Connected by', addr)

    try:
        data = user.recv(1024)

        print("Client Says: " + data.decode())

        # RECEIVE COMMAND FROM CLIENT
        message = json.loads(data.decode())
        fName = message["fName"]
        command = message["command"]

        # ACKNOWLEDGE CLIENT INTENT
        user.sendall(b"ok")

        if command == "download":
            download(user, message)

        elif command == "upload":
            upload(user, message)

        else:
            print("Server Error")
            s.close()

    except socket.error:
        print("Error Occured.")
        s.close()
    s.close()


if __name__ == "__main__":
    main()
