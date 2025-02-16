from django import forms
from django.forms import ModelForm
from .models import RecipientCategory, EmailTemplate, EmailAttachment
from bulk_core.models import RecipientDataSheet,RecipientCategory,TempRecipientDataSheet


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
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body',]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class EmailChangeForm(ModelForm):
    template_name = "form_template/full_width_form.html"
    # attachment = forms.FileField(
    #     widget=forms.ClearableFileInput(attrs={"multiple": True}),
    #     required=False,
    # )
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body',]

        widgets = {
            'name': forms.HiddenInput(attrs={'class': 'form-control',}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

    
    # def clean_attachment(self):
    #     """
    #     Validate total size of uploaded attachments
    #     """
    #     uploaded_files = self.files.getlist("attachment")
    #     total_size = sum(file.size for file in uploaded_files)

    #     max_size = 25 * 1024 * 1024  # 25MB in bytes

    #     if total_size > max_size:
    #         raise forms.ValidationError("Total attachment size cannot exceed 25MB.")
        
    #     return uploaded_files
