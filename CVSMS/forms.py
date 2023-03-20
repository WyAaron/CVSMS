from django import forms 
from django.forms import ModelForm
from .models import Files   




    
class FileForm(ModelForm): 
    class Meta:
        model = Files
        fields = ['file']