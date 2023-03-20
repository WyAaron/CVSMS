from django.contrib import admin


# Register your models here.

from .models import Files

# class CVSMSAdmin(admin.ModelAdmin): 
#     list_display = ['FID', 'fileName']
class FileAdmin(admin.ModelAdmin): 
    list_display = ['id','fileName','file']

# admin.site.register(fileMetadata,CVSMSAdmin)
admin.site.register(Files,FileAdmin)


