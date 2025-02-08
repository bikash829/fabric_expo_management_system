from django.http import JsonResponse,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,HttpResponse,redirect
from django.views import View
from django.views.generic import TemplateView,FormView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import GroupForm, StaffUserCreationForm,StaffChangeForm, UserPermissionForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.models import User
from django.contrib.auth.models import Group, Permission

# Create your views here.
class IndexView(LoginRequiredMixin,TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"
    login_url = reverse_lazy('accounts:login')
    

class MyView(TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"



"""begin:: Manage User"""
# Create new staff
class CreateUserView(LoginRequiredMixin,FormView):
    template_name="admin_dashboard/manage_user/create_user.html"
    form_class = StaffUserCreationForm
    success_url = reverse_lazy('admin_dashboard:create_staff')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        obj = form.save(commit=False)
        obj.is_staff = True
        obj.save()
        messages.success(self.request, 'New staff created successfully!')
        return super().form_valid(form)


# show staff details 
class StaffDetailsView(DetailView,LoginRequiredMixin):
    model= get_user_model()
    template_name = "admin_dashboard/manage_user/profile.html"
    context_object_name = 'staff'


# Edit staff
class ChangeUserView(LoginRequiredMixin,UpdateView):
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
    


# manage permissions
class ManageUserPermissionView(LoginRequiredMixin,UpdateView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/manage_permissions.html"
    form_class = UserPermissionForm

    # def get_success_url(self):
    #     return reverse_lazy("admin_dashboard:user_detail", kwargs={"pk": self.object.pk})
    
    def get_success_url(self):
        """
        Redirects to the referring page if available; otherwise, reloads the form page.
        """
        return self.request.META.get("HTTP_REFERER") or reverse_lazy("admin_dashboard:user_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Permissions have been updated successfully!")
        return super().form_valid(form)
    

# Delete staff 
class DeleteStaffView(LoginRequiredMixin,DeleteView):
    model = get_user_model()
    success_url = reverse_lazy("admin_dashboard:staff_list")
    
    # def get(self, request, *args, **kwargs):
    #     # Override the GET method to directly delete the object without a confirmation page.
    #     self.object = self.get_object()
    #     self.object.delete()
    #     return redirect(self.success_url)
    
### ============= Activate and deactivate user account =================
class ToggleStaffActivationView(View):
    is_active = None  # Set this in the subclasses
    success_url = reverse_lazy("admin_dashboard:staff_list")  # Default success URL

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        user.is_active = self.is_active
        user.save()

        status = "activated" if self.is_active else "deactivated"
        message_type = messages.SUCCESS if self.is_active else messages.WARNING
        messages.add_message(request, message_type, f"Staff account for {user.username} has been {status}!")

        return self.handle_success_url(request)

    def handle_success_url(self, request):
        return redirect(self.success_url)
    

# Deactivate Staff View
class DeactivateStaffView(LoginRequiredMixin,ToggleStaffActivationView):
    is_active = False
    success_url = reverse_lazy("admin_dashboard:inactive_users")

# Activate Staff View
class ActivateStaffView(LoginRequiredMixin,ToggleStaffActivationView):
    is_active = True
    success_url = reverse_lazy("admin_dashboard:active_users")  # Custom success URL

# show active user list 
class ActiveUserListView(LoginRequiredMixin,ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"
    
    def get_queryset(self):
        return self.model.objects.filter(is_active=True)


# show deactivated user list 
class DeactivatedUserListView(LoginRequiredMixin,ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"
    
    def get_queryset(self):
        return self.model.objects.filter(is_active=False)
### ============= ./ Activate and deactivate user account =================


# show all suepruser list
class SuperuserListView(LoginRequiredMixin,ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"
    
    def get_queryset(self):
        return self.model.objects.filter(is_superuser=True)

# Show all staff 
class StaffListView(LoginRequiredMixin,ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"

    def get_queryset(self):
        return self.model.objects.filter(is_superuser=False)

"""end:: Manage User"""



"""begin:: Groups and Permissions"""
class GroupListView(LoginRequiredMixin,ListView):
    model = Group
    template_name = "admin_dashboard/manage_groups_and_permissions/group-list.html"


class CreateGroupView(LoginRequiredMixin,CreateView):
    model = Group
    form_class=GroupForm
    template_name = "admin_dashboard/manage_groups_and_permissions/group-form.html"
    success_url = reverse_lazy("admin_dashboard:group-list")
    
    
    # custom context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Group'
        context['page_title'] = 'Create New Group'
        context['form_title'] = 'Group Creation Form'
        return context
    
    
    def form_valid(self,form):
        messages.success(self.request, f"Group {form.cleaned_data['name']} created successfully!")
        return super().form_valid(form)

    


class UpdateGroupPermission(LoginRequiredMixin,UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "admin_dashboard/manage_groups_and_permissions/group-form.html"
    # success_url = reverse_lazy("admin_dashboard:group-list")

    # custom context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Group'
        context['page_title'] = 'Change Group'
        context['form_title'] = 'Group Change Form'
        return context


    def get_success_url(self):
        """
        Redirects to the referring page if available; otherwise, reloads the form page.
        """
        # group_name = self.object.name
        # messages.success(self.request, f"Group permissions of {group_name} have been updated successfully!")
        return self.request.META.get('HTTP_REFERER', self.success_url)
    
    def form_valid(self,form):
        messages.success(self.request, "Group permissions updated successfully.")
        return super().form_valid(form)

class DeleteGroupView(LoginRequiredMixin,DeleteView):
    model = Group
    success_url = reverse_lazy("admin_dashboard:group-list")
"""end:: Groups and Permissions"""

