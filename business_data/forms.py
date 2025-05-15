from django import forms

class BuyerUploadForm(forms.Form):
    template_name = "form_template/full_width_form.html"

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith(('.csv', '.xls', '.xlsx')):
            raise forms.ValidationError("Only CSV and Excel files are allowed.")
        return file
    
# customer upload form 
class FileUploadForm(forms.Form):
    template_name = "form_template/full_width_form.html"

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith(('.csv', '.xls', '.xlsx')):
            raise forms.ValidationError("Only CSV and Excel files are allowed.")
        return file
