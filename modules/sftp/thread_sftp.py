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

class SFTPThread():
    def __init__(self, message, storageNode, isArchive = False):
        
        # store the value

        self.storageNode = storageNode
        self.message = message
        self.isArchive = isArchive
        
        self.success = True
        
    # override the run function
    def run(self):
        
        #UPLOAD COMMAND
        if self.message["command"] == "upload":
            try:
                sftp_tools.put(self.message, self.storageNode)

            #CHECK IF THERE ARE ANY ERRORS IN THE FILE UPLOAD
            except Exception as e:
                print(e)
                print("ERROR IN FILE UPLOAD")
                
                #DELETE FILE METADATA IF IT IS NOT AN ARCHIVED FILE
                if not self.isArchive:
                    serverDButil.delMD(self.message["FID"])
                    self.success = False
                    
                else:
                    self.success = False

            #REMOVE FILE FROM LOCAL STORAGE AFTER DOWNLOAD
            shutil.rmtree(self.message["cwd"])
        
        #DOWNLOAD COMMAND
        elif self.message["command"] == "download":
            sftp_tools.get(self.message, self.storageNode)

            
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
        # message = {
        # "fName": self.fName,
        # "FID" : self.message["FID"],
        # "cwd" : self.message["cwd"],
        # "command":"download"
        # }
        
        SFTP = SFTPThread(self.message, self.storageNode)
        SFTP.run()
        
    
    
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
    
        
        
        
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        
        
        
        
        success = True
        
        storageNode = serverDButil.getStorageNode(self.obj.SID)
        
        message = {
            "fName": fName,
            "FID" : self.obj.FID,
            "cwd" : cwd,
            "start" : self.obj.start,
            "size" : self.obj.actualSize,
            "command":"download"
        }     
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
                
                partNames = raid_module.pRAID.split(fName, cwd)
                #raid_module.pRAID.merge(fName, ["hello.txt-0","hello.txt-1"], cwd)
                print("PARITY")
            
            
            
            
            #GET THE STORAGE NODES THAT CAN BE USED FOR FILE UPLOADING
            upload_list = get_tools.get_storage_nodes(partNames, cwd)
  
            #CHECK IF THERE IS ENOUGH STORAGE NODE
            if not upload_list:
                print("NOT ENOUGH STORAGE")
                shutil.rmtree(cwd)
            
            
            
            
            else: 
                
                #CHECK IF SFTP IS SUCCESSFUL
                success = True
                
                
                time.sleep(1)
                #BEING UPLOAD OF ALL THE FILE PARTS TO THEIR RESPECTIVE STORAGE NODES
                for i in upload_list:
                    start = i["storage_info"]["Gap"][0]
                    storageNode = i["storage_info"]["storageNode"]
                    
                    
                    message = {
                        "fName": i["fName"],
                        "FID" : self.obj.FID,
                        "cwd" : cwd,
                        "start" : start,
                        "command":"upload"
                    }
    
                    

                  
                    #TRY UPLOADING
                    try: 
                        
                        sftp_tools.put(message,storageNode)
                    except Exception as e:
                        print(e)
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
                    serverDButil.setRAIDtype(self.RAIDtype, self.obj.FID)
                    
                    
                    
                    #RAID ID COUNTER
                    raid_id = 0
                    
                    
                    
                    #CREATE DATABASE ENTRY FOR NEWLY UPLOADED FILES
                    for i in upload_list:
                        
                        start = i["storage_info"]["Gap"][0]
                        storageNode = i["storage_info"]["storageNode"]
                        
                        raid_id+=1
                        
                        #CREATE THE ENTRY
                        Files.objects.create(
                            owner=self.obj.owner, 
                            fName= i["fName"],
                            file=self.obj.file,
                            actualSize=os.path.getsize(os.path.join(cwd, i["fName"])),
                            SID = storageNode["SID"],
                            RAIDtype = self.RAIDtype,
                            RAIDid = raid_id,
                            start = start,
                            FID=self.obj.FID,)

                    
                    # #SET THE RAID TYPE FOR THE FILES 
                    
                    
                    
                    shutil.rmtree(cwd)
    
            
            

                