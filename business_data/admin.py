from django.contrib import admin
from .models import CompanyProfile, ProductImage

# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(ProductImage)