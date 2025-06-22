import pprint
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView,FormView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.urls import reverse_lazy

from bulk_email.models import EmailSession, SentMail
from bulk_whatsapp.models import SentMessage
from business_data.models import Buyer, Product, Supplier
from .forms import GroupForm, StaffUserCreationForm,StaffChangeForm, UserPermissionForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.models import User
from django.contrib.auth.models import Group
from django.http import JsonResponse
import random
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now


class IndexView(LoginRequiredMixin,TemplateView):
    template_name= "admin_dashboard/pages/dashboard.html"
    login_url = reverse_lazy('accounts:login')


"""begin:: Manage User"""
# Create new staff
class CreateUserView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = "accounts.add_user"
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
class StaffDetailsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "accounts.view_user"
    model= get_user_model()
    template_name = "admin_dashboard/manage_user/profile.html"
    context_object_name = 'staff'



# Edit staff
class ChangeUserView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "accounts.change_user"
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
class ManageUserPermissionView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "auth.change_permission"
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/manage_permissions.html"
    form_class = UserPermissionForm

    def get_success_url(self):
        """
        Redirects to the referring page if available; otherwise, reloads the form page.
        """
        return self.request.META.get("HTTP_REFERER") or reverse_lazy("admin_dashboard:user_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Permissions have been updated successfully!")
        return super().form_valid(form)
    

# Delete staff 
class DeleteStaffView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "accounts.delete_user"
    model = get_user_model()
    success_url = reverse_lazy("admin_dashboard:staff_list")
    
    
### ============= Activate and deactivate user account =================
class ToggleStaffActivationMixin(View):
    permission_required = "accounts.can_activate_deactivate_account"
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
class DeactivateStaffView(LoginRequiredMixin, PermissionRequiredMixin, ToggleStaffActivationMixin):
    permission_required = "accounts.can_activate_deactivate_account"
    is_active = False
    success_url = reverse_lazy("admin_dashboard:inactive_users")

# Activate Staff View
class ActivateStaffView(LoginRequiredMixin, PermissionRequiredMixin, ToggleStaffActivationMixin):
    permission_required = "accounts.can_activate_deactivate_account"
    is_active = True
    success_url = reverse_lazy("admin_dashboard:active_users")  # Custom success URL


# show active user list 
class ActiveUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "accounts.can_view_active_inactive_users"
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"

    
    def get_queryset(self):
        return self.model.objects.filter(is_active=True)


# show deactivated user list 
class DeactivatedUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "accounts.can_view_active_inactive_users"
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"
    
    def get_queryset(self):
        return self.model.objects.filter(is_active=False)
### ============= ./ Activate and deactivate user account =================


# show all superuser list
class SuperuserListView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"
    
    def get_queryset(self):
        return self.model.objects.filter(is_superuser=True)

# Show all staff 
class StaffListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "accounts.view_user"
    model = get_user_model()
    template_name = "admin_dashboard/manage_user/staff_list.html"

    def get_queryset(self):
        return self.model.objects.filter(is_superuser=False).exclude(pk=self.request.user.pk)

"""end:: Manage User"""



"""begin:: Groups and Permissions"""
# create/add new group 
class CreateGroupView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "auth.add_group"
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
    
# show group list 
class GroupListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "auth.view_group"
    model = Group
    template_name = "admin_dashboard/manage_groups_and_permissions/group-list.html"


    
# change/update groups and permissions info
class UpdateGroupPermission(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "auth.change_group"
    model = Group
    template_name = "admin_dashboard/manage_groups_and_permissions/group-form.html"
    form_class = GroupForm

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


# delete group 
class DeleteGroupView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "auth.delete_group"
    model = Group
    success_url = reverse_lazy("admin_dashboard:group-list")
    
"""end:: Groups and Permissions"""


"""start::chart data"""
# user summary 
class UserSummaryDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs ):
        labels = []
        data = []
        background_color = set()

        # Helper to generate a unique random RGB color
        def unique_rgb_color(existing_colors):
            while True:
                color = f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})"
                if color not in existing_colors:
                    existing_colors.add(color)
                    return color

        # total user 
        User = get_user_model()    
        total_user = User.objects.count()
        labels.append('Total User')
        data.append(total_user)
        unique_rgb_color(background_color)

        # Get group counts in one query
        group_counts = (
            Group.objects.annotate(user_count=Count('user'))
            .values_list('name', 'user_count')
        )

        for group_name, user_count in group_counts:
            labels.append(group_name)
            data.append(user_count)
            unique_rgb_color(background_color)

        return JsonResponse({
            'labels': labels,
            'data': data,
            'background_color': list(background_color),
        })
    
