from django import forms
from django.forms import ModelForm
from bulk_wechat.models import WeChatTemplate
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

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['platform'].initial = 'wechat'

    def clean_data_sheet(self):
        file = self.cleaned_data.get('data_sheet')
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError("Only CSV files are allowed.")
        return file
    