import django
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from CVSMS.models import  Files,storageNodeInfo
from .forms import FileForm,RAIDForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import sSFTP
import RAIDmod
import serverDButil
import fileMod
import storageNodeMD
import os 
from django.http import HttpResponse
from django.contrib import messages
import time 
import threading
import shutil
import time



# Cr = "eate your views here.
def get_storageSize():
    obj = storageNodeInfo.objects.all()
    storageSize = sum(obj.values_list('allocSize',flat=True))
    return storageSize


def get_fileTotalSize(): 
    files = Files.objects.filter(RAIDid = -1)    
    totalFileSize = sum(files.values_list('actualSize',flat=True))    
    return totalFileSize

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

# Home view of user
@login_required
def home_view(request): 
    user = request.user 
    if user.is_superuser: 
        context = {
        "file_list": Files.objects.filter(RAIDid = -1) , 
        #"file_list": Files.objects.all() ,
        'storageSize': get_storageSize(),
        'totalFileSize': get_fileTotalSize()
    }
    else:
        context = {
            "file_list": Files.objects.filter(owner=request.user,RAIDid = -1),
        }
    
        
    return  render(request,'home-view.html',context=context) 
 

#TODO: dashboard for admin

@login_required
# def CVSMS_detailed_view(request,id): 
#     file_obj = None
#     if id is not None: 
#         file_obj = fileMetadata.objects.get(id=id)
#         context = {
#             "object": file_obj, 
#         }

    # return render(request, 'detail.html', context=context)

@login_required
def fileSearch_view(request):
    query_dict =  request.GET 
    query = query_dict.get('q')
    
    try: 
        query = int(query_dict.get('q'))
    except: 
        query = None
    file_obj = None
    if query is not None: 
        file_obj = Files.objects.get(id=query)
    context ={
        "object": file_obj
    }
    return render(request, 'search.html', context=context)

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
            sSFTP.upload(self.message, self.storageNode)
            if self.deleteFolder:
                shutil.rmtree(self.message["cwd"])
        elif self.message["command"] == "download":
            sSFTP.download(self.message, self.storageNode)

        else:
            sSFTP.delete(self.message, self.storageNode)
            
        # block for a moment
        # display a message
        
#### Uploading of file
@login_required
def file_Upload_view(request):
    context = {
        "form": FileForm()
    }
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                id  = Files.objects.latest('id')
                FID = id.id+1
            except:
                FID = 1   
           
            #TODO CONNECTED STORAGE NODES
            obj = Files.objects.create(
            owner=request.user, 
            fileName= request.FILES["file"],
            file=request.FILES['file'],
            actualSize=request.FILES["file"].size,
            FID=FID)
                        
            cwd = os.path.dirname(obj.file.path)
            fName = os.listdir(cwd)[0]


            storageNodeList = serverDButil.getAllStorageNodes()
            storageNode = getStorageNodes([fName], storageNodeList, cwd)[0]["storageNode"]
            serverDButil.addStorageNode(storageNode["SID"],obj.FID)
             
             

            if storageNode:
                message = {
                "fName": fName,
                "FID" : obj.FID,
                "cwd" : cwd,
                "command":"upload"
                }
                messages.info(request,f'File has been uploaded!')
                try:
                    
                    t1 = SFTPThread(message, storageNode, deleteFolder=True)
                    t1.start()

                    
                except Exception as e:
                    #Todo Function when false it must delete file from db 
                    print(e)
            else:
                serverDButil.delMD([FID])
                messages.info(request,"There is no more space")
            
            #CREATE DB ENTRY FOR FILE SAVED
            
        return redirect('/')
    else:
        form = FileForm()
    return render(request,'file-Upload.html',context=context)


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
                print(i[0])
                if not i[1]["status"]:
                    brokenFile = True
                    missingFile = i[0]

                else:
                    t1 = SFTPThread(message, i[1])   
                    threads.append(t1)
                    fileParts.append(i[0])
                    ctr += 1
                
                
                #stop other node download if it is in RAID 1
                if (self.message["RAIDtype"] == "1") and ctr > 1:
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
                print(i[0])
            if self.message["RAIDtype"] == "0":
                raid = RAIDmod.raid0
                
                raid.merge(fileList[0][:-2], fileList, self.message["cwd"])
      
                print("MERGING")
                for i in fileList:
                    file = os.path.join(self.message["cwd"],i)
                    if os.path.isfile(file):
                        os.remove(file)
            
            elif self.message["RAIDtype"] == "PARITY":
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

            
            
            

