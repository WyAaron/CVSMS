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
    queryset = Files.objects.all()
    
    
    for file_obj in queryset: 
        
        if os.path.isfile(os.path.join("media", str(file_obj.id), str(file_obj.fName))):
    
            file_obj.isCached = True
            file_obj.save()
        else: 
            file_obj.isCached = False
            file_obj.save()
             
    # files[i]["isCached"] = False

    