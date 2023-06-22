import os
import threading
import shutil

import modules.sftp.sftp_tools as sftp_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil

from CVSMS.models import  Files,storageNodeInfo



    

class thread_get(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        file_list = serverDButil.getFileMD(self.obj.FID)
        
        #GET THE CWD OF THE FILE
        cwd = os.path.dirname(self.obj.file.path)
        
  
        storageNode = None
        
        #LOOP THROUGH ALL THE FILES AND GET THE STORAGE NODE
        for fileMD in file_list:
            # print(fileMD["RAIDid"])
            if fileMD["RAIDid"] != -1:
                
                #Added temp variable to verify if atleast one storage node is alive
                temp = serverDButil.getStorageNode(fileMD["SID"])
                
                if temp:
                    storageNode = temp
                    break
            
            else:
                print("SKIPPED 1st ENTRY") 
        
        
        
        if not storageNode:
            print("NO NODES ARE ALIVE")
            shutil.rmtree(cwd)
        else:
            message = {
            "fName": fileMD["fName"],
            "FID" : fileMD["FID"],
            "command" : "download",
            "size": fileMD["actualSize"],
            "start": fileMD["start"],
            "cwd" : cwd
            }
                    
            #CONDITION CHECKER FOR SFTP IF SUCCESSFUL
            success = True
            
            try:
                #CHECK IF FILE IS IN CACHE
                sftp_tools.get(message, storageNode)
                
            except Exception as e:
                print(f"ERROR: {e}")
                success = False

            if not success:
                #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
                shutil.rmtree(cwd)
        
            
class thread_unraid(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj
    
    
    
    def run(self):
        fileMD = serverDButil.getFileMD(self.obj.FID)
        fileLocations = [] 
        
        #GET ALL THE STORAGE NODES ASSOCIATED WITH THE FILE
        for i in fileMD:
            if i["RAIDid"] != -1:
                fileLocations.append(serverDButil.getStorageNode(i["SID"]))
        
        
        
        storageNode = fileLocations[0]
        
        #FIND THE SID OF THE STORAGE NODE THAT HAS THE LARGER CAPACITY
        for i in fileLocations:
           if storageNode["maxSize"] < i["maxSize"]:
               storageNode = i
        
        newSID = storageNode["SID"] 
        
        #LOCATE THE START OF THE NEW FILE MD THAT CONTAINS THE NEW SID
        for i in fileMD:
            if i["SID"] == newSID:
                start = i["start"]
        
        
        #print(start)
        

        
        #CREATE THE NEW UNRAIDED FILE ENTRY
        serverDButil.delMD(self.obj.FID)
        
        Files.objects.create(
        owner = self.obj.owner, 
        fName = self.obj.fName,
        file = self.obj.file,
        actualSize = self.obj.actualSize,
        FID = self.obj.FID,
        start = start["start"],
        isCached = False,
        SID = newSID)
        
        shutil.rmtree(os.path.dirname(self.obj.file.path))
        
        
            
        
        