def file_Retreive_view(request,id): 
    
    context = {
        "file": Files.objects.get(id=id)
    }
    obj =Files.objects.get(id=id)
    cwd = os.path.dirname(obj.file.path)
    url = obj.file.url
    
    
    fName = os.path.split(url)[-1]
    
    if not os.path.exists(cwd):
        os.mkdir(cwd)
    else:
        print("Directory Exists, Proceeding to SFTP")
    #TODO CONNECTED STORAGE NODES
    storageNodeList = getCurrentFileStorageNodes(obj.FID)
    fileList = serverDButil.searchMD([obj.FID])

    print(fileList)
    fileTuple = []
    
    if fileList[0]["RAIDtype"] != "NONE":
        for i in range(1,len(fileList)):
            
            fileName = fileList[i]["fileName"]
            print(fileName)
            fileTuple.append((fileName, storageNodeList[i-1]))
    
    else:
        fileTuple.append((fName, storageNodeList[0]))
        

    
    #GET DATA FROM DB
    message = {
        "FID" : obj.FID,
        "cwd" : cwd,
        "command":"download",
        "RAIDtype": obj.RAIDtype
        }
    context = {
        'button': False
    }

    

    if not os.path.isfile(os.path.join(cwd,fName)): #condition for file DNE in server
        messages.info(request,f'file started downloading from storage node.')
        # create the thread
        thread = download(message,fileTuple)
        # start the thread
        thread.start()
        return redirect('/')
        
        # t1.start()

        
        # disable download button
    elif os.path.isfile(os.path.join(cwd,fName)): #condition if file is in server already
        if os.path.getsize(os.path.join(cwd,fName)) == obj.actualSize: #File complete download from storage node
            if request.method == "GET": 
                file_download = get_object_or_404(Files, pk = id )
                response = HttpResponse(file_download.file, content_type='multipart/form-data')
                response['Content-Disposition'] =f'attactments; filename="{file_download.fileName}"' 
                return response
        else: # file is downloading from storage node
            messages.info(request,f'file is downloading')
    
    
    return redirect('/')



