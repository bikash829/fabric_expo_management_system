from django import forms

from business_data.models import Buyer, Product

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


from django import forms
from django.core.validators import URLValidator, validate_email
from django.core.exceptions import ValidationError
from .models import (
    ContactInfo, PersonEmail, PersonPhone, 
    Buyer, Customer, Supplier, Product, 
    ProductImage, CompanyProfile
)
from phonenumber_field.formfields import PhoneNumberField
from django.forms import inlineformset_factory

# Base Contact Info Form with Bootstrap classes
class ContactInfoForm(forms.ModelForm):
    # emails = forms.CharField(
    #     widget=forms.Textarea(attrs={
    #         'rows': 2,
    #         'class': 'form-control',
    #         'placeholder': 'example1@domain.com, example2@domain.com'
    #     }),
    #     required=False,
    #     help_text="Enter multiple emails separated by commas"
    # )
    
    # phones = forms.CharField(
    #     widget=forms.Textarea(attrs={
    #         'rows': 2,
    #         'class': 'form-control',
    #         'placeholder': '+8801XXXXXXXX, +8801XXXXXXXX'
    #     }),
    #     required=False,
    #     help_text="Enter phone numbers separated by commas"
    # )
    
    # whatsapp_numbers = forms.CharField(
    #     widget=forms.Textarea(attrs={
    #         'rows': 2,
    #         'class': 'form-control',
    #         'placeholder': '+8801XXXXXXXX, +8801XXXXXXXX'
    #     }),
    #     required=False,
    #     help_text="Enter WhatsApp numbers separated by commas"
    # )

    class Meta:
        model = ContactInfo
        fields = [
            'date',
            'company_name',
            'organization_type',
            'brand',
            'department',
            'country_of_origin',
            'website',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
            # 'tag'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'organization_type': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brand Name'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
            'country_of_origin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'mailing_address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Mailing Address'
            }),
            'visiting_address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Visiting Address'
            }),
            'linkedin_profile': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/company/example'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Additional remarks'
            }),
            'concern_fe_rep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Concern FE Representative'
            }),
            # 'tag': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Tag'
            # }),
        }

    # ... (keep the rest of the methods unchanged)

# Buyer Form with Bootstrap classes
# class BuyerForm(ContactInfoForm):
#     class Meta(ContactInfoForm.Meta):
#         model = Buyer
#         fields = ContactInfoForm.Meta.fields + [
#             'buyer_name',
#             'designation',
#             'category',
#             'is_international',
#             'payment_term',
#             'fabric_reference'
#         ]
#         widgets = {
#             **ContactInfoForm.Meta.widgets,
#             'buyer_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Buyer Name'
#             }),
#             'designation': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Designation'
#             }),
#             'category': forms.TextInput(attrs={
#                 'class': 'form-control'
#             }),
#             'is_international': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input'
#             }),
#             'payment_term': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Payment Terms'
#             }),
#             'fabric_reference': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Reference'
#             }),
#         }
class BuyerForm(ContactInfoForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'buyer@company.com'
        }),
        required=False
    )
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False
    )
    
    whatsapp_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False,
        help_text="Must be a valid WhatsApp number"
    )

    class Meta(ContactInfoForm.Meta):
        model = Buyer
        fields = [
            'date',
            'company_name',
            'organization_type',
            'brand',
            'department',
            'country_of_origin',
            'website',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
            # 'tag',
            'buyer_name',
            'designation',
            'category',
            'payment_term',
            'fabric_reference',
            'email',
            'phone',
            'whatsapp_number',
            # 'is_international',
        ]
        widgets = {
            **ContactInfoForm.Meta.widgets,
            'buyer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Buyer Name'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Designation'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'payment_term': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payment Terms'
            }),
            'fabric_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fabric Reference'
            }),
            # 'is_international': forms.CheckboxInput(attrs={
            #     'class': 'form-check-input'
            # }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove the multiple emails/phones fields from parent
        self.fields.pop('emails', None)
        self.fields.pop('phones', None)
        self.fields.pop('whatsapp_numbers', None)
        
        # Initialize with existing data if available
        if self.instance.pk:
            # Get first email
            email = self.instance.emails.first()
            if email:
                self.fields['email'].initial = email.email
            
            # Get first regular phone
            phone = self.instance.phones.filter(is_whatsapp=False).first()
            if phone:
                self.fields['phone'].initial = phone.phone
            
            # Get first whatsapp number
            whatsapp = self.instance.phones.filter(is_whatsapp=True).first()
            if whatsapp:
                self.fields['whatsapp_number'].initial = whatsapp.phone

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Phone number is required")
        # Add any phone validation logic here
        return phone

    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number')
        if not whatsapp:
            raise ValidationError("WhatsApp number is required")
        # Add any WhatsApp-specific validation here
        return whatsapp

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Handle email (only keep one)
            self.instance.emails.all().delete()
            PersonEmail.objects.create(
                contact_info=instance,
                email=self.cleaned_data['email']
            )
            
            # Handle phones (one regular, one whatsapp)
            self.instance.phones.all().delete()
            
            # Regular phone
            PersonPhone.objects.create(
                contact_info=instance,
                phone=self.cleaned_data['phone'],
                is_whatsapp=False
            )
            
            # WhatsApp number
            PersonPhone.objects.create(
                contact_info=instance,
                phone=self.cleaned_data['whatsapp_number'],
                is_whatsapp=True
            )
        
        return instance
    
    
