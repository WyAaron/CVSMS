import threading
import os

import modules.sqlite3.serverDButil as serverDButil
import modules.sftp.thread_sftp as thread_sftp
import modules.sftp.raid.raid0_tools as raid0_tools
import modules.sftp.raid.raid1_tools as raid1_tools
import modules.sftp.raid.parity_tools as parity_tools

import modules.archive.fileMod as file_module
import modules.nodeTools.getTools as NodeGetTools
import shutil

from CVSMS.models import  Files



class archive_put(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj
    
    def run(self):
        
        
    
        obj = self.obj
        cwd = os.path.dirname(obj.file.path)
        url = obj.file.url

        fName = serverDButil.getFileMD(obj.FID)[0]["fName"]

        context = {
            'button': False
        }
        message = {
                    "fName": obj.fName,
                    "FID": obj.FID,
                    "cwd": cwd,
                    "command": "download",
                    "size": obj.actualSize,
                    "start": obj.start,
                    "RAIDtype": obj.RAIDtype
                }
        
        #DOWNLOAD IF FILE IS NOT IN SERVER
        if not os.path.isfile(os.path.join(cwd, fName)):
            if not os.path.exists(cwd):
                os.mkdir(cwd)
                
            # create the thread
            if obj.RAIDtype == "NONE":
                # GET DATA FROM DB
                fileMD = serverDButil.getFileMD(obj.FID)[0]
                storageNode = serverDButil.getStorageNode(fileMD["SID"])
                get = thread_sftp.standard_get(message, fName, storageNode)
                
            else:
                print("DOWNLOADING RAIDED FILES")
                if obj.RAIDtype == "0":
                    get = raid0_tools.thread_get(obj)

                elif obj.RAIDtype == "1":
                    get = raid1_tools.thread_get(obj)
                    
                else:
                    get = parity_tools.thread_get(obj)
            
            get.start()
            get.join()
        
        
        #GET THE START BYTE OF THE FILE
        all_files = serverDButil.get_all_files_by_sid("ARCHIVE")
        storage_size = serverDButil.getStorageNode("ARCHIVE")["allocSize"]  
        start = file_module.getStartLocation(all_files, message["size"], storage_size)
        
        #print(f"STARTING ARCHIVAL STARTING BYTE: {start}")
    
        #CHECK IF THE FILE CAN STILL FIT IN THE ARCHIVE 
        if start != None: 
            archiveCWD = os.path.join(os.getcwd(),"storageFolder/storage")
            
            #CHECK IF FILE STORING IS SUCCESSFUL
            success = True
            try:
                file_module.storeFile(message["fName"], message["cwd"], start, archiveCWD)
            
            except Exception as e:
                print(e)
                success = False
                
            
            if success:
                #CREATE THE NEW UNRAIDED FILE ENTRY
                serverDButil.delMD(self.obj.FID)
                
                Files.objects.create(
                owner = self.obj.owner, 
                fName = self.obj.fName,
                file = self.obj.file,
                actualSize = self.obj.actualSize,
                FID = self.obj.FID,
                start = start,
                isCached = False,
                SID = "ARCHIVE")
                
                shutil.rmtree(os.path.dirname(self.obj.file.path))
                
                print("SUCCESSFUL ARCHIVING")
                
                
            else:
                print("NOT ENOUGH STORAGE IN THE ARCHIVE")




class archive_get(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj
    
    def run(self):
        
        obj = self.obj
        cwd = os.path.dirname(obj.file.path)
        
        #DOWNLOAD IF FILE IS NOT IN SERVER
        if not os.path.isfile(os.path.join(cwd, self.obj.fName)):
            if not os.path.exists(cwd):
                os.mkdir(cwd)
                
            
            
            message = {
                    "fName": obj.fName,
                    "FID": obj.FID,
                    "cwd": cwd,
                    "command": "download",
                    "size": obj.actualSize,
                    "start": obj.start,
                    "RAIDtype": obj.RAIDtype
                }
            
            
            archiveCWD = os.path.join(os.getcwd(),"storageFolder/storage")
            
            file_module.retFile(message, archiveCWD)
        
        

class unarchive(threading.Thread):
    def __init__(self, obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        self.obj = obj
    
    def run(self):
        
        obj = self.obj
        cwd = os.path.dirname(obj.file.path)
        
        
        #RETRUEVE FILE IF IT IS STILL IN STORAGE
        if not os.path.isfile(os.path.join(cwd, self.obj.fName)):
            if not os.path.exists(cwd):
                os.mkdir(cwd)
                
            
            
            message = {
                    "fName": obj.fName,
                    "FID": obj.FID,
                    "cwd": cwd,
                    "command": "download",
                    "size": obj.actualSize,
                    "start": obj.start,
                    "RAIDtype": obj.RAIDtype
                }
            
            
            archiveCWD = os.path.join(os.getcwd(),"storageFolder/storage")
            
            file_module.retFile(message, archiveCWD)
        

        storageNode = NodeGetTools.get_storage_nodes([obj.fName], cwd)  
        
        if storageNode:
            storageNode = storageNode[0]["storage_info"]
            # GET FILE START BYTE
            start = storageNode["Gap"][0]

            # SET THE START BYTE IF THE FILE
            obj.start = start
            obj.save()

            #print(start)

            storageNode = storageNode["storageNode"]
            serverDButil.addStorageNode(storageNode["SID"], obj.FID)

            message = {
                "fName": obj.fName,
                "FID": obj.FID,
                "cwd": cwd,
                "size": obj.actualSize,
                "start": obj.start,
                "command": "upload"
            }

            try:

                sFTP = thread_sftp.SFTPThread(
                    message, storageNode, isArchive=True)

                sFTP.run()
                success = sFTP.success
                
                if success:
                    #CREATE THE NEW UNARCHIVED FILE ENTRY
                    serverDButil.delMD(self.obj.FID)
                    
                    Files.objects.create(
                    owner = self.obj.owner, 
                    fName = self.obj.fName,
                    file = self.obj.file,
                    actualSize = self.obj.actualSize,
                    FID = self.obj.FID,
                    start = obj.start,
                    isCached = False,
                    SID = storageNode["SID"])
            
                
                
            except Exception as e:
                # Todo Function when false it must delete file from db
                print(e)
                
        else:
            shutil.rmtree(cwd)
            print("There is not enough space")
        
        
        
        
        