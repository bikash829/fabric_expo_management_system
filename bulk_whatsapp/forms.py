from django import forms
from django.forms import ModelForm
from bulk_whatsapp.models import TempRecipient, WhatsappTemplate
from bulk_core.models import RecipientDataSheet,RecipientCategory,TempRecipientDataSheet
from bulk_core.utils import MultipleFileField,MultipleFileInput



    
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
    attachment = MultipleFileField(required=False,label='Choose Files to Attach (Multiple selections allowed)',widget=MultipleFileInput(attrs={'class': 'form-control'}))

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



