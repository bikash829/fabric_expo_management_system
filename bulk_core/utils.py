from django import forms
from django.forms import ModelForm, ValidationError


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