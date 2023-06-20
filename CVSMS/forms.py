from django import forms 
from django.forms import ModelForm
from .models import Files   
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



    
class FileForm(ModelForm): 
    class Meta:
        model = Files
        fields = ['file']
        
class RAIDForm(ModelForm): 
    
    class Meta: 
        model = Files
        fields = ['RAIDtype']

# class UserRegistrationForm(UserCreationForm): 

#     username = forms.CharField(widget=forms.TextInput(attrs={
#         "class":"input", 
#         "type": "text", 
#         "placeholder": "Enter Username"
#     }), label="Username")

#     password1 = forms.CharField(widget=forms.TextInput(attrs={
#         "class":"input", 
#         "type": "password", 
#         "placeholder": "Enter Password"
#     }))

#     password2 = forms.CharField(widget=forms.TextInput(attrs={
#         "class":"input", 
#         "type": "password", 
#         "placeholder": "Enter Password"
#     }))

    
#     class Meta: 
#         models = User
#         fields = ['username','password1','password2' ]