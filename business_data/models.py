from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from fabric_expo_management_system.custom_model_manager import SoftDeleteModel

import os
import qrcode
import barcode
from io import BytesIO
from barcode.writer import ImageWriter
from django.core.files import File
from django.conf import settings
from django.core.exceptions import ValidationError
import random
from barcode import EAN13


# Contact info 
class ContactInfo(models.Model):
    date = models.DateField(null=True,blank=True)
    company_name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    country_of_origin = models.CharField(max_length=100, blank=True, null=True)
    # email = models.EmailField(blank=True, null=True)
    # phone_number = models.CharField(max_length=50, blank=True, null=True)
    # whatsapp_number = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    mailing_address = models.TextField(blank=True, null=True)
    visiting_address = models.TextField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    concern_fe_rep = models.CharField(max_length=255, blank=True)
    created_at = models.DateField(auto_now_add=True)
    tag = models.CharField(max_length=50,null=True,blank=True)



    def __str__(self):
        return self.company_name

# multiple email choice 
class PersonEmail(models.Model):
    # email = models.EmailField(unique=True)
    email = models.EmailField()
    contact_info = models.ForeignKey(ContactInfo, related_name='emails', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.email
    

# multiple phone number 
class PersonPhone(models.Model):
    # phone = PhoneNumberField()
    phone = models.CharField(max_length=20)
    is_whatsapp = models.BooleanField(default=False)  # Flag for WhatsApp connection
    is_wechat = models.BooleanField(default=False)    # Flag for WeChat connection

    contact_info = models.ForeignKey(ContactInfo, related_name='phones', on_delete=models.CASCADE)

    def __str__(self):
        return self.phone
    

# Buyer info
class Buyer(SoftDeleteModel, ContactInfo):
    buyer_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True,null=True, help_text="Apparel or Textile")
    is_international = models.BooleanField(default=True)  # <-- flag
    payment_term = models.CharField(max_length=100, blank=True)
    fabric_reference = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return f"{self.buyer_name} ({self.company_name})"
    

# customer info 
class Customer(SoftDeleteModel, ContactInfo ):
    customer_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True,null=True, help_text="Apparel or Textile")
    is_local = models.BooleanField(default=True)  # <-- flag
    payment_term = models.CharField(max_length=100, blank=True)
    fabric_reference = models.CharField(max_length=255, blank=True)
    # is_deleted = models.BooleanField(default=False,blank=True,editable=False)


    def __str__(self):
        return f"{self.customer_name} ({self.company_name})"
    
# supplier info
class Supplier(SoftDeleteModel,ContactInfo):
    mill_name = models.CharField(max_length=255)
    supplier_name = models.CharField(max_length=255)
    concern_person = models.CharField(max_length=255)
    concern_person_designation = models.CharField(max_length=100)
    product_category = models.CharField(max_length=100)
    product_range = models.CharField(max_length=100)
    speciality = models.CharField(max_length=255, blank=True)
    wechat_id = models.CharField(max_length=50, blank=True, null=True)
    payment_term = models.CharField(max_length=100)
    fabric_reference = models.CharField(max_length=255, blank=True)
    # email_2 = models.EmailField(blank=True, null=True)
    # email_3 = models.EmailField(blank=True, null=True)
    # phone_2 = models.CharField(max_length=50, blank=True, null=True)
    # is_deleted = models.BooleanField(default=False,blank=True,editable=False)



    def __str__(self):
        return f"Supplier Mill Name: {self.mill_name}"
    

