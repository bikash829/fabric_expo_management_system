from django.shortcuts import get_object_or_404, render, redirect

# Create your views here.
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from fabric_expo_management_system.decorators import redirect_authenticated_user
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView,TemplateView
from django.contrib.auth.decorators import login_required
# get user model
from django.contrib.auth import get_user_model
User = get_user_model()

# import forms 
from .forms import ProfilePhotoForm

@method_decorator(redirect_authenticated_user, name='dispatch')
class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class ProfileView(LoginRequiredMixin,TemplateView):
    # model = User
    template_name = 'accounts/profile.html'
    
    # context_object_name = 'user_info'

@login_required
def change_profile_photo(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfilePhotoForm(instance=user)
    return render(request, 'accounts/profile.html', {'change_photo_form': form})