from django.shortcuts import render,HttpResponse,redirect
from django.views.generic import TemplateView,FormView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import StaffUserCreationForm,StaffChangeForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.models import User
# Create your views here.
class IndexView(LoginRequiredMixin,TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"
    login_url = reverse_lazy('accounts:login')
    

class MyView(TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"


"""begin:: Manage User"""
# Create new staff
class CreateUserView(FormView):
    template_name="admin_dashboard/manage_user/create_user.html"
    form_class = StaffUserCreationForm
    success_url = reverse_lazy('admin_dashboard:create_staff')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        print(self.request.POST)
        print(form.cleaned_data)
        obj = form.save(commit=False)
        obj.is_staff = True
        print(obj)
        obj.save()
        messages.success(self.request, 'New staff created successfully!')
        return super().form_valid(form)


# show staff details 
class StaffDetailsView(DetailView):
    model= get_user_model()
    template_name = "admin_dashboard/manage_user/profile.html"
    context_object_name = 'staff'


# Edit staff
class ChangeUserView(UpdateView):
    model=User
    template_name="admin_dashboard/manage_user/edit_staff.html"
    form_class = StaffChangeForm

    def get_success_url(self):
        return reverse_lazy('admin_dashboard:user_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        if self.object.date_of_birth:
            initial['date_of_birth'] = self.object.date_of_birth.strftime('%Y-%m-%d')
        return initial
    
    
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        form.save()
        messages.success(self.request, 'Staff\'s updated successfully!')
        return super().form_valid(form)
    

# Show all staff 
class StaffListView(ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"


# show staff accounts



"""end:: Manage User"""
