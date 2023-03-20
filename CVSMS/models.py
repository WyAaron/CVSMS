from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class storageNode(models.Model): 
    pass

class userInfo(models.Model): 
    pass 

class heartBeat(models.Model): 
    pass

def file_path(instance,filename): 
    return f'{instance.FID}/{filename}'



class Files(models.Model): 
    owner = models.CharField(User, null=True,blank=True,max_length=300)
    FID = models.IntegerField(null=True)
    SID = models.IntegerField(null=True)
    fileName = models.CharField(null=True, max_length=300)
    file = models.FileField(null=True,upload_to=file_path)    
    actualSize = models.IntegerField(null=True)
    start = models.IntegerField(null=True)
    RAIDtype = models.IntegerField(null=True,default=-1)
    RAIDid = models.IntegerField(null=True,default=-1)
    

