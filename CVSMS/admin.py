from django.contrib import admin


# Register your models here.

from .models import *

# class CVSMSAdmin(admin.ModelAdmin): 
#     list_display = ['FID', 'fileName']
class FileAdmin(admin.ModelAdmin): 
    list_display = ['owner','id','fName','file','RAIDtype','SID']
class StorageInfoAdmin(admin.ModelAdmin): 
    list_display = ["SID", "AllocSize","SFTPport", "IP","port", ]

# admin.site.register(fileMetadata,CVSMSAdmin)
admin.site.register(Files,FileAdmin)
admin.site.register(storageNodeStatus)
admin.site.register(storageNodeInfo)
# admin.site.register(storageNodeMetadata)





