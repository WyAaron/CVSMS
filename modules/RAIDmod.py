import os
import time
import numpy as np
import math

KB = 2 ** 10
MB = 2 ** 20
GB = 2 ** 30

def progress_bar(count, total, status=''):
    """
    A function to display a percentage indicator of progress.
    count: the number of items completed so far
    total: the total number of items
    status: an optional message to display alongside the progress bar
    """
    bar_len = 40
    percent = float(count) / float(total)
    hashes = '#' * int(percent * bar_len)
    spaces = ' ' * (bar_len - len(hashes))
    print('\r[{0}] {1}% {2}'.format(hashes + spaces, int(percent * 100), status), end='', flush=True)
    
    
    


class raid0:
    #CANNOT RAID LESS THAN 1 KB * THE NUMBER OF FILES
    def split(fName, numOfFiles, storageLocation):
        #list for 
        fileList = [] # a list to keep track of the opened part files
        partNames = [] # a list for the names of the file parts
        

        #open the amount of files to be split into specified by the user
        for i in range(numOfFiles):
            fileList.append(open(os.path.join(storageLocation,f"{fName}-{i}"), "wb"))
            partNames.append(f"{fName}-{i}")
        
        #OPEN THE FILE TO BE SPLIT
        with open(os.path.join(storageLocation,fName), "rb") as originalFile:
            
            ctr = 0
            while True:
                # GET DATA FROM ORIGINAL FILE
                data = originalFile.read(25*MB)

                fileList[ctr].write(data)
                ctr+=1
            
                #RESET COUNTER IF IT HAS REACHED THE LAST FILE
                if ctr == numOfFiles:
                    ctr = 0 

                # CHECK IF END OF FILE
                #temp+= len(data)
                if not data:
                    break
                #progress_bar(temp, os.path.getsize(fName), status="splitting" )
            
        #CLOSE ALL THE FILES
        for i in fileList:
            i.close()
            
        #RETURN THE LIST OF FILES THAT WERE SPLIT
        return partNames

    def merge(fName, partList, storageLocation):
        fileList = [] # a list to keep track of the opened part files
        ctr = 0 #COUNTER TO KEEP TRACK OF WHICH FILE IS THE NEXT TO ACCESS
        
        #OPEN ALL THE FILE PART
        for i in partList:
            fileList.append(open(os.path.join(storageLocation, i), "rb"))
        
        #OPEN MAIN FILE FOR WRITING
        with open(os.path.join(storageLocation,fName), "wb") as originalFile:
            temp = 0
            
            #progress bar variables
            # total_size = 0
            # for file in partList:
            #     file_size = os.path.getsize(os.path.join(storageLocation, i))
            #     total_size += file_size
                
            while True:
                # RETRIEVE DATA FROM PART FILE
                data = fileList[ctr].read(25*MB)
                
                # WRITE THE FILE IN EACH PART   
                originalFile.write(data)
                ctr+=1
                
                # RESET COUNTER IF IT HAS REACHED THE LAST FILE
                if ctr == len(fileList):
                    ctr = 0 
                    
                # CHECK IF END OF FILE
                if not data:
                    break
                temp+=len(data)
                #progress_bar(temp, total_size , status="merging" )
        #CLOSE ALL THE FILES
        for i in fileList:
            i.close()  
            
            
def xor_chunks(chunk1, chunk2):
    
        if len(chunk1) > len(chunk2):
            chunk2 += bytes(len(chunk1) - len(chunk2))
        else:
            chunk1 += bytes(len(chunk2) - len(chunk1))
        # Convert bytes to numpy arrays
        arr1 = np.frombuffer(chunk1, dtype=np.uint8)
        arr2 = np.frombuffer(chunk2, dtype=np.uint8)

        # XOR the arrays
        result = np.bitwise_xor(arr1, arr2)
            
        return bytes(result)
    