# Customer Form with Bootstrap classes
class CustomerUpdateForm(ContactInfoForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'customer@company.com'
        }),
        required=False
    )
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False
    )
    
    whatsapp_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False,
        help_text="Must be a valid WhatsApp number"
    )

    class Meta(ContactInfoForm.Meta):
        model = Customer
        fields = [
            'date',
            'company_name',
            'organization_type',
            'brand',
            'department',
            'country_of_origin',
            'website',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
            # 'tag',
            'customer_name',
            'designation',
            'category',
            'payment_term',
            'fabric_reference',
            'email',
            'phone',
            'whatsapp_number',
            # 'is_international',
        ]
        widgets = {
            **ContactInfoForm.Meta.widgets,
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer Name'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Designation'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'payment_term': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payment Terms'
            }),
            'fabric_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fabric Reference'
            }),
            # 'is_international': forms.CheckboxInput(attrs={
            #     'class': 'form-check-input'
            # }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove the multiple emails/phones fields from parent
        self.fields.pop('emails', None)
        self.fields.pop('phones', None)
        self.fields.pop('whatsapp_numbers', None)
        
        # Initialize with existing data if available
        if self.instance.pk:
            # Get first email
            email = self.instance.emails.first()
            if email:
                self.fields['email'].initial = email.email
            
            # Get first regular phone
            phone = self.instance.phones.filter(is_whatsapp=False).first()
            if phone:
                self.fields['phone'].initial = phone.phone
            
            # Get first whatsapp number
            whatsapp = self.instance.phones.filter(is_whatsapp=True).first()
            if whatsapp:
                self.fields['whatsapp_number'].initial = whatsapp.phone

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Phone number is required")
        # Add any phone validation logic here
        return phone

    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number')
        if not whatsapp:
            raise ValidationError("WhatsApp number is required")
        # Add any WhatsApp-specific validation here
        return whatsapp

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Handle email (only keep one)
            self.instance.emails.all().delete()
            PersonEmail.objects.create(
                contact_info=instance,
                email=self.cleaned_data['email']
            )
            
            # Handle phones (one regular, one whatsapp)
            self.instance.phones.all().delete()
            
            # Regular phone
            PersonPhone.objects.create(
                contact_info=instance,
                phone=self.cleaned_data['phone'],
                is_whatsapp=False
            )
            
            # WhatsApp number
            PersonPhone.objects.create(
                contact_info=instance,
                phone=self.cleaned_data['whatsapp_number'],
                is_whatsapp=True
            )
        
        return instance
    
        
