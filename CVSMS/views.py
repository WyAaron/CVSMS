import django
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from CVSMS.models import  Files,storageNodeInfo
from .forms import FileForm,RAIDForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

import os 
from django.http import HttpResponse
from django.contrib import messages

import shutil

from django.db.models import Q
# Cr = "eate your views here.



#MODULE IMPORTS

import modules.view.view_tools as view_tools 

import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil
import modules.nodeTools.getTools as NodeGetTools

#SFTP INITIALIZATION TOOLS, INCLUDES THREADING
import modules.sftp.sftp_init_tools as sftp_init_tools

#MODULES FOR RAIDING FILES AND INITIATING ITS SFTP
import modules.sftp.thread_sftp as thread_sftp
import modules.sftp.raid.thread_raid0 as thread_raid0
import modules.sftp.raid.thread_raid1 as thread_raid1
import modules.sftp.raid.thread_praid as thread_praid
#-----------------------------





# Home view of user
@login_required
def home_view(request): 
    user = request.user 
    if user.is_superuser: 
        context = {
        "file_list": Files.objects.filter(RAIDid = -1) , 
        #"file_list": Files.objects.all() ,
        'storageSize': view_tools.get_storageSize(),
        'totalFileSize': view_tools.get_fileTotalSize(),
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
            storageNode = NodeGetTools.getStorageNodes([fName], storageNodeList, cwd)[0]["storageNode"]
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
                    
                    t1 = thread_sftp.SFTPThread(message, storageNode, deleteFolder=True)
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
    storageNodeList = NodeGetTools.getCurrentFileStorageNodes(obj.FID)
    fileList = serverDButil.searchMD([obj.FID])

    
    fileTuple = []
    
    if fileList[0]["RAIDtype"] != "NONE":
        for i in range(1,len(fileList)):
            fileName = fileList[i]["fileName"]
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
        thread = thread_sftp.download(message,fileTuple)
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




                
def file_RAID_view(request,id): 
    
    context = {
    "form": RAIDForm(),
    "file":Files.objects.get(id=id) 
    }
    if request.method == "POST":
        form = RAIDForm(request.POST)
        RAIDtype = request.POST["RAIDtype"]
        obj = Files.objects.get(id=id)
        # storageNode = {        
        #     "SID":1,
        #     "AllocSize":1000,
        #     "MaxSize": 1000,
        #     "IP":"192.168.0.225",
        #     "PORT":5001,
        # }
        
        
        
        
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
        storageNodeList = NodeGetTools.getCurrentFileStorageNodes(file.FID)
        
        
        message = {
            # "fName": fName,
            "FID" : file.FID,
        } 
        t1 = thread_sftp.SFTPThread(message, )   
        # delete.start() 
        {   
        "FID" : file.FID,
        "command" : "delete"
        }
        
        for i in storageNodeList:
            if i != None:
                t1 = thread_sftp.SFTPThread(message, i)   
                t1.start()    

        return redirect('/')
        # return redirect(success_url
    context = {
        "file":file
    }
    return render(request,'file-Delete.html',context)

#TODO: 
def file_toLocalStorage_view(request,id): 
    obj = Files.objects.get(id = id)
    #Testing
    context = {
        "file": obj
    }
    if request.method == "POST": 
        #-- INSERT COMMANDS HERE --# 
        print(obj.file)
        return redirect('/')
    
    return render(request, 'file-toLocalStorage.html',context)

def file_backToStorageNodes_view(request,id): 
    obj = Files.objects.get(id = id)
    
    context = {
        "file": obj
    }
    if request.method == "POST": 
        #-- INSERT COMMANDS HERE --# 
        print(obj.file)
        return redirect('/')
    
    return render(request, 'file-backToStorageNodes.html',context)

#TODO
def file_UNRAID_view(request,id):
    obj = Files.objects.get(id=id)
    print(f'UNRAIDED! {obj}')
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