class pRAID:
    def split(fName, storageLocation):
        #list for 
        fileList = [] # a list to keep track of the opened part files
        partNames = [] # a list for the names of the file parts
        parityChunks = []
        numOfFiles = 2
        ctr = 0 # ctr for which part to write in

        #open the amount of files to be split into specified by the user
        for i in range(numOfFiles):
            fileList.append(open(os.path.join(storageLocation,f"{fName}-{i}"), "wb"))
            partNames.append(f"{fName}-{i}")
        partNames.append(f"{fName}-p")
        
        #OPEN THE FILE TO BE SPLIT
        with open(os.path.join(storageLocation,fName), "rb") as originalFile, open(os.path.join(storageLocation,f"{fName}-p"), "wb") as parityFile:
            #WRITE THE FILE IN EACH PART 
            
            #FOR ZERO MB FILES check if it has ran atleast once
            once = 0
            while True:
                # GET DATA FROM ORIGINAL FILE
                data1 = originalFile.read(25*MB)
                data2 = originalFile.read(25*MB)
                
                    
                
                
                #if there is still data gathered from data 1
                if data1 or not once:
                    if len(data1) < 25*MB:
                        data1 += bytes(25*MB - len(data1))
                    
                    
                    if len(data2) < 25*MB:
                        data2 += bytes(25*MB - len(data2))
                
                    #PUT DATA IN FILE PART
                    fileList[0].write(data1)
                    
                    fileList[1].write(data2)
                    
                    
        
                    
                    parityData = xor_chunks(data1, data2)
                    
                    
                

                    #STORE TO FILE
                    parityFile.write(parityData)
                    

                once += 1
                    
                if (not data1 or not data2) and once >1:
                    break
                # CHECK IF END OF FILE
                #temp+= len(data)
                
                #progress_bar(temp, os.path.getsize(fName), status="splitting" )
            
            
            
            
        #CLOSE ALL THE FILES
        for i in fileList:
            i.close()
            
        #RETURN THE LIST OF FILES THAT WERE SPLIT
        return partNames

    
    def repair(fName, fileList, storageLocation):
        
        validPart = open(os.path.join(storageLocation, fileList[0]), "rb")
        parity = open (os.path.join(storageLocation,fileList[1]), "rb")
        
        # Define the list of possible inputs
        possibleParts = ["0", "1", "p"]
        
        partList = [fileList[0][-1],fileList[1][-1]]
    
        for part in possibleParts:
            if part not in partList:
                recoveredPart = part
                break
        
            
        
            
            
        print(recoveredPart)
    
        with open(os.path.join(storageLocation,f"{fName}-{recoveredPart}"), "wb") as repairedFile:
            
            lastDataLen = None
            while True:
                
                validData = validPart.read(25*MB)
                parityData= parity.read(25*MB)
                
                #PERFORM AN XOR OPERATION TO RECOVER THE LOST DATA
                parityChunk = xor_chunks(validData, parityData)
                    
                #WRITE THE RECOVERED DATA ON THE RECOVERING FILE
                repairedFile.write(parityChunk)
                
                
                #print(validData)
                if not validData or not parityData:
                    break
                
                

            
        validPart.close()
        parity.close() 
        
    def merge(fName, partList,storageLocation):
        fileList = [] # a list to keep track of the opened part files
        ctr = 0 #COUNTER TO KEEP TRACK OF WHICH FILE IS THE NEXT TO ACCESS
        
        #OPEN ALL THE FILE PART
        for i in partList:
            fileList.append(open(os.path.join(storageLocation,i), "rb"))
        
        #OPEN MAIN FILE FOR WRITING
        with open(os.path.join(storageLocation,fName), "wb+") as originalFile:
            temp = 0
            
            #progress bar variables
            # total_size = 0
            # for file in partList:
            #     file_size = os.path.getsize(os.path.join(storageLocation,i))
            #     total_size += file_size
                
            while True:
                # RETRIEVE DATA FROM PART FILE
                data = fileList[ctr].read(25*MB)
                
                # WRITE THE FILE IN EACH PART   
                originalFile.write(data)
                ctr+=1
                
                # RESET COUNTER IF IT HAS REACHED THE LAST FILE
                if ctr == len(fileList):
                    ctr = 0 
                    
                # CHECK IF END OF FILE
                if not data:
                    break
                
                lastLen = len(data)
                temp+=len(data)
                #progress_bar(temp, total_size , status="merging" )
                
            #CHECK IF FILE IS CHUNKABLE
            
            if math.ceil(originalFile.tell() / 25*MB % 2) != 2:
                originalFile.seek(-lastLen*2,1)
                data = originalFile.read(25*MB*2)
                originalFile.seek(-lastLen*2,1)
                originalFile.truncate(originalFile.tell())
                originalFile.write(data.rstrip(b'\x00'))
            else:
                originalFile.seek(-lastLen,1)
                data = originalFile.read(25*MB)
                originalFile.seek(-lastLen,1)
                originalFile.truncate(originalFile.tell())
                originalFile.write(data.rstrip(b'\x00'))
            
        #CLOSE ALL THE FILES
        for i in fileList:
            i.close()  

def main():
    fName = "test50mb"
    #fName = "test50mb"
    # raid = pRAID()
    fileList = ['test50mb-0', 'test50mb-1']
    #fileList = ['vid.mp4-0', 'vid.mp4-1']
    
    print(25*MB)
    #['test50mb.pdf-0', 'test50mb.pdf-1', 'test50mb.pdf-p']
    #print(pRAID.split(fName,"splitStorage"))
    
    #pRAID.repair(fName, fileList, "splitStorage")
    #fileList = ['hello.txt-0', 'hello.txt-1', 'hello.txt-p']
    #fileList = ['tempvid.mp4-0', 'tempvid.mp4-1']
    pRAID.merge(fName, fileList,"splitStorage")
    
    # Setup to easily reuse byte sizes
    
    # option = 2
    # if option == 1:
    #     raid0cut(fName)
    # else:
    #     raid0recover(fName)

    # RAID0 = raid0
    
    # print(raid0.split(fName, 2, "splitStorage"))
    #raid0.merge(fName, fList, "splitStorage")
    
    

if __name__ == "__main__":
    starttime = time.time()
    main()
    endtime = time.time()
    print(endtime-starttime)