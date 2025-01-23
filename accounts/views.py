from django.shortcuts import render

# Create your views here.
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from fabric_expo_management_system.decorators import redirect_authenticated_user
from django.utils.decorators import method_decorator

@method_decorator(redirect_authenticated_user, name='dispatch')
class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True