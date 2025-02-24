from django import forms
from django.forms import ModelForm
from bulk_whatsapp.models import TempRecipient, WhatsappTemplate
from bulk_core.models import RecipientDataSheet,RecipientCategory,TempRecipientDataSheet



    
class TempRecipientImportForm(ModelForm):
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
        self.fields['platform'].initial = 'whatsapp'

    def clean_data_sheet(self):
        file = self.cleaned_data.get('data_sheet')
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError("Only CSV files are allowed.")
        return file
    


# create message form 
class MessageCreationForm(ModelForm):
    template_name = "form_template/full_width_form.html"
    class Meta:
        model = WhatsappTemplate
        fields = ['name', 'message_content']
        labels = {
                    'name': 'Template Name',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'message_content': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

# class EmailChangeForm(ModelForm):
#     template_name = "form_template/full_width_form.html"
#     class Meta:
#         model = EmailTemplate
#         fields = ['name', 'subject', 'body']

#         widgets = {
#             'name': forms.HiddenInput(attrs={'class': 'form-control',}),
#             'subject': forms.TextInput(attrs={'class': 'form-control'}),
#             'body': forms.Textarea(attrs={'class':'form-control','rows':3}),
#         }
class MessageDraftUpdateForm(ModelForm):
    template_name = "form_template/full_width_form.html"
    class Meta:
        model = WhatsappTemplate
        fields = ['name', 'message_content', ]
        labels = {
            'name': 'Template Name',
        }

        widgets = {
            'name': forms.HiddenInput(attrs={'class': 'form-control',}),
            'message_content': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }





# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True

# class MultipleFileField(forms.FileField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)

#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = [single_file_clean(data, initial)]
#         return result

# class FileFieldForm(forms.Form):
#     file_field = MultipleFileField(required=False)