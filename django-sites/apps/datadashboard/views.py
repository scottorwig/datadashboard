from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import Template, Context
from django.template.loader import get_template
from models import *
from forms import *

def index(request):
    debug_string = ''
    title = 'Welcome to the Data Dashboard'
    return render_to_response('dash_home.html',
                              {
                                  'debug_string':debug_string,
                                  'title': title,
                              })