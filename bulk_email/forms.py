from django import forms
from django.forms import ModelForm, ValidationError
from .models import RecipientCategory, EmailTemplate, EmailAttachment
from bulk_core.models import RecipientDataSheet,RecipientCategory,TempRecipientDataSheet


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        max_total_size = 20 * 1024 * 1024  # 20 MB in bytes
        files = data if isinstance(data, list) else [data]

        total_size = sum(file.size for file in files)
        if total_size > max_total_size:
            raise ValidationError(f"One or more files exceed the 20MB size limit.")
        
        return data

    
class TempEmailRecipientImportForm(ModelForm):
    template_name = "form_template/full_width_form.html"

    class Meta:
        model = TempRecipientDataSheet
        fields= ['data_sheet','category','description','platform',]

        widgets = {
                'data_sheet': forms.FileInput(attrs={'class': 'form-control'}),
                'platform': forms.HiddenInput(),
                'category': forms.Select(attrs={'class':'form-select'}),
                'description': forms.TextInput(attrs={'class':'form-control'}),
        }
    # field_order = ['data_sheet','category','description','platform',]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['platform'].initial = 'email'

    def clean_data_sheet(self):
        file = self.cleaned_data.get('data_sheet')
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError("Only CSV files are allowed.")
        return file
    


# create email form 
class EmailCreationForm(ModelForm):
    template_name = "form_template/full_width_form.html"
    attachment = MultipleFileField(label='Choose Files to Attach (Multiple selections allowed)',widget=MultipleFileInput(attrs={'class': 'form-control'}))
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body','attachment']

        labels = {
            'name': 'Template Name',
            'subject': 'Email Subject',
            'body': 'Email Body',
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class':'form-control','rows':3})
        }


class EmailChangeForm(ModelForm):
    template_name = "form_template/full_width_form.html"
   

    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']

        labels = {
            'name': 'Template Name',
            'subject': 'Email Subject',
            'body': 'Email Body',
        }

        widgets = {
            'name': forms.HiddenInput(attrs={'class': 'form-control',}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }


class EmailAttachmentForm(ModelForm):
    class Meta:
        fields=['attachment','template']
        




# class FileFieldForm(forms.Form):
#     file_field = MultipleFileField(required=False)