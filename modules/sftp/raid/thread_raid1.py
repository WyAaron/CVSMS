import os
import threading
import shutil

import modules.sftp.sftp_tools as sftp_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil

from CVSMS.models import  Files,storageNodeInfo

#elif self.RAIDtype == "1":
    #pass
    
    
    # #upload to 2 storage nodes
    # storageNodeList = serverDButil.getAllStorageNodes()
    
    # fileList = []
    
    # for i in range(2):
    #     fileList.append(FileToRaid["fName"])
    
    # #SEND THE SPLIT FILES TO THE STORAGE NODES
    
    
    # threads = []
    # fileStorPair = getStorageNodes(fileList, storageNodeList, FileToRaid["filePath"])
    # print(fileStorPair)
    # if len(fileStorPair) == len(fileList):
    
    #     for i in fileStorPair:
            
    #         #DUPLOCATE THE FILES TO THE STORAGE NODES
    #         message = {
    #             "fName": i["fileMD"]["fName"],
    #             "FID" : FileToRaid["FID"],
    #             "cwd" : FileToRaid["filePath"],
    #             "command":"upload"
    #         }
    #         try:
    #             Files.objects.create(
    #                 owner=self.obj.owner, 
    #                 FID = self.obj.FID,
    #                 SID = i["storageNode"]["SID"], 
    #                 fileName = self.obj.fileName, 
    #                 file = self.obj.file, 
    #                 actualSize = i["fileMD"]["fSize"],
    #                 RAIDtype = self.RAIDtype,
    #                 RAIDid = 0    
    #                 )
    #             t1 = sftp_init_tools.SFTPThread(message, i["storageNode"])
    #             threads.append(t1)
                
    #         except Exception as e:
    #             #Todo Function when false it must delete file from db 
    #             print(e)
                
    #     for i in threads:
    #         i.start()
    #     for i in threads:
    #         i.join()
                        
    #     shutil.rmtree(FileToRaid["filePath"])
    # else:
    #     print("Not enough storage Nodes")