import os
import threading
import shutil

import modules.sftp.sftp_tools as sftp_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil

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
        
        
        for fileMD in file_list:
            # print(fileMD["RAIDid"])
            if fileMD["RAIDid"] != -1:
                storageNode = serverDButil.getStorageNode(fileMD["SID"])

            
        
        pass