class raidThread(threading.Thread):
    def __init__(self,obj,RAIDtype):
        # execute the base constructor
        threading.Thread.__init__(self)
        # store the value
        self.obj = obj
        self.RAIDtype = RAIDtype
    # override the run function
    def run(self):
        # TODO: Change to SFTP function
        #TODO: implement in upload
        FileToRaid = {
            'owner':self.obj.owner, 
            'FID': self.obj.FID, 
            'fName': self.obj.fileName, 
            'file':self.obj.file,
            'actualSize': self.obj.actualSize,
            'RAIDtype': self.RAIDtype, 
            "filePath": os.path.dirname(self.obj.file.path)
            }
        
        #CREATE FUNCTION TO FIND STORAGE NODE LOCATION OF FILE TO BE RAIDED
    
        storageNodeList = getCurrentFileStorageNodes(self.obj.FID)
        
        storageNode = storageNodeList[0]
        
        #SFTP THE FILE FROM THE STORAGE NODE
        message = {
            "fName": FileToRaid["fName"],
            "FID" : FileToRaid["FID"],
            "cwd" : FileToRaid["filePath"],
            "command":"download"
        }
        
        
 
        
        if not os.path.exists(FileToRaid["filePath"]):
            os.mkdir(FileToRaid["filePath"])
        
        if not os.path.isfile(self.obj.file.path):
            print("downloading")
            try:
                sSFTP.download(message, storageNode)    
                self.obj.SID = "NONE"
                self.obj.RAIDtype = FileToRaid["RAIDtype"]
                self.obj.save()
            except Exception as e:
                print(e)
            
            # message = {
            # "FID": FileToRaid["FID"],
            # "command":"delete"
            # }
            # sSFTP.delete(message, storageNode, isRaid = True)
        
        else:
            print("Did not download")
        # #PERFORM RAID   
        
        if self.RAIDtype == "0":
            raid = RAIDmod.raid0
            fileList = raid.split(FileToRaid["fName"],2,FileToRaid["filePath"])
            
            threads = []
            storageNodeList = serverDButil.getAllStorageNodes()
            
            
            #SEND THE SPLIT FILES TO THE STORAGE NODES
            fileStorPair = getStorageNodes(fileList, storageNodeList, FileToRaid["filePath"])
            
            if len(fileStorPair) == len(fileList):
            
                for i in fileStorPair:
                    message = {
                        "fName": i["fileMD"]["fName"],
                        "FID" : FileToRaid["FID"],
                        "cwd" : FileToRaid["filePath"],
                        "command":"upload"
                    }
                    try:
                        print(i["fileMD"]["fName"])
                        Files.objects.create(
                            owner=self.obj.owner, 
                            FID = self.obj.FID,
                            SID = i["storageNode"]["SID"], 
                            fileName = i["fileMD"]["fName"], 
                            file = self.obj.file, 
                            actualSize = i["fileMD"]["fSize"],
                            RAIDtype = self.RAIDtype,
                            RAIDid = 0     
                            )
                        
                        t1 = SFTPThread(message, i["storageNode"])
                        threads.append(t1)
                        
                    except Exception as e:
                        #Todo Function when false it must delete file from db 
                        print(e)
                        
                for i in threads:
                    i.start()
                for i in threads:
                    i.join()
                        
                shutil.rmtree(FileToRaid["filePath"])
                        
                    
            else:
                print("Not enough storage Nodes")

            
        elif self.RAIDtype == "1":
            #upload to 2 storage nodes
            storageNodeList = serverDButil.getAllStorageNodes()
            
            fileList = []
            
            for i in range(2):
                fileList.append(FileToRaid["fName"])
            
            #SEND THE SPLIT FILES TO THE STORAGE NODES
            
            
            threads = []
            fileStorPair = getStorageNodes(fileList, storageNodeList, FileToRaid["filePath"])
            print(fileStorPair)
            if len(fileStorPair) == len(fileList):
            
                for i in fileStorPair:
                    
                    #DUPLOCATE THE FILES TO THE STORAGE NODES
                    message = {
                        "fName": i["fileMD"]["fName"],
                        "FID" : FileToRaid["FID"],
                        "cwd" : FileToRaid["filePath"],
                        "command":"upload"
                    }
                    try:
                        Files.objects.create(
                            owner=self.obj.owner, 
                            FID = self.obj.FID,
                            SID = i["storageNode"]["SID"], 
                            fileName = self.obj.fileName, 
                            file = self.obj.file, 
                            actualSize = i["fileMD"]["fSize"],
                            RAIDtype = self.RAIDtype,
                            RAIDid = 0    
                            )
                        t1 = SFTPThread(message, i["storageNode"])
                        threads.append(t1)
                        
                    except Exception as e:
                        #Todo Function when false it must delete file from db 
                        print(e)
                        
                for i in threads:
                    i.start()
                for i in threads:
                    i.join()
                                
                shutil.rmtree(FileToRaid["filePath"])
            else:
                print("Not enough storage Nodes")
        else:
            raid = RAIDmod.pRAID()
            
            #storageNodeUploadList = get_Three_StorageNode_That_Can_Fit_The_File_Parts(self.storageNodeList, FileToRaid["fSize"])
            storageNodeList = serverDButil.getAllStorageNodes()
            fileList = raid.split(FileToRaid["fName"], FileToRaid["filePath"])
            # print(fileList)
            # #CREATE FUNCTION TO GENERATE LIST OF DIFFERENT STORAGE NODES
            fileStorPair = getStorageNodes(fileList, storageNodeList, FileToRaid["filePath"])
            threads = []
            
            if len(fileStorPair) == len(fileList):
                #SEND THE SPLIT FILES TO THE STORAGE NODES
                    try:
                        for i in fileStorPair:
                            message = {
                                "fName": i["fileMD"]["fName"],
                                "FID" : FileToRaid["FID"],
                                "cwd" : FileToRaid["filePath"],
                                "command":"upload"
                            }
                            
    
                            Files.objects.create(
                                owner=self.obj.owner, 
                                FID = self.obj.FID,
                                SID = i["storageNode"]["SID"], 
                                fileName = i["fileMD"]["fName"], 
                                file = self.obj.file, 
                                actualSize = i["fileMD"]["fSize"],
                                RAIDtype = self.RAIDtype,
                                RAIDid = 0     
                                )
                            t1 = SFTPThread(message, i["storageNode"])
                            threads.append(t1)
                            
                        for i in threads:
                            i.start()
                        for i in threads:
                            i.join()
                                    
                        shutil.rmtree(FileToRaid["filePath"])
                    except Exception as e:
                        print(e)
            else:
                print("Not enough storage Nodes")   
                
