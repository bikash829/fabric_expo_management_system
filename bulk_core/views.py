from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView,DetailView

from bulk_email.forms import EmailRecipientImportForm
from .models import RecipientCategory, RecipientDataSheet
from .forms import CategoryCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
# Create your views here.


# create category view
class CategoryCreateView(CreateView,LoginRequiredMixin,PermissionRequiredMixin):
    permission_required = 'bulk_core.add_recipientcategory'
    model = RecipientCategory
    form_class = CategoryCreateForm
    template_name = "bulk_core/category/create_category.html"
    success_url = reverse_lazy('bulk_core:category_list')


    def form_valid(self,form):
        new_name = form.cleaned_data.get('name')
        messages.success(self.request,f'Category "{new_name}" has been created')
        return super().form_valid(form)


# category details
# class CategoryDetailView(DetailView,LoginRequiredMixin,PermissionRequiredMixin):
#     permission_required = 'bulk_core.view_recipientcategory'
#     model = RecipientCategory
#     template_name = "bulk_core/category/category_details.html"



# category list
class CategoryListView(ListView,LoginRequiredMixin,PermissionRequiredMixin):
    permission_required = 'bulk_core.view_recipientcategory'
    model = RecipientCategory
    template_name = "bulk_core/category/category_list.html"


# category update
class CategoryUpdateView(UpdateView,LoginRequiredMixin,PermissionRequiredMixin):
    permission_required = 'bulk_core.change_recipientcategory'
    model = RecipientCategory
    form_class = CategoryCreateForm
    template_name = "bulk_core/category/create_category.html"
    success_url = reverse_lazy('bulk_core:category_list')
    

    def form_valid(self,form):
        old_name = self.get_object().name
        new_name = form.cleaned_data.get('name')
        messages.success(self.request,f'Category updated from {old_name} to {new_name}')
        return super().form_valid(form)

    
# delete category
class CategoryDeleteView(DeleteView,LoginRequiredMixin,PermissionRequiredMixin):
    permission_required = 'bulk_core.delete_recipientcategory'
    model = RecipientCategory
    success_url = reverse_lazy('bulk_core:category_list')


# import email 
class ImportEmailView(CreateView):
    model = RecipientDataSheet
    from_class = EmailRecipientImportForm 