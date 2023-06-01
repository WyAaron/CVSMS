#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import multiprocessing,threading
from modules.ServerConnectionModule import SerConMod
import subprocess

def find_process_id_by_port(port):
    # Find the process ID (PID) associated with the port
    cmd = f"lsof -i :{port} -t"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        pid = int(output.decode().strip())
        return pid
    else:
        return None

def terminate_process_by_pid(pid):
    # Terminate the process using the PID
    cmd = f"kill {pid}"
    subprocess.run(cmd, shell=True)


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






if __name__ == '__main__':
    
    main()
    # t1 = multiprocessing.Process(target=main)
    # t1.start()
    
    # t2 = multiprocessing.Process(target=SerConMod.main)
    # t2.start()

    # t1.join()
    # t2.join()
    
    
