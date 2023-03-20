from django.urls import path
from .views import home_view,fileSearch_view, login_view, logout_view,register_view,file_Upload_view, file_Download_view,file_Delete_view,file_Retreive_view,file_RAID_view

urlpatterns = [ 
            path('', home_view),
            path('file/', fileSearch_view,name='file'),
            path('file-upload/',file_Upload_view,name='file-upload'),
            path('file-retrieve/<int:id>/', file_Retreive_view,name='file-retrieve'), 
            path("file-download", file_Download_view, name="file-download"), 
            path("file-RAID/<int:id>", file_RAID_view, name="file-RAID"),
            path("file-delete/<int:id>", file_Delete_view, name="file-delete"), 
            path('login/', login_view,name='login'),
            path('logout/', logout_view,name='logout'),
            path('register/', register_view,name='register'),

]



 
