import os
import threading
import shutil

import json

import modules.sftp.sftp_tools as sftp_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as raid_module
import modules.sqlite3.serverDButil as serverDButil
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as raid_module



from CVSMS.models import  Files,storageNodeInfo



    
    
class thread_get(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        file_list = serverDButil.getFileMD(self.obj.FID)
        
        
        for fileMD in file_list:
            # print(fileMD["RAIDid"])
            if fileMD["RAIDid"] != -1:
                storageNode = serverDButil.getStorageNode(fileMD["SID"])
                
                cwd = os.path.dirname(self.obj.file.path)
                
                message = {
                "fName": fileMD["fName"],
                "FID" : fileMD["FID"],
                "command" : "download",
                "cwd" : cwd
                }
                
                
                #CHECK IF FILE EXISTS

                if not os.path.isfile(os.path.join(cwd, fileMD["fName"])): #condition for file DNE in server
                    print(f'file is not in cache downloading...')
                    if not os.path.exists(cwd):
                        os.mkdir(cwd)
                    else:
                        print("Directory Exists, Proceeding to SFTP")
                
                    #GET THE FILES
                    sftp_tools.get(message, storageNode)
            else:
                print("SKIPPED 1st ENTRY")
                
                
        sorted_file_list = sorted(file_list, key=lambda item: item["RAIDid"])
        if self.obj.RAIDtype == "0":
            fileList = [sorted_file_list[1]["fName"], sorted_file_list[2]["fName"]]
            
            raid_module.raid0.merge(sorted_file_list[0]["fName"], fileList, cwd)
            pass
        
        elif self.obj.RAIDtype == "1":
            pass
        
        elif self.obj.RAIDtype == "PARITY":
            pass
        
        
        
        pass