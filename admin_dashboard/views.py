from django.shortcuts import render,HttpResponse
from django.views.generic import TemplateView

# Create your views here.
class IndexView(TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"


class MyView(TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"