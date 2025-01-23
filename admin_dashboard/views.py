from django.shortcuts import render,HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.
class IndexView(LoginRequiredMixin,TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"
    login_url = reverse_lazy('accounts:login')

class MyView(TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"