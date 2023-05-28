import threading
import time
import os
import shutil


import modules.sftp.sftp_tools as sftp_tools 
import modules.sqlite3.serverDButil as serverDButil
import modules.RAIDmod as raid_module
import modules.sftp.raid.raid0_tools as raid0_tools
import modules.sftp.sftp_tools as sftp_tools


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
    
    
class raidThread(threading.Thread):
    def __init__(self, obj, RAIDtype):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj
        self.RAIDtype = RAIDtype    

    def run(self):
        cwd = os.path.dirname(self.obj.file.path)
        fName = self.obj.fName
        
        message = {
            "fName": fName,
            "FID" : self.obj.FID,
            "cwd" : cwd,
            "command":"download"
        }
        
       
        

        #CHECK IF FILE EXISTS
        if not os.path.isfile(os.path.join(cwd,fName)): #condition for file DNE in server
            print(f'file is not in cache downloading...')
            if not os.path.exists(cwd):
                os.mkdir(cwd)
            else:
                print("Directory Exists, Proceeding to SFTP")
            # sftp_get = SFTPThread(message, storageNode)
            # sftp_get.start()
            # sftp_get.join()
            
        if self.RAIDtype == "0":
            partNames = raid_module.raid0.split(fName, 2, cwd)
            #raid_module.raid0.merge(fName, ["hello.txt-0","hello.txt-1"], cwd)
            
            upload_list = raid0_tools.get_storage_nodes(partNames, message["cwd"])
            print("RAID 0")
            if not upload_list:
                print("NOT ENOUGH STORAGE")
                
        elif self.RAIDtype == "1":
            print("RAID 1")
        elif self.RAIDtype == "PARITY":
            #RAIDmod.pRAID.split(fName, cwd)
            #raid_module.pRAID.merge(fName, ["hello.txt-0","hello.txt-1"], cwd)
            print("PARITY")
        
        
        
        
        try:  
            for i in upload_list:
                message = {
                    "fName": i["fName"],
                    "FID" : self.obj.FID,
                    "cwd" : cwd,
                    #"start":i["Gap"][0],
                    "command":"upload"
                }
                print("a")
                storageNode = i["storage_info"]
                print(storageNode)

                sftp_tools.put(message,storageNode)
                
                
                
                
        except Exception as e:
            print("ERROR IN SFTP UPLOAD")

        
        print("HELLO I WAS SUCCESSFUL")