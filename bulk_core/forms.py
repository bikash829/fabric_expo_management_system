from django import forms
from django.forms import ModelForm
from .models import RecipientCategory

class CategoryCreateForm(ModelForm):
    template_name = "bulk_core/form_template/full_width_form.html"

    class Meta:
        model = RecipientCategory
        fields = ['name','description']
        widgets={
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':"3"}),

        }