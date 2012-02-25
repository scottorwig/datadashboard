from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from models import *
from views import *

class IncidentEntryForm(forms.ModelForm):
    referrer = forms.CharField()
    class Meta:
        model = Incident

class DisciplineActionEntryForm(forms.ModelForm):
    class Meta:
        model = DisciplineAction

