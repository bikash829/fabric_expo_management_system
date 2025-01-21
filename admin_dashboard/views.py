from django.shortcuts import render,HttpResponse
from django.views.generic import TemplateView

# Create your views here.
class IndexView(TemplateView):
    template_name= "_base.html"