# Customer Form with Bootstrap classes
class SupplierUpdateForm(ContactInfoForm):
    # Email fields (max 3)
    email1 = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'primary@company.com'
        }),
        required=False,
        label="Primary Email"
    )
    
    email2 = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'secondary@company.com'
        }),
        required=False,
        label="Secondary Email"
    )
    
    email3 = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tertiary@company.com'
        }),
        required=False,
        label="Tertiary Email"
    )

    # Phone fields (max 2 regular)
    phone1 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False,
        label="Primary Phone"
    )
    
    phone2 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False,
        label="Secondary Phone"
    )

    # WhatsApp (max 1)
    whatsapp_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXX'
        }),
        required=False,
        label="WhatsApp Number"
    )

    class Meta(ContactInfoForm.Meta):
        model = Supplier
        fields = [
            'date',
            'mill_name',
            'supplier_name',
            'concern_person',
            'concern_person_designation',
            'product_category',
            'product_range',
            'speciality',
            'country_of_origin',
            'email1', 'email2', 'email3',
            'phone1', 'phone2',
            'whatsapp_number',
            'wechat_id',
            'payment_term',
            'fabric_reference',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
            # 'tag'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    }),
            'mill_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'concern_person': forms.TextInput(attrs={'class': 'form-control'}),
            'concern_person_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'product_category': forms.TextInput(attrs={'class': 'form-control'}),
            'product_range': forms.TextInput(attrs={'class': 'form-control'}),
            'speciality': forms.TextInput(attrs={'class': 'form-control'}),
            'wechat_id': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_term': forms.TextInput(attrs={'class': 'form-control'}),
            'fabric_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'country_of_origin': forms.TextInput(attrs={'class':'form-control'}),
            'mailing_address': forms.Textarea(
                attrs={
                    'class':'form-control',
                    'rows': 3,
                    'placeholder': 'Factory Mailing Address',
                    }
                ),
            'visiting_address': forms.Textarea(
                attrs={
                    'class':'form-control',
                    'rows': 3,
                    'placeholder': 'Factory Visiting Address',
                    }
                ),
            'linkedin_profile': forms.TextInput(attrs={'class':'form-control'}),
            'remarks': forms.Textarea(
                attrs={
                    'class':'form-control',
                    'rows': 3,
                    'placeholder': 'Remarks',
                    }
                ),
            'concern_fe_rep': forms.TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize with existing data if available
        if self.instance.pk:
            emails = list(self.instance.emails.all())
            if len(emails) > 0:
                self.fields['email1'].initial = emails[0].email
            if len(emails) > 1:
                self.fields['email2'].initial = emails[1].email
            if len(emails) > 2:
                self.fields['email3'].initial = emails[2].email
            
            regular_phones = list(self.instance.phones.filter(is_whatsapp=False))
            if len(regular_phones) > 0:
                self.fields['phone1'].initial = regular_phones[0].phone
            if len(regular_phones) > 1:
                self.fields['phone2'].initial = regular_phones[1].phone
            
            whatsapp = self.instance.phones.filter(is_whatsapp=True).first()
            if whatsapp:
                self.fields['whatsapp_number'].initial = whatsapp.phone

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Handle emails (max 3)
            self.instance.emails.all().delete()
            if self.cleaned_data['email1']:
                PersonEmail.objects.create(contact_info=instance, email=self.cleaned_data['email1'])
            if self.cleaned_data['email2']:
                PersonEmail.objects.create(contact_info=instance, email=self.cleaned_data['email2'])
            if self.cleaned_data['email3']:
                PersonEmail.objects.create(contact_info=instance, email=self.cleaned_data['email3'])
            
            # Handle phones (max 2 regular + 1 whatsapp)
            self.instance.phones.all().delete()
            if self.cleaned_data['phone1']:
                PersonPhone.objects.create(
                    contact_info=instance,
                    phone=self.cleaned_data['phone1'],
                    is_whatsapp=False
                )
            if self.cleaned_data['phone2']:
                PersonPhone.objects.create(
                    contact_info=instance,
                    phone=self.cleaned_data['phone2'],
                    is_whatsapp=False
                )
            if self.cleaned_data['whatsapp_number']:
                PersonPhone.objects.create(
                    contact_info=instance,
                    phone=self.cleaned_data['whatsapp_number'],
                    is_whatsapp=True
                )
        
        return instance
    #     fields = [
    #         'date',
    #         'company_name',
    #         'organization_type',
    #         'brand',
    #         'department',
    #         'country_of_origin',
    #         'website',
    #         'mailing_address',
    #         'visiting_address',
    #         'linkedin_profile',
    #         'remarks',
    #         'concern_fe_rep',
    #         # 'tag',
    #         'customer_name',
    #         'designation',
    #         'category',
    #         'payment_term',
    #         'fabric_reference',
    #         'email',
    #         'phone',
    #         'whatsapp_number',
    #         # 'is_international',
    #     ]
    #     widgets = {
    #         **ContactInfoForm.Meta.widgets,
    #         'customer_name': forms.TextInput(attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Customer Name'
    #         }),
    #         'designation': forms.TextInput(attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Designation'
    #         }),
    #         'category': forms.TextInput(attrs={
    #             'class': 'form-control'
    #         }),
            
    #         'payment_term': forms.TextInput(attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Payment Terms'
    #         }),
    #         'fabric_reference': forms.TextInput(attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Fabric Reference'
    #         }),
    #         # 'is_international': forms.CheckboxInput(attrs={
    #         #     'class': 'form-check-input'
    #         # }),
    #     }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        
    #     # Remove the multiple emails/phones fields from parent
    #     self.fields.pop('emails', None)
    #     self.fields.pop('phones', None)
    #     self.fields.pop('whatsapp_numbers', None)
        
    #     # Initialize with existing data if available
    #     if self.instance.pk:
    #         # Get first email
    #         email = self.instance.emails.first()
    #         if email:
    #             self.fields['email'].initial = email.email
            
    #         # Get first regular phone
    #         phone = self.instance.phones.filter(is_whatsapp=False).first()
    #         if phone:
    #             self.fields['phone'].initial = phone.phone
            
    #         # Get first whatsapp number
    #         whatsapp = self.instance.phones.filter(is_whatsapp=True).first()
    #         if whatsapp:
    #             self.fields['whatsapp_number'].initial = whatsapp.phone

    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if not phone:
    #         raise ValidationError("Phone number is required")
    #     # Add any phone validation logic here
    #     return phone

    # def clean_whatsapp_number(self):
    #     whatsapp = self.cleaned_data.get('whatsapp_number')
    #     if not whatsapp:
    #         raise ValidationError("WhatsApp number is required")
    #     # Add any WhatsApp-specific validation here
    #     return whatsapp

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
        
    #     if commit:
    #         instance.save()
            
    #         # Handle email (only keep one)
    #         self.instance.emails.all().delete()
    #         PersonEmail.objects.create(
    #             contact_info=instance,
    #             email=self.cleaned_data['email']
    #         )
            
    #         # Handle phones (one regular, one whatsapp)
    #         self.instance.phones.all().delete()
            
    #         # Regular phone
    #         PersonPhone.objects.create(
    #             contact_info=instance,
    #             phone=self.cleaned_data['phone'],
    #             is_whatsapp=False
    #         )
            
    #         # WhatsApp number
    #         PersonPhone.objects.create(
    #             contact_info=instance,
    #             phone=self.cleaned_data['whatsapp_number'],
    #             is_whatsapp=True
    #         )
        
    #     return instance
        
         
# class CustomerForm(ContactInfoForm):
#     class Meta(ContactInfoForm.Meta):
#         model = Customer
#         fields = ContactInfoForm.Meta.fields + [
#             'customer_name',
#             'designation',
#             'category',
#             'is_local',
#             'payment_term',
#             'fabric_reference'
#         ]
#         widgets = {
#             **ContactInfoForm.Meta.widgets,
#             'customer_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Customer Name'
#             }),
#             'designation': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Designation'
#             }),
#             'category': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'is_local': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input'
#             }),
#             'payment_term': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Payment Terms'
#             }),
#             'fabric_reference': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Reference'
#             }),
#         }

# # Supplier Form with Bootstrap classes
# class SupplierForm(ContactInfoForm):
#     wechat_id = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'WeChat ID'
#         })
#     )
    
#     class Meta(ContactInfoForm.Meta):
#         model = Supplier
#         fields = ContactInfoForm.Meta.fields + [
#             'mill_name',
#             'supplier_name',
#             'concern_person',
#             'concern_person_designation',
#             'product_category',
#             'product_range',
#             'speciality',
#             'wechat_id',
#             'payment_term',
#             'fabric_reference'
#         ]
#         widgets = {
#             **ContactInfoForm.Meta.widgets,
#             'mill_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Mill Name'
#             }),
#             'supplier_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Supplier Name'
#             }),
#             'concern_person': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Concern Person'
#             }),
#             'concern_person_designation': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Designation'
#             }),
#             'product_category': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Product Category'
#             }),
#             'product_range': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Product Range'
#             }),
#             'speciality': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Speciality'
#             }),
#             'payment_term': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Payment Terms'
#             }),
#             'fabric_reference': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Reference'
#             }),
#         }

# # Product Form with Bootstrap classes
# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = [
#             'article_no',
#             'date',
#             'fabric_article_supplier',
#             'fabric_article_fexpo',
#             'fabric_mill_supplier',
#             'rd_generated_date',
#             'fabric_mill_source',
#             'coo',
#             'product_category',
#             'mill_reference',
#             'fabricexpo_reference',
#             'season',
#             'style',
#             'po',
#             'customer_name',
#             'composition',
#             'construction',
#             'weight',
#             'color',
#             'cut_width',
#             'weave',
#             'wash',
#             'price_per_yard',
#             'shrinkage_percent',
#             'stock_qty',
#             'concern_person',
#             'remarks',
#             'tag'
#         ]
#         widgets = {
#             'article_no': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Article Number'
#             }),
#             'date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'
#             }),
#             'fabric_article_supplier': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Article (Supplier)'
#             }),
#             'fabric_article_fexpo': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Article (Fabric Expo)'
#             }),
#             'fabric_mill_supplier': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Mill (Supplier)'
#             }),
#             'rd_generated_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'
#             }),
#             'fabric_mill_source': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Mill (Source)'
#             }),
#             'coo': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Country of Origin'
#             }),
#             'product_category': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Product Category'
#             }),
#             'mill_reference': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Mill Reference'
#             }),
#             'fabricexpo_reference': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Fabric Expo Reference'
#             }),
#             'season': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Season'
#             }),
#             'style': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Style'
#             }),
#             'po': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'PO Number'
#             }),
#             'customer_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Customer Name'
#             }),
#             'composition': forms.Textarea(attrs={
#                 'rows': 2,
#                 'class': 'form-control',
#                 'placeholder': 'Composition'
#             }),
#             'construction': forms.Textarea(attrs={
#                 'rows': 2,
#                 'class': 'form-control',
#                 'placeholder': 'Construction'
#             }),
#             'weight': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Weight (GSM/OZ)'
#             }),
#             'color': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Color'
#             }),
#             'cut_width': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Cut Width (Inch)'
#             }),
#             'weave': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Weave'
#             }),
#             'wash': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Wash'
#             }),
#             'price_per_yard': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#                 'placeholder': 'Price per Yard'
#             }),
#             'shrinkage_percent': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#                 'placeholder': 'Shrinkage %'
#             }),
#             'stock_qty': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Stock Quantity'
#             }),
#             'concern_person': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Concern Person'
#             }),
#             'remarks': forms.Textarea(attrs={
#                 'rows': 3,
#                 'class': 'form-control',
#                 'placeholder': 'Remarks'
#             }),
#             'tag': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Tag'
#             }),
#         }

# # Product Image Form with Bootstrap classes
# # class ProductImageForm(forms.ModelForm):
# #     class Meta:
# #         model = ProductImage
# #         fields = ['image', 'alt_text', 'sample_type']
# #         widgets = {
# #             'image': forms.FileInput(attrs={
# #                 'class': 'form-control'
# #             }),
# #             'alt_text': forms.TextInput(attrs={
# #                 'class': 'form-control',
# #                 'placeholder': 'Alternative text for image'
# #             }),
# #             'sample_type': forms.Select(attrs={
# #                 'class': 'form-select'
# #             }, choices=ProductImage.SampleTypeChoices.choices)
# #         }

# # Company Profile Form with Bootstrap classes
# class CompanyProfileForm(forms.ModelForm):
#     class Meta:
#         model = CompanyProfile
#         fields = '__all__'
#         widgets = {
#             'company_name': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'logo': forms.FileInput(attrs={
#                 'class': 'form-control'
#             }),
#             'address': forms.Textarea(attrs={
#                 'rows': 3,
#                 'class': 'form-control'
#             }),
#             'phone_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': '+880XXXXXXXXXX'
#             }),
#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'example@domain.com'
#             }),
#             'website': forms.URLInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'https://example.com'
#             }),
#             'established_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'
#             }),
#             'description': forms.Textarea(attrs={
#                 'rows': 4,
#                 'class': 'form-control'
#             }),
#         }

# # Formset for Product Images
# # ProductImageFormSet = inlineformset_factory(
# #     Product, 
# #     ProductImage, 
# #     form=ProductImageForm,
# #     extra=1,
# #     max_num=3,
# #     can_delete=True
# # )

# # Form for managing individual emails with Bootstrap classes
# class PersonEmailForm(forms.ModelForm):
#     class Meta:
#         model = PersonEmail
#         fields = ['email']
#         widgets = {
#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'example@domain.com'
#             })
#         }

# # Form for managing individual phone numbers with Bootstrap classes
# class PersonPhoneForm(forms.ModelForm):
#     class Meta:
#         model = PersonPhone
#         fields = ['phone', 'is_whatsapp', 'is_wechat']
#         widgets = {
#             'phone': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': '+880XXXXXXXXXX'
#             }),
#             'is_whatsapp': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input'
#             }),
#             'is_wechat': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input'
#             }),
#         }