# Buyer and Suppliers summary 
class BuyerAndSupplierSummaryDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs ):
        labels = []
        data = []
        background_color = set()

        # Helper to generate a unique random RGB color
        def unique_rgb_color(existing_colors):
            while True:
                color = f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})"
                if color not in existing_colors:
                    existing_colors.add(color)
                    return color

        # total buyers     
        total_buyers = Buyer.objects.count()
        labels.append('Total Buyers')
        data.append(total_buyers)
        unique_rgb_color(background_color)

        # total suppliers     
        total_suppliers = Supplier.objects.count()
        labels.append('Total Supplier')
        data.append(total_suppliers)
        unique_rgb_color(background_color)

        # total local buyers
        total_local_buyers = Buyer.objects.filter(country_of_origin__iexact="bangladesh").count()
        labels.append('Local Buyers')
        data.append(total_local_buyers)
        unique_rgb_color(background_color)

        # total local suppliers 
        total_local_suppliers = Supplier.objects.filter(country_of_origin__iexact="bangladesh").count()
        labels.append('Local Suppliers')
        data.append(total_local_suppliers)
        unique_rgb_color(background_color)


        return JsonResponse({
            'labels': labels,
            'data': data,
            'background_color': list(background_color),
        })



class FabricOverviewDataView(View):
    def get(self, request, *args, **kwargs):
        # Example: You can add filters based on request.GET later
        fabric_counts = Product.objects.values('composition').annotate(count=Count('id')).order_by('-count')
        supplier_types = Product.objects.values('fabric_mill_supplier').annotate(count=Count('id')).order_by('-count')
        country_origin = Product.objects.values('coo').annotate(count=Count('id')).order_by('-count')

        return JsonResponse({
            'fabric_counts': list(fabric_counts),
            'supplier_types': list(supplier_types),
            'country_origin': list(country_origin),
        })
    

# qr code activity 
class QrCodeActivityDataView(View):
    def get(self, request, *args, **kwargs):
        period = request.GET.get('period', 'week')  # Default to weekly
        end_date = timezone.now().date()

        if period == 'month':
            # Monthly data for last 12 months
            start_date = end_date - timedelta(days=365)
            data = (
                Product.objects
                .filter(date__gte=start_date)
                .annotate(period=TruncMonth('date'))
                .values('period')
                .annotate(count=Count('id'))
                .order_by('period')
            )
            
            # Generate all months in range (including empty ones)
            labels = []
            data_points = []
            current_month = end_date.replace(day=1)
            
            for i in range(12):
                month = current_month - timedelta(days=30*i)
                month = month.replace(day=1)
                labels.insert(0, month.strftime('%b %Y'))
                count = next(
                    (item['count'] for item in data 
                    if item['period'].replace(day=1) == month),  # Removed .date()
                    0
                )
                data_points.insert(0, count)
                
        else:
            # Weekly data for last 12 weeks
            start_date = end_date - timedelta(weeks=24)
            data = (
                Product.objects
                .filter(created_at__gte=start_date)
                .annotate(period=TruncWeek('created_at'))
                .values('period')
                .annotate(count=Count('id'))
                .order_by('period')
            )
            
            # Generate all weeks in range (including empty ones)
            labels = []
            data_points = []
            
            for i in range(24):
                week_start = end_date - timedelta(weeks=(23-i))
                week_start = week_start - timedelta(days=week_start.weekday())  # Start of week (Monday)
                labels.append(f"Week {week_start.isocalendar()[1]} ({week_start.strftime('%Y-%m-%d')})")
                count = next(
                    (item['count'] for item in data 
                    if item['period'] == week_start),  # Removed .date()
                    0
                )
                data_points.append(count)
        
        return JsonResponse({
            'labels': labels,
            'data': data_points,
            'period': period
        })
    

# communication tracker 
class CommunicationTrackerDataView(View):
    def get(self, request, *args, **kwargs):

        end_date = now().date()
        start_date = end_date - timedelta(days=29)

        # Prepare date labels for the last 30 days
        labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

        # Get email counts per day
        email_counts = (
            SentMail.objects.filter(sent_at__date__range=(start_date, end_date))
            .extra({'date': "date(sent_at)"})
            .values('date')
            .annotate(count=Count('id'))
        )
        email_data_map = {item['date']: item['count'] for item in email_counts}

        # Get whatsapp counts per day
        whatsapp_counts = (
            SentMessage.objects.filter(sent_at__date__range=(start_date, end_date))
            .extra({'date': "date(sent_at)"})
            .values('date')
            .annotate(count=Count('id'))
        )
        whatsapp_data_map = {item['date']: item['count'] for item in whatsapp_counts}

        # Prepare data lists aligned with labels
        email_data = [email_data_map.get(label, 0) for label in labels]
        whatsapp_data = [whatsapp_data_map.get(label, 0) for label in labels]

        return JsonResponse({
            'labels': labels,
            'email_data': email_data,
            'whatsapp_data': whatsapp_data,
        })

"""end::chart data"""
