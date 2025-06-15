# Django core imports
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib import messages

# Django authentication imports
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Django utilities and decorators
from django.utils.decorators import method_decorator

# Django generic views
from django.views.generic import TemplateView, UpdateView

# Project-specific imports
from fabric_expo_management_system.decorators import redirect_authenticated_user

# Local app imports
from .forms import CustomUserChangeForm, ProfilePhotoForm, UserEmailUpdateForm

# Get the custom user model
User = get_user_model()

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



class EmailChangeView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "accounts/manage_account/change_email.html"
    success_url=reverse_lazy("accounts:profile")
    form_class = UserEmailUpdateForm

    # pass user instance to the form
    def get_form_kwargs(self):
        kwargs = super(EmailChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # check field validation
    def form_valid(self, form):
        messages.success(self.request, "Your email has been updated successfully.")
        return super().form_valid(form)


class UsernameChangeView(UpdateView):
    pass 



class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "accounts/manage_account/change_profile.html"
    success_url = reverse_lazy('accounts:profile')


    def form_valid(self,form):
        messages.success(self.request,"Your profile has been updated successfully")
        return super().form_valid(form)