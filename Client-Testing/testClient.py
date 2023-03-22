import socket
import time
import json
HOST = "192.168.1.9"
PORT = 5555


with open("./test-Config-Client.json", 'r', encoding='utf-8-sig') as f:
    config = json.loads(f.read())
    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST,PORT))
    while True: 
        file = json.dumps(config)
        client.send(bytes(file, encoding='utf-8'))
        data = client.recv(1024)
    
        print(f"Received {data!r}")
        time.sleep(2)