def file_RAID_view(request,id): 
    
    context = {
    "form": RAIDForm(),
    "file":Files.objects.get(id=id) 
    }
    if request.method == "POST":
        form = RAIDForm(request.POST)
        RAIDtype = request.POST["RAIDtype"]
        obj = Files.objects.get(id=id)
        storageNode = {        
            "SID":1,
            "AllocSize":1000,
            "MaxSize": 1000,
            "IP":"192.168.0.225",
            "PORT":5001,
        }
        
        
        
        
        if form.is_valid():
            t1 = raidThread(obj,RAIDtype)
            t1.start()


            return redirect('/')
        else: 
            form = RAIDForm()
    return render(request,'file-RAID.html',context=context)



    
def file_Delete_view(request, id): 
    file = Files.objects.get(id=id)
    if request.method == "POST":
        storageNodeList = getCurrentFileStorageNodes(file.FID)
        
        
     
        # delete.start() 
        message = {   
        "FID" : file.FID,
        "command" : "delete"
        }
        
        for i in storageNodeList:
            if i != None:
                t1 = SFTPThread(message, i)   
                t1.start()    

        return redirect('/')
        # return redirect(success_url
    context = {
        "file":file
    }
    return render(request,'file-Delete.html',context)

class LocalStoragethread(threading.Thread):
    def __init__(self, message, fileTuple, obj):
        # execute the base constructor
        threading.Thread.__init__(self) 
        self.message  = message
        self.fileTuple = fileTuple
        self.obj = obj
    def run(self):
        thread = download(self.message, self.fileTuple)
        thread.start()
        thread.join()
        
        
        storageNodeList = serverDButil.getAllStorageNodes()
        
        newStorageLoc = storageNodeList[0]
        for i in range(len(storageNodeList)):
            if storageNodeList[i]["maxSize"] > newStorageLoc["maxSize"]:
                newStorageLoc = storageNodeList[i]
        
        if newStorageLoc["maxSize"] < os.path.getsize(os.path.join(self.message["cwd"],self.message["fName"])):
            print("No more space, cannot un RAID")
        else:
            for i in self.fileTuple:
                message = {
                    'FID':self.obj.FID,
                    "command":"delete"
                }

                print(i[1])

                sSFTP.delete(message, i[1])
                serverDButil.delMD([self.message["FID"]])
            message = {
                    'fName' : self.message["fName"],
                    'FID':self.obj.FID,
                    "command":"delete",
                    "cwd":self.message["cwd"]
                }
            
            storFolder = "storageFolder"
            storName = "storage"
            storageLoc = os.path.join(storFolder, storName) 
            
            fileSize = os.path.getsize(os.path.join(str(message["FID"]), message["fName"]))
            mdList = storageNodeMD.showMD()
            start = fileMod.getStartLocation(mdList, fileSize, os.path.getsize(storageLoc))
            newMD = fileMod.storeFile(message["fName"], message["FID"], start, storageLoc, self.message["cwd"])
            storageNodeMD.addMD(newMD["FID"], newMD["fileName"], newMD["fileSize"], newMD["start"])
            
            #LOOK FOR THE SMALLEST AVAILABLE LOCATION THAT CAN FIT THE FILE
            
            #SEND UPDATED DB
            
            
            
            Files.objects.create(
                                owner=self.obj.owner, 
                                FID = self.obj.FID,
                                SID = "localStorage", 
                                fileName = self.message["fName"], 
                                file = self.obj.file, 
                                actualSize = os.path.getsize(os.path.join(self.message["cwd"],self.message["fName"])),
                                RAIDtype = "NONE",
                                RAIDid = -1     
                                )
