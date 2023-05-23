
import os
import modules.sqlite3.serverDButil as serverDButil

def findStorNode(storNodeList, fileSize):
    storNodeForFile = None
    storNodeList = sorted(storNodeList, key=lambda x: x['maxSize'], reverse=True)
    # storNodeList = sorted(storNodeList, reverse=True)
    for i in range(len(storNodeList)):
        #print(f"{storNodeList[i]} < {fileSize} = {storNodeList[i] < fileSize}")
        if storNodeList[i]["maxSize"] >= fileSize:
            
            storNodeForFile = storNodeList[i]
        elif storNodeList[i]["maxSize"] < fileSize:
            break
    if storNodeForFile == None:
        return storNodeList, storNodeForFile
    
    else:
        
        # print()
        storNodeList.pop(i)
        
        return storNodeList, storNodeForFile


def getAvailableStorNode(storNodeList, fileList):
    storList = []
    
    tempList = storNodeList
    fileList = sorted(fileList, key=lambda x: x['fSize'], reverse=True)
    if len(tempList) >= len(fileList):
        for i in fileList:
            
            tempList, storNode = findStorNode(tempList, i['fSize'])
            

            #print(len(fileList))
            if storNode:
                storList.append({"fileMD" : i, "storageNode" : storNode})
    
    if len(storList) == len(fileList): 
        return storList
    else:
        return[]


def getStorageNodes(fileList, storageNodeList, path):
    #GET THE FILE SIZE FOR EACH PART
        tempFileList = []
        for i in range(len(fileList)):
            fileSize = os.path.getsize(os.path.join(path, fileList[i]))
            
            tempFileMD = {
                "fName": fileList[i],
                "fSize": fileSize
            }
            
            tempFileList.append(tempFileMD)
            
        #SORT THE FILES IN ASCENDING ORDER BASED ON THEIR SIZE 
        return getAvailableStorNode(storageNodeList, tempFileList)
    

def getCurrentFileStorageNodes(FID):
    fileList = serverDButil.searchMD([FID])
    storageSIDlist = []
    
    for i in fileList:
        if i["SID"] != "NONE":
            storageSIDlist.append(serverDButil.getStorageNode([i["SID"]]))
    
    return storageSIDlist