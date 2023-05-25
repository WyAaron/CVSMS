import os
from CVSMS.models import  Files,storageNodeInfo

def get_storageSize():
    obj = storageNodeInfo.objects.all()
    storageSize = sum(obj.values_list('allocSize',flat=True))
    return storageSize

def get_fileTotalSize(): 
    files = Files.objects.filter(RAIDid = -1)    
    totalFileSize = sum(files.values_list('actualSize',flat=True))    
    return totalFileSize


def get_AvailabilityInCache():
    pass
    