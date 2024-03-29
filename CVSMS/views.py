import django
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from CVSMS.models import Files, storageNodeInfo
from .forms import FileForm, RAIDForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

import os
from django.http import HttpResponse
from django.contrib import messages

import shutil

import threading


from django.db import models

# Cr = "eate your views here.


# MODULE IMPORTS

import modules.view.view_tools as view_tools

import modules.RAIDmod as RAIDmod
import modules.sqlite3.serverDButil as serverDButil
import modules.nodeTools.getTools as NodeGetTools

# SFTP INITIALIZATION TOOLS, INCLUDES THREADING
import modules.sftp.sftp_tools as sftp_tools

# MODULES FOR RAIDING FILES AND INITIATING ITS SFTP
import modules.sftp.thread_sftp as thread_sftp
import modules.sftp.raid.raid0_tools as raid0_tools
import modules.sftp.raid.raid1_tools as raid1_tools
import modules.sftp.raid.parity_tools as parity_tools
import modules.archive.archive_tools as archive_tools
# -----------------------------


# Home view of user
@login_required
def home_view(request):
    view_tools.get_AvailabilityInCache()
    user = request.user
    if user.is_superuser:
        context = {
            "file_list": Files.objects.filter(RAIDid=-1),
            # "file_list": Files.objects.all() ,
            'storageSize': view_tools.get_storageSize(),
            'totalFileSize': view_tools.get_fileTotalSize(),
            'storageNodes': storageNodeInfo.objects.all()

        }
    else:
        context = {
            "file_list": Files.objects.filter(owner=request.user, RAIDid=-1),
        }

    return render(request, 'home-view.html', context=context)


# TODO: dashboard for admin

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
    query_dict = request.GET
    query = query_dict.get('q')

    try:
        query = int(query_dict.get('q'))
    except:
        query = None
    file_obj = None
    if query is not None:
        file_obj = Files.objects.get(id=query)
    context = {
        "object": file_obj
    }
    return render(request, 'search.html', context=context)

    # block for a moment
    # display a message

# Uploading of file


@login_required
def file_Upload_view(request):
    context = {
        "form": FileForm()
    }
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():

            # # #TODO CONNECTED STORAGE NODES
            obj = Files.objects.create(
                owner=request.user,
                fName=request.FILES["file"].name,
                actualSize=request.FILES["file"].size,
                isCached=False)
            # print(request.FILES["file"].name)

            serverDButil.addFID(obj.id, obj.id)

            obj = Files.objects.get(id=obj.id)
            print(f'file -  {request.FILES["file"]}')
            obj.file = request.FILES['file']

            obj.save()

            FID = obj.id

            cwd = os.path.dirname(obj.file.path)
            fName = os.listdir(cwd)[0]

            storageNode = NodeGetTools.get_storage_nodes([fName], cwd)
            
            # print(storageNode)
            
            if storageNode:
                storageNode = storageNode[0]["storage_info"]
                # GET FILE START BYTE
                start = storageNode["Gap"][0]

                # SET THE START BYTE IF THE FILE
                obj.start = start
                obj.save()

                #print(start)

                storageNode = storageNode["storageNode"]
                serverDButil.addStorageNode(storageNode["SID"], FID)

                message = {
                    "fName": fName,
                    "FID": FID,
                    "cwd": cwd,
                    "size": obj.actualSize,
                    "start": obj.start,
                    "command": "upload"
                }

                try:
                    
                    sftpClass = thread_sftp.SFTPThread(message, storageNode)
                    
                    t1 = threading.Thread(target = sftpClass.run())
                    t1.start()
                    
                    messages.info(request, f'File has been uploaded!')

                except Exception as e:
                    # Todo Function when false it must delete file from db
                    print(e)
                    serverDButil.delMD(FID)
                    shutil.rmtree(cwd)
            else:
                serverDButil.delMD(FID)
                shutil.rmtree(cwd)
                messages.info(request, "There is not enough space")

        return redirect('/')
    else:
        form = FileForm()
    return render(request, 'file-Upload.html', context=context)