def file_toLocalStorage_view(request,id): 
    obj = Files.objects.get(id = id)
    #Testing
    context = {
        "file": obj
    }
    
    
    if request.method == "POST": 
        #-- INSERT COMMANDS HERE --# 
        
        obj =Files.objects.get(id=id)
        cwd = os.path.dirname(obj.file.path)
        url = obj.file.url
        
        
        fName = os.path.split(url)[-1]
        
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        else:
            print("Directory Exists, Proceeding to SFTP")
        #TODO CONNECTED STORAGE NODES
        storageNodeList = getCurrentFileStorageNodes(obj.FID)
        fileList = serverDButil.searchMD([obj.FID])

        print(fileList)
        fileTuple = []
        
        if fileList[0]["RAIDtype"] != "NONE":
            for i in range(1,len(fileList)):
                
                fileName = fileList[i]["fileName"]
                print(fileName)
                fileTuple.append((fileName, storageNodeList[i-1]))
        
        else:
            fileTuple.append((fName, storageNodeList[0]))
            

        
        #GET DATA FROM DB
        message = {
            "fName": fName,
            "FID" : obj.FID,
            "cwd" : cwd,
            "command":"download",
            "RAIDtype": obj.RAIDtype
            }
        context = {
            'button': False
        }

        thread = LocalStoragethread(message,fileTuple,obj)
        thread.start()
        
        return redirect('/')
        
        print(obj.file)
        return redirect('/')
    
    return render(request, 'file-toLocalStorage.html',context)


class retStorthread(threading.Thread):
    def __init__(self, message, fileTuple, obj):
        threading.Thread.__init__(self)
        self.message = message
        
    def run(self):
        
        fileMD = storageNodeMD.searchMD([self.message["FID"]])
        storFolder = "storageFolder"
        storName = "storage"
        storageLoc = os.path.join(storFolder, storName)
        fileToPut = self.message["cwd"]
        
        fileMod.retFile(fileMD, storageLoc, fileToPut)

def file_backToStorageNodes_view(request,id): 
    obj = Files.objects.get(id = id)
    
    context = {
        "file": obj
    }
    
    obj =Files.objects.get(id=id)
    cwd = os.path.dirname(obj.file.path)
    url = obj.file.url
    
    
    fName = os.path.split(url)[-1]
    
    if not os.path.exists(cwd):
        os.mkdir(cwd)
    else:
        print("Directory Exists, Proceeding to SFTP")
    message = {
            "fName": fName,
            "FID" : obj.FID,
            "cwd" : cwd,
            "command":"download",
            }
    
    
    if request.method == "POST": 
        #-- INSERT COMMANDS HERE --# 
        print(obj.file)
        return redirect('/')
    
    return render(request, 'file-backToStorageNodes.html',context)


