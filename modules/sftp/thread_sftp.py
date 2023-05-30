import threading
import time
import os
import shutil


import modules.sftp.sftp_tools as sftp_tools 
import modules.sqlite3.serverDButil as serverDButil
import modules.RAIDmod as raid_module
import modules.nodeTools.getTools as get_tools
import modules.sftp.sftp_tools as sftp_tools


from CVSMS.models import  Files

class SFTPThread(threading.Thread):
    def __init__(self, message, storageNode, deleteFolder = False):
        # execute the base constructor
        threading.Thread.__init__(self)
        # store the value
        self.storageNode = storageNode
        self.message = message
        self.deleteFolder = deleteFolder
    # override the run function
    def run(self):
        # TODO: Change to SFTP function
        if self.message["command"] == "upload":
            print(self.storageNode["port"])
            sftp_tools.put(self.message, self.storageNode)
            if self.deleteFolder:
                pass
                #shutil.rmtree(self.message["cwd"])
        elif self.message["command"] == "download":
            sftp_tools.get(self.message, self.storageNode)

        else:
            print("NOT YET IMPLEMENTED")
            #delete(self.message, self.storageNode)
          
            
class standard_get(threading.Thread):
    def __init__(self,message, fName, storageNode):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.storageNode = storageNode
        self.fName = fName
        self.message = message
        
    # override the run function
    def run(self):
        threads = []
        fileParts = []
        brokenFile = False
        ctr = 0
        # for i in self.fileTuple:
            
        #     if i != "NONE":
        message = {
        "fName": self.fName,
        "FID" : self.message["FID"],
        "cwd" : self.message["cwd"],
        "command":"download"
        }
        
        get_Thread = SFTPThread(message, self.storageNode)
        get_Thread.start()
    
    
class raidPut(threading.Thread):
    def __init__(self, obj, RAIDtype):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj
        self.RAIDtype = RAIDtype    

    def run(self):
        
        cwd = os.path.dirname(self.obj.file.path)
        fName = self.obj.fName
        
        #MAKE THE DIRECTORY OF THE FILE TO BE RAIDED
    
        
        message = {
            "fName": fName,
            "FID" : self.obj.FID,
            "cwd" : cwd,
            "command":"download"
        }
        
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        
        
        
        
        success = True
        
        storageNode = serverDButil.getStorageNode(self.obj.SID)
                
        try:
            #CHECK IF FILE IS IN CACHE
            if not os.path.isfile(os.path.join(cwd, fName)): #condition for file DNE in server
                print(f'file is not in cache downloading...')
                #GET THE FILES
                sftp_tools.get(message, storageNode)
            else:
                print("Part Exists")
                
        except Exception as e:
            print(e)
            print("ERROR DOWNLOADING FILES TO BE RAIDED")
            success = False
        
    
    
    
        #CHECK IF ORIGINAL FILE UPLOAD WAS SUCCESSFUL 
        if not success:
            print("ERROR IN SFTP FROM ORIGINAL FILE UPLOAD")
        
        else:
               
            if self.RAIDtype == "0":
                partNames = raid_module.raid0.split(fName, 2, cwd)
                #raid_module.raid0.merge(fName, ["hello.txt-0","hello.txt-1"], cwd)
                
                
                print("RAID 0")
                
                    
            elif self.RAIDtype == "1":
                
                partNames = [fName, fName]
                print("RAID 1")
            elif self.RAIDtype == "PARITY":
                
                #raid_module.pRAID.split(fName, cwd)
                #raid_module.pRAID.merge(fName, ["hello.txt-0","hello.txt-1"], cwd)
                print("PARITY")
            
            
            
            
            #GET THE STORAGE NODES THAT CAN BE USED FOR FILE UPLOADING
            upload_list = get_tools.get_storage_nodes(partNames, cwd)
            
            #CHECK IF THERE IS ENOUGH STORAGE NODE
            if not upload_list:
                    print("NOT ENOUGH STORAGE")
            
            else: 
                
                #CHECK IF SFTP IS SUCCESSFUL
                success = True
                
                
                #BEING UPLOAD OF ALL THE FILE PARTS TO THEIR RESPECTIVE STORAGE NODES
                for i in upload_list:
                    message = {
                        "fName": i["fName"],
                        "FID" : self.obj.FID,
                        "cwd" : cwd,
                        #"start":i["storage_info"]["Gap"][0],
                        "command":"upload"
                    }
    
                    storageNode = i["storage_info"]
        
                    #TRY UPLOADING
                    try: 
                        sftp_tools.put(message,storageNode)
                    except Exception as e:
                        print("ERROR IN SFTP UPLOAD")
                        success = False
                        break
                        
                        
                        
                
                
                #CHECK IF THERE WAS NO ERROR IN SFTP
                if not success:
                    print("SFTP WAS NOT SUCCESSFUL")
                    
                    
                else:
                    print("HELLO SFTP WAS SUCCESSFUL FOR ALL FILES")
                    
                    
                    #REMOVE THE SID FROM THE ORIGINAL FILE
                    serverDButil.removeSID(self.obj.FID)
                    
                    #SET THE RAID TYPE FOR THE FILES 
                    serverDButil.setRAIDtype(self.RAIDtype, self.obj.FID)
                    
                    
                    
                    #RAID ID COUNTER
                    raid_id = 0
                    
                    
                    #CREATE DATABASE ENTRY FOR NEWLY UPLOADED FILES
                    for i in upload_list:
                        raid_id+=1
                        
                        #CREATE THE ENTRY
                        Files.objects.create(
                            owner=self.obj.owner, 
                            fName= i["fName"],
                            file=self.obj.file,
                            actualSize=os.path.getsize(os.path.join(cwd, i["fName"])),
                            SID = i["storage_info"]["SID"],
                            RAIDtype = self.RAIDtype,
                            RAIDid = raid_id,
                            #start = i["storage_info"]["Gap"][0],
                            start = 0,
                            FID=self.obj.FID,)

                    
                    
                    #UPDATE STORAGE NODE INFORMATION
                    for i in upload_list:
                        
                        nodeSID = i["storage_info"]["SID"]
                        #GET ALL FILES STORED IN THE STORAGE NODE
                        files_in_node = serverDButil.get_all_files_by_sid(nodeSID)
                        
                        # print(files_in_node)
                        #GET THE NEW MAXIMUM SIZE THAT CAN BE STORED ON THE STORAGE NODE
                        # print(i["storage_info"]["maxSize"])
                        
                        
                        newMaxSize = get_tools.getMaxFile(files_in_node, i["storage_info"]["allocSize"])
                        
                        # print(newMaxSize)
                        #UPDATE THE STORAGE NODE INFORMATION ON THE DATA BASE
                        #serverDButil.updateMaxSize(newMaxSize, nodeSID)
            
            

                