# product info 
class Product(SoftDeleteModel):
    article_no = models.CharField(unique=True,max_length=100)
    date = models.DateField(blank=True,null=True)
    fabric_article_supplier = models.CharField(max_length=255,blank=True,null=True)
    fabric_article_fexpo = models.CharField(max_length=255,blank=True,null=True)
    fabric_mill_supplier = models.CharField(max_length=255,blank=True,null=True)
    rd_generated_date = models.DateField(blank=True, null=True)
    fabric_mill_source = models.CharField(max_length=255,blank=True,null=True)
    coo = models.CharField(max_length=100,blank=True,null=True)  # Country of Origin
    product_category = models.CharField(max_length=100,blank=True,null=True)
    mill_reference = models.CharField(max_length=255,blank=True,null=True)
    fabricexpo_reference = models.CharField(max_length=255,blank=True,null=True)
    season = models.CharField(max_length=100,blank=True,null=True)
    style = models.CharField(max_length=100,blank=True,null=True)
    po = models.CharField(max_length=100,blank=True,null=True)
    customer_name = models.CharField(max_length=100,null=True)
    composition = models.CharField(max_length=255,blank=True,null=True)
    construction = models.CharField(max_length=255,blank=True,null=True)
    weight = models.CharField(max_length=50,blank=True,null=True)  # e.g., "220 GSM"
    color = models.CharField(max_length=100,blank=True,null=True)
    cut_width = models.CharField(max_length=50,blank=True,null=True)
    weave = models.CharField(max_length=100,blank=True,null=True)
    wash = models.CharField(max_length=100,blank=True,null=True)
    price_per_yard = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    shrinkage_percent  = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    stock_qty = models.PositiveIntegerField(blank=True,null=True)
    # images = models.ImageField(upload_to='product_images/', blank=True, null=True)
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    barcode_number = models.CharField(max_length=12, unique=True, null=True,blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    concern_person = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    created_date = models.DateField(auto_now_add=True,blank=True,null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    tag = models.CharField(max_length=50,null=True,blank=True)
    # gtin = models.CharField(max_length=14, unique=True, blank=True, null=True)  # GS1 Global Trade Item Number
    # batch_number = models.CharField(max_length=50)  # For traceability

    @property
    def total_value(self):
        """
        Returns the total value of the product (price_per_yard * stock_qty).
        """
        if self.price_per_yard is not None and self.stock_qty is not None:
            return self.price_per_yard * self.stock_qty
        return 0
 
    def __str__(self):
        return f"{self.article_no} | {self.date}"
    
    def get_absolute_url(self):
        return reverse('business_data:product-detail', kwargs={'pk': self.pk})

    # def generate_barcode_image(self):
    #     # Generate a unique 12-digit barcode number if not set
    #     if not self.barcode_number:
    #         while True:
    #             code_value = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    #             if not Product.objects.filter(barcode_number=code_value).exists():
    #                 self.barcode_number = code_value
    #                 break

    #     # Generate EAN13 barcode (checksum auto-handled)
    #     ean = EAN13(self.barcode_number, writer=ImageWriter())
    #     buffer = BytesIO()
    #         # Custom writer with reduced barcode height
    #     writer_options = {
    #         'module_height': 10.0,  # 🔽 Reduce height (default is 15.0)
    #     }

    #     ean.write(buffer, options=writer_options)

    #     file_name = f"barcode_{self.pk or 'temp'}.png"
    #     self.barcode.save(file_name, File(buffer), save=False)
    def generate_barcode_image(self):
        # Generate EAN13 barcode image using self.barcode_number
        ean = EAN13(self.barcode_number, writer=ImageWriter())
        buffer = BytesIO()

        writer_options = {
            'module_height': 10.0,  # Reduce image height
        }

        ean.write(buffer, options=writer_options)

        file_name = f"barcode_{self.pk}.png"
        self.barcode.save(file_name, File(buffer), save=False)
        
    def generate_qr_code_image(self):
        # full_url = f"{settings.SITE_BASE_URL}{self.get_absolute_url()}"
        full_url = f"{settings.SITE_BASE_URL}{reverse('business_data:product-detail', kwargs={'pk': self.pk})}"

        qr = qrcode.make(full_url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f"qrcode_{self.id}.png"
        self.qr_code.save(file_name, File(buffer), save=False)

    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)
    #     if is_new:
    #         self.generate_barcode_image()
    #         self.generate_qr_code_image()
    #         super().save(update_fields=['barcode', 'qr_code'])
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new and not self.barcode_number:
            # Generate a unique 12-digit barcode number
            while True:
                code_value = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                if not Product.objects.filter(barcode_number=code_value).exists():
                    self.barcode_number = code_value
                    break

        super().save(*args, **kwargs)

        if is_new:
            self.generate_barcode_image()
            self.generate_qr_code_image()
            super().save(update_fields=['barcode', 'barcode_number', 'qr_code'])


# Add sample type choices for ProductImage using a base choice class
class SampleTypeChoices(models.TextChoices):
    FABRIC = 'FABRIC', 'Fabric Sample'
    GARMENT = 'GARMENT', 'Garment View'
    MODEL = 'MODEL', 'Model View'

class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    sample_type = models.CharField(
        max_length=20,
        choices=SampleTypeChoices.choices,
        default=SampleTypeChoices.FABRIC,
        help_text="Type of sample shown in the image"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sample of: {self.product.article_no} | {self.product.date}"
    
    def clean(self):
        # Check if this is a new image being added (not an update to existing)
        if not self.pk and self.product.images.count() >= 3:
            raise ValidationError("A product cannot have more than 3 images.")
        super().clean()

    

class CompanyProfile(models.Model):
    COMPANY_CHOICES = [
        ('FABRIC_EXPO', 'Fabric Expo'),
        ('REPUBLIC_EXPORT', 'REPUBLIC EXPORT'),
        ('INTEXTILE', 'Intextile'),
        # Add more choices as needed
    ]
    company_name = models.CharField(max_length=255, choices=COMPANY_CHOICES)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    established_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name














































    