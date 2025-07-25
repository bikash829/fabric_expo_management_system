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
    # email_2 = models.EmailField(blank=True, null=True)
    # email_3 = models.EmailField(blank=True, null=True)
    # phone_2 = models.CharField(max_length=50, blank=True, null=True)
    wechat_id = models.CharField(max_length=50, blank=True, null=True)
    payment_term = models.CharField(max_length=100)
    fabric_reference = models.CharField(max_length=255, blank=True)
    # is_deleted = models.BooleanField(default=False,blank=True,editable=False)



    def __str__(self):
        return f"Supplier Mill Name: {self.mill_name}"
    

# product info 
class Product(SoftDeleteModel):
    date = models.DateField()
    fabric_article_supplier = models.CharField(max_length=255)
    fabric_article_fexpo = models.CharField(max_length=255)
    fabric_mill_supplier = models.CharField(max_length=255)
    rd_generated_date = models.DateField(blank=True, null=True)
    fabric_mill_source = models.CharField(max_length=255)
    coo = models.CharField(max_length=100)  # Country of Origin
    product_category = models.CharField(max_length=100)
    mill_reference = models.CharField(max_length=255)
    fabricexpo_reference = models.CharField(max_length=255)
    season = models.CharField(max_length=100)
    style = models.CharField(max_length=100)
    po = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100,null=True)
    composition = models.CharField(max_length=255)
    construction = models.CharField(max_length=255)
    weight = models.CharField(max_length=50)  # e.g., "220 GSM"
    color = models.CharField(max_length=100)
    cut_width = models.CharField(max_length=50)
    wash = models.CharField(max_length=100)
    price_per_yard = models.DecimalField(max_digits=10, decimal_places=2)
    shrinkage_percent  = models.DecimalField(max_digits=5, decimal_places=2)
    stock_qty = models.PositiveIntegerField()
    # images = models.ImageField(upload_to='product_images/', blank=True, null=True)
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    concern_person = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    tag = models.CharField(max_length=50,null=True,blank=True)


    @property
    def total_value(self):
        """
        Returns the total value of the product (price_per_yard * stock_qty).
        """
        if self.price_per_yard is not None and self.stock_qty is not None:
            return self.price_per_yard * self.stock_qty
        return 0
 

    def __str__(self):
        return f"{self.fabric_article_supplier} - {self.style}"
    

    def get_absolute_url(self):
        return reverse('business_data:product-detail', kwargs={'pk': self.pk})

    def generate_barcode_image(self):
        code_value = f"PROD-{self.id}"
        ean = barcode.get('code128', code_value, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        file_name = f"barcode_{self.id}.png"
        self.barcode.save(file_name, File(buffer), save=False)

    def generate_qr_code_image(self):
        # full_url = f"{settings.SITE_BASE_URL}{self.get_absolute_url()}"
        full_url = f"{settings.SITE_BASE_URL}{reverse('business_data:product-detail-sticker', kwargs={'pk': self.pk})}"

        qr = qrcode.make(full_url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f"qrcode_{self.id}.png"
        self.qr_code.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.generate_barcode_image()
            self.generate_qr_code_image()
            super().save(update_fields=['barcode', 'qr_code'])



class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    uploaded_at = models.DateTimeField(auto_now_add=True)














































    