import os
import math
import json
import time
# Setup to easily reuse byte sizes
KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30

#CHECK IF A JSON DB EXISTS
if os.path.isfile ("mdJson.json"):
    with open("mdJson.json", "r") as f:
        data = f.read()
        if data:
            mdList = json.loads(data)
        else:
            mdList = []
#IF NOT, SET VALUES TO DEFAULT
else:
    mdList = []
    
#STORAGE SIZE
if os.path.isfile ("storageFolder/storage"):
    storSize = os.path.getsize("storageFolder/storage")
else:
    storSize = 0



#-----------------Fragmented Check-----------------------
def fragmentCheck(mdList, storSize):
    #sort json list based on start point to sort the files
    jsonList = sorted(mdList, key=lambda k: k["start"])
    
    prev_end = 0
    spaceBetweenFiles  = []
    
    for file in jsonList:
        # Calculate the end byte of the current file
        endByte = file["start"] + file["fileSize"]
        
        #calculate if there is a gap between the previous file and the current file
        if file["start"] != 0:
            space_start = prev_end
            space_end = file["start"]
            
            #if there is a gap append the gap to the list of gaps
            if (space_end - space_start) != 0:
                spaceBetweenFiles.append((space_start,space_end))
        
        prev_end = endByte
    
    #get the size between the last file and the storage location
    space_start = prev_end
    space_end = storSize
    spaceBetweenFiles.append((space_start,space_end))
    
    return spaceBetweenFiles

def getStartLocation(mdList, fileSize, storSize):
    spaceBetweenFiles = fragmentCheck(mdList,storSize)
    
    smallestSpace = None
    #look for the smallest space where the file can fit
    for space in spaceBetweenFiles:
        
        if space[1]-space[0] >= fileSize:
            if smallestSpace is None or space[1]-space[0] < smallestSpaceBetween:
                smallestSpace = space
                smallestSpaceBetween = space[1]-space[0]
    
    if smallestSpace != None:
        return smallestSpace[0]
    else:
        return None
#-----------------Fragmented Check-----------------------


def getMaxFile(mdList, storSize):
    fragments = fragmentCheck(mdList, storSize)
    largest = 0
    for i in fragments:
        if i[1] - i[0] > largest:
            largest = i[1] - i[0]
    return largest
    
    
    


def CreateAlloc(size):
    storName = "storage"
    #CREATE FOLDER
    storageLoc = "storageFolder"
    if not os.path.exists(storageLoc):
        os.makedirs(storageLoc)
        
    #CREATE BLANK FILE 
    if not os.path.isfile(os.path.join(storageLoc,storName)):
        with open(os.path.join(storageLoc,storName), 'wb') as storage:
            for each in range(math.floor(size / KB)): 
                storage.write(b'0'*KB)
        storSize = os.path.getsize(os.path.join(storageLoc,storName))
        return storSize

def storeFile(fName, cwd, start, storageLoc):
    #Open Storage file
    with open(storageLoc, 'rb+') as storage, open(os.path.join(cwd, fName), 'rb') as inputFile:
        fileSize = os.stat(os.path.join(cwd, fName)).st_size
        
        storage.seek(start)
        
        for each in range(math.ceil(fileSize / KB)): # Read range is done per KB; Ceiling is used to write the last KB of the inputFile
            storage.write(inputFile.read(KB))
            
        # #Save updated metadata to json file
        # with open("mdJson.json", "w") as f:
            
        #     json.dump(mdList, f)




def retFile(fileMD, storageLoc):
    if fileMD == -1:
        print("File Does not Exist")

    else:
        
        #print(fileMD)
        with open(storageLoc, 'rb+') as storage, open(os.path.join(fileMD["cwd"],fileMD["fName"]), 'wb') as outputFile:

            storage.seek(fileMD["start"])
            ctr = 0
            
            for each in range(math.floor(fileMD["size"] / KB)): # Write is done per KB; Floor is used to leave the last KB
                
                outputFile.write(storage.read(KB))
            outputFile.write(storage.read(fileMD["size"] - math.floor(fileMD["size"] / KB) * KB)) # Writes the last KB in case the remaining bytes is not a full KB
        
        
def delFile(mdList, fID):
    index_to_delete = None
    for i, item in enumerate(mdList):
        if item["FID"] == fID:
            index_to_delete = i
            break
    if index_to_delete is not None:
        del mdList[index_to_delete]
    return mdList


def fileModModule(command, fID, fName, storageLoc):
    

    #CreateAlloc(int(2.5*GB), storFolder, storName)

    
    
    #storeFile(fName, fID, storageLoc)
    if command == "download":
        retFile(mdList, fID, storageLoc)
        pass
    elif command == "upload":
        newMDlist = storeFile(fName, fID, storageLoc)
        pass
    elif command == "delete":
        newMDlist = delFile(mdList, fID)
        pass
    
    
def main():
    
    command = "download"
    fID = 130
    fName = "test.mp4"
    
    storFolder = "storageFolder"
    storName = "storage"
    storageLoc = os.path.join(storFolder, storName)
    
    fileModModule(command, fID, fName, storageLoc)
    
    
if __name__ == "__main__":
    starttime = time.time()
    main()
    endtime = time.time()
    print(endtime-starttime)
