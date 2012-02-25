from django import forms
from models import *

class ApplicationForm(forms.ModelForm):
    FileName = forms.CharField(max_length=100)
    File  = forms.FileField()
    class Meta:
        model = BoeApplication
