from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from CVSMS.models import  Files
from .forms import FileForm
from django.shortcuts import get_object_or_404
import sSFTP
import os 
import pathlib
# Create your views here.




# Home view of user
@login_required
def home_view(request):  
    context = {
        "file_list": Files.objects.filter(owner=request.user),
    }
    print(f'{Files.objects.get_queryset()}')
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
            obj = Files.objects.create(owner=request.user, fileName= request.FILES["file"],file=request.FILES['file'],actualSize=request.FILES["file"].size,FID=FID)
            #TODO CONNECTED STORAGE NODES
            storageNode = {
                
                "SID":1,
                "AllocSize":1000,
                "IP":"192.168.1.21",
                "PORT":5001,
            }
            
            cwd = os.path.dirname(obj.file.path)
            fName = os.listdir(cwd)[0]

            message = {
            "fName": fName,
            "FID" : obj.FID,
            "cwd" : cwd,
            "command":"upload"
            }
            #TODO: upload to Storage Node
            
            try:
                
                sSFTP.upload(message, storageNode)
                success = True
                
            except Exception as e:
                #Todo Function when false it must delete file from db 
                success = False
            
            
            #CREATE DB ENTRY FOR FILE SAVED
            
        return redirect('/')
    else:
        form = FileForm()
    return render(request,'file-Upload.html',context=context)

#### File download request 
@login_required
def file_Download_view(request): 
    
    
        # sSFTP.download(message,storageNode)
        
        
    # file_server = pathlib.Path()
    # if request.method == "GET": 
    #     file_download = get_object_or_404(Files, pk = id )
    #     response = HttpResponse(file_download.file, content_type='application/pdf')
    #     response['Content-Disposition'] =f'attactments; filename="{file_download.fileName}"' 
    #     return response 
    return render(request,'file-Download.html', {})    

def file_Retreive_view(request,id): 
    context = {
        "file": Files.objects.get(id=id)
    }
    obj =Files.objects.get(id=id)
    cwd = os.path.dirname(obj.file.path)
    url = obj.file.url
    if  "/" in url :
        urlList = url.split("/")
        splitChar = "/"
    else:
        urlList = url.split("\\")
        splitChar = "\\"
    
    fName = urlList[len(urlList)-1]

    #TODO CONNECTED STORAGE NODES
    storageNode = {        
            "SID":1,
            "AllocSize":1000,
            "IP":"192.168.1.21",
            "PORT":5001,
        }
    #GET DATA FROM DB
    message = {
        "fName": fName,
        "FID" : obj.FID,
        "cwd" : cwd,
        "command":"download"
            }
    context = {
        'button': False
    }
    # return True 

    # return False
    if not os.path.isFile(cwd+splitChar+fName):
        sSFTP.download()
        # alert("file started downloading)


    elif os.path.isFile(cwd+splitChar+fName):
        if os.path.getsize(cwd+splitChar+fName) == obj.actualSize:
            return render(request,'file-Download.html',{})
        else:
            pass
            # alert("file is downloading)
        # render(request,'fil.html',context=context)
    
    
    return render(request,'/',{})

    


def file_Delete_view(request, id=None): 
    file_delete = get_object_or_404(Files, id=id, owner=request.user)
    
    if request.method == "POST": 
        file_delete.delete()
        # success_url = reverse('/')
        # return redirect(success_url)
    context={
        "file": file_delete
    }
    return render(request,'file-delete.html',context=context)


    

############################## Account portion #############################
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

