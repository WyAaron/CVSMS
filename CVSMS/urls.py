from django.urls import path
from .views import home_view,fileSearch_view, login_view, logout_view,register_view,file_Upload_view ,file_Delete_view,file_Retreive_view,file_RAID_view,file_UNRAID_view,file_toLocalStorage_view, file_backToStorageNodes_view,get_status_of_Nodes,user_view,deleteUser_view

urlpatterns = [ 
            path('', home_view),
            path('file/', fileSearch_view,name='file'),
            path('file-upload/',file_Upload_view,name='file-upload'),
            path('file-retrieve/<int:id>/', file_Retreive_view,name='file-retrieve'), 
            path("file-RAID/<int:id>", file_RAID_view, name="file-RAID"),
            path("file-UNRAID/<int:id>", file_UNRAID_view, name="file-UNRAID"),
            path("file-delete/<int:id>", file_Delete_view, name="file-delete"), 
            path("file-toLocalStorage/<int:id>", file_toLocalStorage_view, name="file-toLocalStorage"),
            path("file-backToStorageNodes/<int:id>", file_backToStorageNodes_view, name="file-backToStorageNodes"),
            path('get-statusOfNodes', get_status_of_Nodes, name="get-statusOfNodes"),
            path('login/', login_view,name='login'),
            path('logout/', logout_view,name='logout'),
            path('register/', register_view,name='register'),
            path('user/',user_view, name="user"), 
            path('delete/<str:username>',deleteUser_view,name="delete")
]