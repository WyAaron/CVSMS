import os
import threading
import shutil

import modules.sftp.sftp_init_tools as sftp_init_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil

from CVSMS.models import  Files,storageNodeInfo

class raid0_put(threading.Thread):
    def __init__(self,obj,RAIDtype):
        # execute the base constructor
        threading.Thread.__init__(self)
        # store the value
        self.obj = obj
        self.RAIDtype = RAIDtype
    # override the run function
    def run(self):
        pass
        # FileToRaid = {
        #     'owner':self.obj.owner, 
        #     'FID': self.obj.FID, 
        #     'fName': self.obj.fileName, 
        #     'file':self.obj.file,
        #     'actualSize': self.obj.actualSize,
        #     'RAIDtype': self.RAIDtype, 
        #     "filePath": os.path.dirname(self.obj.file.path)
        #     }
        
        # #FIND STORAGE NODE LOCATION OF FILE TO BE RAIDED
        # storageNodeList = NodeGetTools.getCurrentFileStorageNodes(self.obj.FID)
        
        # storageNode = storageNodeList[0]
        
        # #SFTP THE FILE FROM THE STORAGE NODE
        # message = {
        #     "fName": FileToRaid["fName"],
        #     "FID" : FileToRaid["FID"],
        #     "cwd" : FileToRaid["filePath"],
        #     "command":"download"
        # }

        # if not os.path.exists(FileToRaid["filePath"]):
        #     os.mkdir(FileToRaid["filePath"])
        
        # if not os.path.isfile(self.obj.file.path):
        #     sftp_init_tools.download(message, storageNode)    
        #     # serverDButil.removeStorageNodeFromFileMD(message["FID"],)
        #     # serverDButil.updateRaidType(FileToRaid["RAIDtype"], message["FID"])
            
        #     # message = {
        #     # "FID": FileToRaid["FID"],
        #     # "command":"delete"
        #     # }
        #     # sSFTP.delete(message, storageNode, isRaid = True)
        
        # else:
        #     print("Did not download")
        # # #PERFORM RAID   
        
        # if self.RAIDtype == "0":
        #     raid = RAIDmod.raid0
        #     fileList = raid.split(FileToRaid["fName"],2,FileToRaid["filePath"])
            
        #     threads = []
        #     storageNodeList = serverDButil.getAllStorageNodes()
            
            
        #     #SEND THE SPLIT FILES TO THE STORAGE NODES
        #     fileStorPair = serverDButil.getStorageNodes(fileList, storageNodeList, FileToRaid["filePath"])
            
        #     if len(fileStorPair) == len(fileList):
            
        #         for i in fileStorPair:
        #             message = {
        #                 "fName": i["fileMD"]["fName"],
        #                 "FID" : FileToRaid["FID"],
        #                 "cwd" : FileToRaid["filePath"],
        #                 "command":"upload"
        #             }
        #             try:
        #                 print(i["fileMD"]["fName"])
        #                 Files.objects.create(
        #                     owner=self.obj.owner, 
        #                     FID = self.obj.FID,
        #                     SID = i["storageNode"]["SID"], 
        #                     fileName = i["fileMD"]["fName"], 
        #                     file = self.obj.file, 
        #                     actualSize = i["fileMD"]["fSize"],
        #                     RAIDtype = self.RAIDtype,
        #                     RAIDid = 0     
        #                     )
                        
        #                 t1 = sftp_init_tools.SFTPThread(message, i["storageNode"])
        #                 threads.append(t1)
                        
        #             except Exception as e:
        #                 #Todo Function when false it must delete file from db 
        #                 print(e)
                        
        #         for i in threads:
        #             i.start()
        #         for i in threads:
        #             i.join()
                        
        #         #shutil.rmtree(FileToRaid["filePath"])
                        
                    
        #     else:
        #         print("Not enough storage Nodes")

class raid0_get(threading.Thread):    
    pass