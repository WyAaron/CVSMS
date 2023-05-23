import os
import threading
import shutil

import modules.sftp.sftp_init_tools as sftp_init_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil

from CVSMS.models import  Files,storageNodeInfo

# else:
#     pass
    # raid = RAIDmod.pRAID()
    
    # #storageNodeUploadList = get_Three_StorageNode_That_Can_Fit_The_File_Parts(self.storageNodeList, FileToRaid["fSize"])
    # storageNodeList = serverDButil.getAllStorageNodes()
    # fileList = raid.split(FileToRaid["fName"], FileToRaid["filePath"])
    # # print(fileList)
    # # #CREATE FUNCTION TO GENERATE LIST OF DIFFERENT STORAGE NODES
    # fileStorPair = getStorageNodes(fileList, storageNodeList, FileToRaid["filePath"])
    # threads = []
    
    # if len(fileStorPair) == len(fileList):
    #     #SEND THE SPLIT FILES TO THE STORAGE NODES
    #         try:
    #             for i in fileStorPair:
    #                 message = {
    #                     "fName": i["fileMD"]["fName"],
    #                     "FID" : FileToRaid["FID"],
    #                     "cwd" : FileToRaid["filePath"],
    #                     "command":"upload"
    #                 }
                    

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
                    
    #             for i in threads:
    #                 i.start()
    #             for i in threads:
    #                 i.join()
                            
    #             shutil.rmtree(FileToRaid["filePath"])
    #         except Exception as e:
    #             print(e)
    # else:
    #     print("Not enough storage Nodes")   