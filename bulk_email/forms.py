from django import forms
from django.forms import ModelForm
from .models import RecipientCategory
from bulk_core.models import RecipientDataSheet,RecipientCategory


class EmailRecipientImportForm(ModelForm):


    class Meta:
        model = RecipientDataSheet
        fields= ['data_sheet','description','platform','category']

        widgets = {
                'platform': forms.HiddenInput(),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['platform'].initial = 'email'

    def clean_data_sheet(self):
        file = self.cleaned_data.get('data_sheet')
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError("Only CSV files are allowed.")
        return file