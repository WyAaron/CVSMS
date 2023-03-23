#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import multiprocessing
import socket
import time
import json
import SerConMod




def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trydjango.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def runserver():
    IP = "192.168.1.9"
    PORT = 5555 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: 
        server.bind((IP,PORT))
        server.listen()
        print(f'server Listening on {PORT}')
        conn, addr = server.accept()
        with conn:
            print(f'Connected by {addr}')
            while True: 
                data = conn.recv(1024)
                print(f'{data}')
                if not data:
                    break 
                conn.sendall(data)




if __name__ == '__main__':
    # main()
    t2 = multiprocessing.Process(target=SerConMod.main)
    t1 = multiprocessing.Process(target=main)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    
