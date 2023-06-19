import socket
import json
import os
import threading
import heartbeat_module
import sftp_module

# from RetrieveFile import *

# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30

thread_crashed = False

# file_module.CreateAlloc(1*GB, "storage")
# storageNodeMD.createMD()


def sftp_thread(config):
    #WHILE MAIN THREAD IS ALIVE KEEP WAITING FOR SFTP
    while threading.main_thread().is_alive():
        sftp_module.client_SFTP(config["storageIP"], config["SFTPport"], config["username"], config["password"])
    
    
# def heartbeat_thread(config):
def main():
    
        with open(os.path.join(os.getcwd(), "Config.json"), 'r', encoding='utf-8-sig') as f:
            config = json.loads(f.read())
        
        sftp = threading.Thread(target=sftp_thread, args = (config,))
        sftp.start()    
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.bind((config["storageIP"], config["heartbeatPort"]))
            print(f'serverIP, port = {config["serverIP"],config["serverPort"]}')
            client.connect((config["serverIP"], config["serverPort"]))
            
            try:
                if config["Registered"]:
                    print(f'Status: Registered, Reconnecting with the Server')
                    p1 = threading.Thread(
                        target=heartbeat_module.Heartbeat, args=(client, config,))
                    p1.start()
                    p1.join()
                    
                else:
                    print(f'Status: Not Registered')
                    heartbeat_module.Registration(client, config)
                    # ---- insert heartbeat----#

                    p1 = threading.Thread(
                        target=heartbeat_module.Heartbeat, args=(client, config,))
                    p1.start()
                    p1.join()
                    
            except Exception as e:
                print("Status: Error with Registration/Reconnection contact admin")

        


if __name__ == "__main__":
    main()
