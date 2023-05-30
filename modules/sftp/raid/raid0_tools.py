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
        
        #GET THE CWD OF THE FILE
        cwd = os.path.dirname(self.obj.file.path)

        #CHECK IF ALL THE STORAGE NODES ARE AVAILABLE
        allAlive = True
        for fileMD in file_list:
            if fileMD["RAIDid"] != -1:
                if not serverDButil.getStorageNode(fileMD["SID"])["status"]:
                    allAlive = False
                    break
        
        if not allAlive:
            shutil.rmtree(cwd)
            print("Some Storage Nodes are Down, Cannot download all the files in this RAID")
        else:
        
        
            #LOOP THROUGH ALL THE FILES 
            for fileMD in file_list:
                # print(fileMD["RAIDid"])
                
                
                
                
                if fileMD["RAIDid"] != -1:
                    storageNode = serverDButil.getStorageNode(fileMD["SID"])
                    
                    message = {
                    "fName": fileMD["fName"],
                    "FID" : fileMD["FID"],
                    "command" : "download",
                    "cwd" : cwd
                    }
                    
                    #CONDITION CHECKER FOR SFTP IF SUCCESSFUL
                    success = True
                    
                    try:
                        #CHECK IF FILE IS IN CACHE
                        if not os.path.isfile(os.path.join(cwd, fileMD["fName"])): #condition for file DNE in server
                            print(f'file is not in cache downloading...')
                            #GET THE FILES
                            sftp_tools.get(message, storageNode)
                        else:
                            print("Part Exists")
                            
                    except Exception as e:
                        print(e)
                        print("ERROR DOWNLOADING FILES TO BE RAIDED")
                        success = False
                        
                        
                        break
                else:
                    print("SKIPPED 1st ENTRY")
                    
            if not success:
                #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
            else:
                sorted_file_list = sorted(file_list, key=lambda item: item["RAIDid"])
                fileList = [sorted_file_list[1]["fName"], sorted_file_list[2]["fName"]]
                raid_module.raid0.merge(sorted_file_list[0]["fName"], fileList, cwd)



class thread_unraid(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        file_list = serverDButil.getFileMD(self.obj.FID)
        
        #GET THE CWD OF THE FILE
        cwd = os.path.dirname(self.obj.file.path)
        
        #CHECK IF THE DIRECTORY FOR THE SFTP EXISTS
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        else:
            print("Directory Exists, Proceeding to SFTP")

        
        
        #CHECK IF ALL THE STORAGE NODES ARE AVAILABLE
        allAlive = True
        for fileMD in file_list:
            if fileMD["RAIDid"] != -1:
                if not serverDButil.getStorageNode(fileMD["SID"])["status"]:
                    allAlive = False
                    break
        
        if not allAlive:
            shutil.rmtree(cwd)
            print("Some Storage Nodes are Down, Cannot download all the files in this RAID")
        else:
            #LOOP THROUGH ALL THE FILES 
            for fileMD in file_list:
                # print(fileMD["RAIDid"])
                if fileMD["RAIDid"] != -1:
                    storageNode = serverDButil.getStorageNode(fileMD["SID"])
                    
                    message = {
                    "fName": fileMD["fName"],
                    "FID" : fileMD["FID"],
                    "command" : "download",
                    "cwd" : cwd
                    }
                    
                    #CONDITION CHECKER FOR SFTP IF SUCCESSFUL
                    success = True
                    
                    try:
                        #CHECK IF FILE IS IN CACHE
                        if not os.path.isfile(os.path.join(cwd, fileMD["fName"])): #condition for file DNE in server
                            print(f'file is not in cache downloading...')
                            #GET THE FILES
                            sftp_tools.get(message, storageNode)
                        else:
                            print("Part Exists")
                            
                    except Exception as e:
                        print(e)
                        print("ERROR DOWNLOADING FILES TO BE RAIDED")
                        success = False
                        shutil.rmtree(cwd)
                        break
                else:
                    print("SKIPPED 1st ENTRY")
                    
            if not success:
                #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
            else:
                sorted_file_list = sorted(file_list, key=lambda item: item["RAIDid"])
                fileList = [sorted_file_list[1]["fName"], sorted_file_list[2]["fName"]]
                raid_module.raid0.merge(sorted_file_list[0]["fName"], fileList, cwd)

                fName = self.obj.fName
            
                
                storageNode = NodeGetTools.get_storage_nodes([fName], cwd)
            
                if storageNode:
                    
                    message = {
                        "fName": fName,
                        "FID" : self.obj.FID,
                        "cwd" : cwd,
                        #"start" : storageNode[0]["Gap"][0],
                        "start" : 0,
                        "command":"upload"
                    }
                    
                
                    success = True
                    try: 
                        storageNode = storageNode[0]["storage_info"]
                        sftp_tools.put(message, storageNode)
                        
                    except Exception as e:
                        print(e)
                        success = False
                    
                    if not success:
                        print("SFTP of merged file failed")
                        
                    else:
                        
                        print("SFTP upload of merged file success")
                        #REMOVE OLD DATA OF FILE FROM DB
                        serverDButil.delMD(self.obj.FID)
                        
                        #ADD THE NEW UNRAIDED DATA TO DB
                        Files.objects.create(
                        owner = self.obj.owner, 
                        fName = self.obj.fName,
                        file = self.obj.file,
                        actualSize = self.obj.actualSize,
                        FID = self.obj.FID,
                        #start = storageNode[0]["Gap"][0],
                        start = 0,
                        isCached = False,
                        SID = storageNode["SID"])
                    
                    shutil.rmtree(cwd)
                    
            