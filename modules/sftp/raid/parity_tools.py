import os
import threading
import shutil

import modules.sftp.sftp_tools as sftp_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as raid_module
import modules.sqlite3.serverDButil as serverDButil

from CVSMS.models import  Files,storageNodeInfo



class thread_get(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        file_list = serverDButil.getFileMD(self.obj.FID)
        #SORT FILE LIST BY NAME
        file_list = sorted(file_list, key=lambda x: x['fName'])

       
        #GET THE CWD OF THE FILE
        cwd = os.path.dirname(self.obj.file.path)
        
        
        
        fileMD_nodeList_tuple = []
        
        #GET THE STORAGE NODE 

        for fileMD in file_list:
            if fileMD["RAIDid"] != -1:
                node = serverDButil.getStorageNode(fileMD["SID"])
                if node["status"]:
                    fileMD_nodeList_tuple.append({"fileMD":fileMD, "node":node}) 
               
                    
        if len(fileMD_nodeList_tuple) < 2:
            shutil.rmtree(cwd)
            print("Not enough storage nodes are up, Cannot download all the files in this RAID")
        elif len(fileMD_nodeList_tuple) < 3:
            print("Some nodes are missing attempting to download and repair the files...")
            
            for i in fileMD_nodeList_tuple:
                
                fileMD = i["fileMD"]
                storageNode = i["node"]
                message = {
                    "fName": fileMD["fName"],
                    "FID" : fileMD["FID"],
                    "size": fileMD["actualSize"],
                    "start" : fileMD["start"],
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
                
                
            if not success:
            #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
            else:
                fileList = [fileMD_nodeList_tuple[0]["fileMD"]["fName"], fileMD_nodeList_tuple[1]["fileMD"]["fName"]]
                print(fileList)
                raid_module.pRAID.repair(self.obj.fName, fileList, cwd)
                
                
                fileList = [f"{self.obj.fName}-0",f"{self.obj.fName}-1"]
                raid_module.pRAID.merge(self.obj.fName, fileList, cwd)
      
            
        else:
            
            
            for i in range(len(fileMD_nodeList_tuple)-1):
                
                fileMD = fileMD_nodeList_tuple[i]["fileMD"]
                storageNode = fileMD_nodeList_tuple[i]["node"]
                
                message = {
                    "fName": fileMD["fName"],
                    "FID" : fileMD["FID"],
                    "size": fileMD["actualSize"],
                    "start": fileMD["start"],
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
                
                
            if not success:
            #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
            else:
                fileList = [fileMD_nodeList_tuple[0]["fileMD"]["fName"], fileMD_nodeList_tuple[1]["fileMD"]["fName"]]
                raid_module.pRAID.merge(self.obj.fName, fileList, cwd)
            
        

class thread_unraid(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        file_list = serverDButil.getFileMD(self.obj.FID)
        #SORT FILE LIST BY NAME
        file_list = sorted(file_list, key=lambda x: x['fName'])

       
        #GET THE CWD OF THE FILE
        cwd = os.path.dirname(self.obj.file.path)
        
        
        
        fileMD_nodeList_tuple = []
        
        #GET THE STORAGE NODE 

        for fileMD in file_list:
            if fileMD["RAIDid"] != -1:
                node = serverDButil.getStorageNode(fileMD["SID"])
                if node["status"]:
                    fileMD_nodeList_tuple.append({"fileMD":fileMD, "node":node}) 
               
                    
        if len(fileMD_nodeList_tuple) < 2:
            shutil.rmtree(cwd)
            print("Not enough storage nodes are up, Cannot download all the files in this RAID")
        elif len(fileMD_nodeList_tuple) < 3:
            print("Some nodes are missing attempting to download and repair the files...")
            
            for i in fileMD_nodeList_tuple:
                
                fileMD = i["fileMD"]
                storageNode = i["node"]
                message = {
                    "fName": fileMD["fName"],
                    "FID" : fileMD["FID"],
                    "size": fileMD["actualSize"],
                    "start": fileMD["start"],
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
                
                
            if not success:
            #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
            else:
                fileList = [fileMD_nodeList_tuple[0]["fileMD"]["fName"], fileMD_nodeList_tuple[1]["fileMD"]["fName"]]
                print(fileList)
                raid_module.pRAID.repair(self.obj.fName, fileList, cwd)
                
                
                fileList = [f"{self.obj.fName}-0",f"{self.obj.fName}-1"]
                raid_module.pRAID.merge(self.obj.fName, fileList, cwd)
      
            
        else:
            
            
            for i in range(len(fileMD_nodeList_tuple)-1):
                
                fileMD = fileMD_nodeList_tuple[i]["fileMD"]
                storageNode = fileMD_nodeList_tuple[i]["node"]
                
                message = {
                    "fName": fileMD["fName"],
                    "FID" : fileMD["FID"],
                    "size": fileMD["actualSize"],
                    "start": fileMD["start"],
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
                
                
            if not success:
            #SORT THE FILES BY RAID ID
                print("ERROR IN SFTP")
            else:
                fileList = [fileMD_nodeList_tuple[0]["fileMD"]["fName"], fileMD_nodeList_tuple[1]["fileMD"]["fName"]]
                raid_module.pRAID.merge(self.obj.fName, fileList, cwd)
        
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