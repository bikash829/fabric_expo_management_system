from django import forms

from business_data.models import Product

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


class ProductUpdateForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    article_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    fabric_article_supplier = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fabric_article_fexpo = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fabric_mill_supplier = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rd_generated_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fabric_mill_source = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    coo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_category = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mill_reference = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fabricexpo_reference = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    season = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    style = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    po = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    composition = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    construction = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    weight = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    color = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cut_width = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    weave = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    wash = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    price_per_yard = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    shrinkage_percent = forms.DecimalField(max_digits=5, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    stock_qty = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    concern_person = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    remarks = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # tag = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model =Product
        fields = [
            'date','article_no', 'fabric_article_supplier', 'fabric_article_fexpo', 'fabric_mill_supplier',
            'rd_generated_date', 'fabric_mill_source', 'coo', 'product_category', 'mill_reference',
            'fabricexpo_reference', 'season', 'style', 'po', 'customer_name', 'composition',
            'construction', 'weight', 'color', 'cut_width','weave', 'wash', 'price_per_yard',
            'shrinkage_percent', 'stock_qty', 'concern_person','remarks'
        ]