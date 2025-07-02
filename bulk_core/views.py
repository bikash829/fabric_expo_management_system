from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
# from bulk_email.forms import EmailRecipientImportForm
from .models import RecipientCategory
from .forms import CategoryCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

# create category view
class CategoryCreateView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    permission_required = 'bulk_core.add_recipientcategory'
    model = RecipientCategory
    form_class = CategoryCreateForm
    template_name = "bulk_core/category/create_category.html"
    success_url = reverse_lazy('bulk_core:category_list')


    def form_valid(self,form):
        new_name = form.cleaned_data.get('name')
        messages.success(self.request,f'Category "{new_name}" has been created')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Create Recipient Category" 
        context['header_title'] = "Create Recipient's Category" 
        context['submit_button_name'] = "Create Category" 
        context['submit_button_icon'] = "<i class='fa-solid fa-plus'></i>"
        context['form_purpose'] = "create" 
        
        return context

# category details
# class CategoryDetailView(DetailView,LoginRequiredMixin,PermissionRequiredMixin):
#     permission_required = 'bulk_core.view_recipientcategory'
#     model = RecipientCategory
#     template_name = "bulk_core/category/category_details.html"



# category list
class CategoryListView(LoginRequiredMixin,PermissionRequiredMixin, ListView):
    permission_required = 'bulk_core.view_recipientcategory'
    model = RecipientCategory
    template_name = "bulk_core/category/category_list.html"


# category update
class CategoryUpdateView(LoginRequiredMixin,PermissionRequiredMixin, UpdateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Update Recipient Category" 
        context['header_title'] = "Update Recipient's Category" 
        context['submit_button_name'] = "Update Category" 
        context['submit_button_icon'] = '<i class="fa-solid fa-floppy-disk"></i>'
        context['form_purpose'] = "update" 
        
        return context
    
# delete category
class CategoryDeleteView(LoginRequiredMixin,PermissionRequiredMixin, DeleteView):
    permission_required = 'bulk_core.delete_recipientcategory'
    model = RecipientCategory
    success_url = reverse_lazy('bulk_core:category_list')


