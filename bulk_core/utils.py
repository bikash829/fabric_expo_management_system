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
    

import re
from colorsys import hls_to_rgb

def hsl_to_rgb(h, s, l):
    r, g, b = hls_to_rgb(h / 360, l / 100, s / 100)
    return int(r * 255), int(g * 255), int(b * 255)

def replace_hsl_with_rgb(html_content):
    def hsl_to_rgb_match(match):
        h, s, l = map(float, match.groups())
        r, g, b = hsl_to_rgb(h, s, l)
        return f"rgb({r}, {g}, {b})"

    return re.sub(r'hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)', hsl_to_rgb_match, html_content)
