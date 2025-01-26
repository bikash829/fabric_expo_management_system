from django.shortcuts import render,HttpResponse,redirect
from django.views.generic import TemplateView,FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import StaffUserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
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
        # print(form.cleaned_data)
        obj = form.save(commit=False)
        obj.is_staff = True
        obj.save()
        messages.success(self.request, 'New staff created successfully!')
        return super().form_valid(form)
    
# Show all staff 
class StaffListView(ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"

"""end:: Manage User"""
