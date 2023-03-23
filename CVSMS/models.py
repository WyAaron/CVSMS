from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def file_path(instance,filename): 
    return f'{instance.FID}/{filename}'
class Files(models.Model):
    
    RAID_TYPE_CHOICES = [
        ('NONE', "NONE"),
        ('PARITY', "PARITY"),
        ('1', "1"),
        ('0', "0"),
        
    ]
    #0,1,P default = none 
    owner = models.CharField(User, null=True,blank=True,max_length=300)
    FID = models.IntegerField(null=True)
    SID = models.CharField(null=True,max_length=256)
    fileName = models.CharField(null=True, max_length=256)
    file = models.FileField(null=True,upload_to=file_path)    
    actualSize = models.IntegerField(null=True)
    start = models.IntegerField(null=True)
    RAIDtype = models.CharField(null=True,choices=RAID_TYPE_CHOICES,default="NONE",max_length=7)
    RAIDid = models.IntegerField(null=True,default=-1)
    

class storageNodeStatus(models.Model): 
    SID = models.CharField(null=True, max_length=50)
    port = models.IntegerField()
    status = models.BooleanField(default=False)
    time = models.TimeField()

class storageNodeInfo(models.Model): 
    SID = models.CharField(max_length=50)
    allocSize = models.IntegerField() 
    IP = models.GenericIPAddressField()
    port = models.IntegerField()
    maxSize = models.IntegerField(null=True)
    status = models.BooleanField(default=False)














