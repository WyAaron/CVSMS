#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import multiprocessing,threading
import SerConMod
import fileMod
import storageNodeMD
# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30


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
    fileMod.CreateAlloc(1*GB,"storage")
    storageNodeMD.createMD()
    # main()
    t1 = multiprocessing.Process(target=main)
    t2 = multiprocessing.Process(target=SerConMod.main)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    
