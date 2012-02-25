from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import Template, Context
from django.template.loader import get_template
from models import *
from forms import *

def index(request):
    return HttpResponse("This is the index page")