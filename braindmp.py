import socket
import json
import time
import os
import math
import random
from datetime import datetime


# TODO: refactor code to sending a json file

with open("./config.json", 'r') as f:
    config = json.loads(f.read())

# with open("./image.jpg", "rb") as f:
#     fileTest = f.read()
    # fileSize = os.stat(fileTest).st_size


serverDetails = config["IP"], config["port"]
########################## Stormod testing grounds ##############################


bufferSize = 1024
HB = {
    "command": "Heartbeat",
    "user": "Aaron-PC"
}
reg = {
    "command": "Register",
    "user": "Aaron-PC"
}
HB2 = {
    "command": "Heartbeat",
    "user": "Aaron-PC"
}


def getCurrTime():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")  # getting the time
    return current_time


####################### Stormod ending grounds ##########################################


######################## File Modification Testing Grounds ##############################

# TODO: change IP when testing using as a client-1
# End of File Modi
IP = "192.168.100.241"
userPort = 8880
userDetails = IP, userPort
# suggestion
# UDP for establishing the configuration file & heartbeat
# TCP-IP for file trasnfer


def hearbeat():

    client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    client.bind(userDetails)
    # Testing for sending 10 heartbeats
    for each in range(10):
        try:
            client.sendto(f"{json.dumps(HB)}".encode(), serverDetails)
            print(f'Sent to Server {each} @{getCurrTime()}')
            client.settimeout(3)
            mainrep, addr = client.recvfrom(bufferSize)
            print(f'MAINREP: @{getCurrTime()}')

            # if mainrep.decode():
            #     print(f'MAINREP')
            #     time.sleep(2)
        except:
            for x in range(5):
                try:
                    client.sendto(f"{json.dumps(HB2)}".encode(), serverDetails)
                    print(f'Resending to Server {x} @{getCurrTime()}')
                    client.settimeout(3)
                    resRep, addr = client.recvfrom(bufferSize)
                    print(f'ResRep: @{getCurrTime()}')
                    time.sleep(2)
                    if resRep.decode():
                        break
                except:
                    if x == 4:
                        print('Server did not respond, shutting down!')
                        client.close()
                        exit()
                print(f'No response from server')
                time.sleep(2)

    f.close()
    client.close()


def TCPhearbeart():
    host = "192.168.43.229"
    port = 8000

    for each in range(10):
        client = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        client.connect((host, port))

        try:
            print(f'client started!')
            client.sendall(f'{json.dumps(HB)}'.encode())
            data = client.recv(bufferSize)
            client.settimeout(3)
            reply = json.loads(data.decode())
            if reply["reply"] == "alive":
                print(f'[Server]:connected @{getCurrTime()}')
                client.close()
        except socket.error:
            for x in range(5):
                print(f'Retransmitting {each}-{x}')
                client.sendall(f'{json.dumps(HB2)}'.encode())
                data = client.recv(bufferSize)
                reply = json.loads(data.decode())
                if reply["reply"] == "alive":
                    print(f'[Server]:connected @{getCurrTime()}')
                    client.close()

        time.sleep(4)
    client.close()


def main():
    TCPhearbeart()


if __name__ == "__main__":
    main()
