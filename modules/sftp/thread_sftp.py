import threading
import time
import os
import shutil

import modules.sftp.sftp_init_tools as sftp_init_tools
import modules.RAIDmod as RAIDmod

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
        time.sleep(2)
        # TODO: Change to SFTP function
        if self.message["command"] == "upload":
            print(self.storageNode["port"])
            upload(self.message, self.storageNode)
            if self.deleteFolder:
                pass
                #shutil.rmtree(self.message["cwd"])
        elif self.message["command"] == "download":
            download(self.message, self.storageNode)

        else:
            delete(self.message, self.storageNode)
            
            
class download(threading.Thread):
    def __init__(self,message, fileTuple):
        # execute the base constructor
        threading.Thread.__init__(self)
 
        self.fileTuple=tuple(sorted(fileTuple, key=lambda x: x[0]))
        self.message = message
        
    # override the run function
    def run(self):
        threads = []
        fileParts = []
        brokenFile = False
        ctr = 0
        for i in self.fileTuple:
            
            if i != "NONE":
                message = {
                "fName": i[0],
                "FID" : self.message["FID"],
                "cwd" : self.message["cwd"],
                "command":"download"
                }
                
                if not i[1]["status"]:
                    brokenFile = True
                    missingFile = i[0]

                else:
                    t1 = sftp_init_tools.SFTPThread(message, i[1])   
                    threads.append(t1)
                    fileParts.append(i[0])
                    ctr += 1
                
                
                #stop other node download if it is in RAID 1
                if self.message["RAIDtype"] == 1:
                    break
                elif self.message["RAIDtype"] == "PARITY":
                    if (not brokenFile) and (ctr == 2):
                        break
                    
        for i in threads:
            i.start()
        for i in threads:
            i.join()
            
        if len(threads) > 1:
            fileList = []
            for i in self.fileTuple:
                fileList.append(i[0])
                
            if self.message["RAIDtype"] == 0:
                raid = RAIDmod.raid0
                if not brokenFile:
                    raid.merge(fileList[0][:-2], fileList, self.message["cwd"])
                else:
                    print("File Corrupted, please try again")
            else:
                raid = RAIDmod.pRAID()
                
                if not brokenFile:
                    

                    raid.merge(fileList[0][:-2], fileParts, self.message["cwd"])
                    
                elif brokenFile and ctr >= 2:
                    fName = fileParts[0][:-2]
                    if fileParts[0][-1].isdigit():
                        part1 = int(fileParts[0][-1])
                    else:
                        part1 = fileParts[0][-1]
                        
                        
                    if fileParts[1][-1].isdigit():
                        part2 = int(fileParts[1][-1])
                    else:
                        part2 = fileParts[1][-1]
                        
                    raid.repair(fName, part1, part2, self.message["cwd"])
                    
                    partList = [f'{fName}-{0}', f'{fName}-{1}']
                    
                    raid.merge(fName, partList, self.message["cwd"])

                        
                else:
                    print("File Corrupted, please try again")
                    for i in self.fileTuple:
                        file = os.path.join(self.message["cwd"],i[0])
                        if os.path.isfile(file):
                            os.remove(file)
            
            for i in self.fileTuple:
                file = os.path.join(self.message["cwd"],i[0])
                if os.path.isfile(file):
                    os.remove(file)