class unRAIDthread(threading.Thread):
    def __init__(self, message, fileTuple, obj):
        # execute the base constructor
        threading.Thread.__init__(self) 
        self.message  = message
        self.fileTuple = fileTuple
        self.obj = obj
    def run(self):
        
 
        
        thread = download(self.message, self.fileTuple)
        thread.start()
        thread.join()
        
        
        storageNodeList = serverDButil.getAllStorageNodes()
        
        newStorageLoc = storageNodeList[0]
        for i in range(len(storageNodeList)):
            if storageNodeList[i]["maxSize"] > newStorageLoc["maxSize"]:
                newStorageLoc = storageNodeList[i]
        
        # for i in self.fileTuple:
        #     print(i[1]["port"])
        if newStorageLoc["maxSize"] < os.path.getsize(os.path.join(self.message["cwd"],self.message["fName"])):
            print("No more space, cannot un RAID")
        else:
            pass
            for i in self.fileTuple:
                message = {
                    'FID':self.obj.FID,
                    "command":"delete"
                }

                print(i[1]["port"])
                sSFTP.delete(message, i[1])
                
        #serverDButil.delMD([self.message["FID"]])
        
        
        
        Files.objects.create(
                            owner=self.obj.owner, 
                            FID = self.obj.FID,
                            SID = newStorageLoc["SID"], 
                            fileName = self.message["fName"], 
                            file = self.obj.file, 
                            actualSize = os.path.getsize(os.path.join(self.message["cwd"],self.message["fName"])),
                            RAIDtype = "NONE",
                            RAIDid = -1     
                            )
        message = {
                'fName' : self.message["fName"],
                'FID':self.obj.FID,
                "command":"upload",
                "cwd":self.message["cwd"]
            } 

        

def file_UNRAID_view(request,id):
    
    obj =Files.objects.get(id=id)
    cwd = os.path.dirname(obj.file.path)
    url = obj.file.url
    
    
    fName = os.path.split(url)[-1]
    
    if not os.path.exists(cwd):
        os.mkdir(cwd)
    else:
        print("Directory Exists, Proceeding to SFTP")
    #TODO CONNECTED STORAGE NODES
    storageNodeList = getCurrentFileStorageNodes(obj.FID)
    fileList = serverDButil.searchMD([obj.FID])

    print(fileList)
    fileTuple = []
    
    if fileList[0]["RAIDtype"] != "NONE":
        for i in range(1,len(fileList)):
            
            fileName = fileList[i]["fileName"]
            print(fileName)
            fileTuple.append((fileName, storageNodeList[i-1]))
    
    else:
        fileTuple.append((fName, storageNodeList[0]))
        

    
    #GET DATA FROM DB
    message = {
        "fName": fName,
        "FID" : obj.FID,
        "cwd" : cwd,
        "command":"download",
        "RAIDtype": obj.RAIDtype
        }
    context = {
        'button': False
    }
    
 
        
    

    thread = unRAIDthread(message,fileTuple,obj)
    thread.start()
    
    return redirect('/')
   
    ## Files to get all of the files 
    ##
    context ={
        "file":obj
    }
    return render(request,'file-UNRAID.html',context)


def get_status_of_Nodes(request): 
    obj = storageNodeInfo.objects.all() 
    context = {
        "statusInfo_list":obj
    }
    
    return render(request,'get-statusOfNodes.html',context)


############################## Account Portion #############################
def login_view(request): 
    if request.method == "POST": 
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate (request, username=username, password=password)
        if user is None: 
            context = {
                "error": "Invalid username or password"
            }
            return render(request,"accounts/login.html",context)
        login(request,user)
        return redirect('/')
    return render(request,"accounts/login.html",{})

def logout_view(request): 
    if request.method == "POST": 
        logout(request)
        return redirect('/')
    
    return render(request,"accounts/logout.html",{})

def register_view(request): 
    
    form = UserCreationForm(request.POST or None )
    if form.is_valid(): 
        user_obj = form.save()
        return redirect('/login')
    
    return render(request,"accounts/register.html",{"form":form})


@login_required
def user_view(request): 
    users = User.objects.all()
    print(users)
    
    context = {
        "user_list": users
    }
    
    return render(request,'accounts/user.html',context)

@login_required
def deleteUser_view(request, username): 
    try:
        u = User.objects.get(username = username)
        u.delete()
        messages.success(request, "The user is deleted")            

    except User.DoesNotExist:
        messages.error(request, "User doesnot exist")    
        return home_view(request)

    except Exception as e: 
        return home_view(request)

    return home_view(request)