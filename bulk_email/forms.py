from django import forms
from django.forms import ModelForm, ValidationError
from .models import RecipientCategory, EmailTemplate, EmailAttachment
from bulk_core.models import RecipientDataSheet,RecipientCategory,TempRecipientDataSheet
from bulk_core.utils import MultipleFileField,MultipleFileInput

    
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
    


from django_ckeditor_5.widgets import CKEditor5Widget
# create email form 
class EmailCreationForm(ModelForm):
    # template_name = "form_template/full_width_form.html"
    attachment = MultipleFileField(required=False,label='Choose Files to Attach (Multiple selections allowed)',widget=MultipleFileInput(attrs={'class': 'form-control'}))
    body = CKEditor5Widget(attrs={"class":"django_ckeditor_5"},config_name="extends")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False
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