def file_Retreive_view(request, id):

    context = {
        "file": Files.objects.get(id=id)
    }
    obj = Files.objects.get(id=id)
    cwd = os.path.dirname(obj.file.path)
    url = obj.file.url

    fName = serverDButil.getFileMD(obj.FID)[0]["fName"]


   
    # TODO CONNECTED STORAGE NODES

    context = {
        'button': False
    }
    #DOWNLOAD IF FILE IS NOT IN SERVER
    if not os.path.isfile(os.path.join(cwd, fName)):  
        
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        else:
            print("Directory Exists, Proceeding to SFTP")
            
        messages.info(request, f'file started downloading from storage node.')
        # create the thread
        
        if obj.SID == "ARCHIVE":
            print("RETRIEVING ARCHIVE FILES")
            
            archive = archive_tools.archive_get(obj)
            archive.start()
         
        
        elif obj.RAIDtype == "NONE":
            # GET DATA FROM DB
            fileMD = serverDButil.getFileMD(obj.FID)[0]
            storageNode = serverDButil.getStorageNode(fileMD["SID"])
            message = {
                "fName": obj.fName,
                "FID": obj.FID,
                "cwd": cwd,
                "command": "download",
                "size": obj.actualSize,
                "start": obj.start,
                "RAIDtype": obj.RAIDtype
            }
            thread = thread_sftp.standard_get(message, fName, storageNode)
            # start the thread
            thread.start()
        
        
        elif obj.RAIDtype == "0":
            print("DOWNLOADING RAID 0 FILES")
            raid_get_thread = raid0_tools.thread_get(obj)
            raid_get_thread.start()

        elif obj.RAIDtype == "1":
            print("DOWNLOADING RAID 1 FILES")
            raid_get_thread = raid1_tools.thread_get(obj)
            raid_get_thread.start()

        else:
            print("DOWNLOADING pRAID FILES")
            raid_get_thread = parity_tools.thread_get(obj)
            raid_get_thread.start()

        return redirect('/')

        # t1.start()

        # disable download button
    # condition if file is in server already
    elif os.path.isfile(os.path.join(cwd, fName)):
        # File complete download from storage node
        if os.path.getsize(os.path.join(cwd, fName)) == obj.actualSize:
            if request.method == "GET":
                file_download = get_object_or_404(Files, pk=id)
                file_download.file.name = f'{id}/{file_download.fName}'
                response = HttpResponse(
                   file_download.file  , content_type='application/octet-stream')
                response['Content-Disposition'] = f'attactments; filename = {file_download.fName} '
                return response
        else:  # file is downloading from storage node
            messages.info(request, f'file is downloading')

    return redirect('/')


def file_RAID_view(request, id):

    context = {
        "form": RAIDForm(),
        "file": Files.objects.get(id=id)
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
            t1 = thread_sftp.raidPut(obj, RAIDtype)
            t1.start()

            return redirect('/')
        else:
            form = RAIDForm()
    return render(request, 'file-RAID.html', context=context)


def file_Delete_view(request, id):
    obj = Files.objects.get(id=id)

    if request.method == "POST":

        serverDButil.delMD(obj.FID)
        cwd = os.path.dirname(obj.file.path)

        if os.path.exists(cwd):
            shutil.rmtree(cwd)
        return redirect('/')
    context = {
        "file": obj
    }

    return render(request, 'file-Delete.html', context)

# TODO:


def file_toLocalStorage_view(request, id):
    obj = Files.objects.get(id=id)
    # Testing
    context = {
        "file": obj
    }
    if request.method == "POST":
        # -- INSERT COMMANDS HERE --#
        print("STARTING ARCHIVE")
        # if obj.SID == "ARCHIVE":
        #     print("FILE IS ALREADY IN ARCHIVE")
        #     unarchive = archive_tools.unarchive(obj)
        #     unarchive.start()
        # else:
        archive = archive_tools.archive_put(obj)
        archive.start()

        
        
        return redirect('/')

    return render(request, 'file-toLocalStorage.html', context)


def file_backToStorageNodes_view(request, id):
    obj = Files.objects.get(id=id)

    context = {
        "file": obj
    }
    if request.method == "POST":
        # -- INSERT COMMANDS HERE --#
        #print(obj.file)
        
        unarchive = archive_tools.unarchive(obj)
        unarchive.start()
        
        return redirect('/')

    return render(request, 'file-backToStorageNodes.html', context)

# TODO


def file_UNRAID_view(request, id):
    obj = Files.objects.get(id=id)

    cwd = os.path.dirname(obj.file.path)
    # CHECK IF THE DIRECTORY FOR THE SFTP EXISTS
    if not os.path.exists(cwd):
        os.mkdir(cwd)
        return redirect('/')
    else:
        print("Directory Exists, Proceeding to SFTP")
        

    if request.method == "POST":
        if obj.RAIDtype == "0":
            print("UNRAIDING RAID 0")
            t1 = raid0_tools.thread_unraid(obj)
            t1.start()
            return redirect('/')
        elif obj.RAIDtype == "1":
            print("UNRAIDING RAID 1")
            t1 = raid1_tools.thread_unraid(obj)
            t1.start()
            return redirect('/')
        elif obj.RAIDtype == "PARITY":
            t1 = parity_tools.thread_unraid(obj)
            t1.start()
            return redirect('/')

    context = {
        "file": obj
    }

    return render(request, 'file-UNRAID.html', context)


def get_status_of_Nodes(request):
    obj = storageNodeInfo.objects.all()
    context = {
        "statusInfo_list": obj
    }

    return render(request, 'get-statusOfNodes.html', context)


############################## Account Portion #############################
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            context = {
                "error": "Invalid username or password"
            }
            return render(request, "accounts/login.html", context)
        login(request, user)
        return redirect('/')
    return render(request, "accounts/login.html", {})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('/')

    return render(request, "accounts/logout.html", {})


def register_view(request):

    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        new_user = authenticate(
            username = form.cleaned_data['username'],
            password = form.cleaned_data['password1']
        )
        login(request,new_user)
        return redirect('/')

    return render(request, "accounts/register.html", {"form": form})


@login_required
def user_view(request):
    users = User.objects.all()
    print(users)

    context = {
        "user_list": users
    }

    return render(request, 'accounts/user.html', context)


@login_required
def deleteUser_view(request, username):
    try:
        u = User.objects.get(username=username)
        serverDButil.deleteUserFiles(username)
        u.delete()
        messages.success(request, "The user is deleted")

    except User.DoesNotExist:
        messages.error(request, "User doesnot exist")
        return home_view(request)

    except Exception as e:
        return home_view(request)

    return home_view(request)
