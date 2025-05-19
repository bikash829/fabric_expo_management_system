import csv
import os
from random import randint
from venv import logger
from django.db import transaction

from django.urls import reverse_lazy
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from business_data.models import Buyer, PersonEmail, PersonPhone, Supplier, Customer, Product
import phonenumber_field

from .forms import BuyerUploadForm, FileUploadForm

# extract data from excel/csv
def extract_data(request,form):
    file = form.cleaned_data['file']
    file_path = default_storage.save(f'temp/{file.name}', file)
    abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

    request.session['temp_file_path'] = file_path

    if file.name.endswith('.csv'):
        df = pd.read_csv(abs_path)
    else:
        df = pd.read_excel(abs_path)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
        # Convert Timestamp objects to strings
    for col in df.select_dtypes(include=['datetime', 'datetime64[ns]']).columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    data = df.to_dict(orient='records')
    return data 


"""Begin:: Buyer Details"""
# upload buyer data
class BuyerUploadView(View):
    def get(self, request):
        form = BuyerUploadForm()
        context = {
            'form': form,
            "title": "Import Buyers",
            "header_title": "Import Buyers From CSV",
            "card_title": "Import Buyers",
            "form_button_title": "Import Buyers",
            'csv_generator_url': reverse_lazy('business_data:buyer_demo_csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context)

    def post(self, request):
        form = BuyerUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_path = default_storage.save(f'temp/{file.name}', file)
            abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

            request.session['temp_file_path'] = file_path

            if file.name.endswith('.csv'):
                df = pd.read_csv(abs_path)
            else:
                df = pd.read_excel(abs_path)

            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
                # Convert Timestamp objects to strings
            for col in df.select_dtypes(include=['datetime', 'datetime64[ns]']).columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

            data = df.to_dict(orient='records')
            request.session['preview_buyer_data'] = data
            return redirect('business_data:buyer-preview')
        context = {
            'form': form,
            "title": "Import Buyers",
            "header_title": "Import Buyers From CSV",
            "card_title": "Import Buyers",
            "form_button_title": "Import Buyers",
            'csv_generator_url': reverse_lazy('business_data:buyer_demo_csv'), 
        }
        return render(request, 'business_data/manage_buyers/upload.html', context)

# preview uploaded data
class BuyerPreviewView(View):
    def get(self, request):
        preview_data = request.session.get('preview_buyer_data', [])
        temp_file_path = request.session.get('temp_file_path', None)
        file_info = {}
        if temp_file_path:
            file_name = os.path.basename(temp_file_path)
            file_info = {
                'name': file_name,
                'url': default_storage.url(temp_file_path),
                'uploaded_at': default_storage.get_created_time(temp_file_path) if default_storage.exists(temp_file_path) else None
            }

        context = {
            'buyers': preview_data,
            'file_info': file_info,
        }

        return render(request, 'business_data/manage_buyers/preview.html', context)

    def post(self, request):
        action = request.POST.get('action')
        file_path = request.session.get('temp_file_path')

        if not file_path:
            return redirect('business_data:buyer-upload')

        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if action == 'confirm':
            if file_path.endswith('.csv'):
                df = pd.read_csv(abs_path)
            else:
                df = pd.read_excel(abs_path)

            df.columns = df.columns.str.strip().str.lower()
            def generate_unique_color():
                    return "#{:06x}".format(randint(0, 0xFFFFFF))
            tag = generate_unique_color()
            
            for _, row in df.iterrows():

                try:
                    buyer = Buyer.objects.create(
                        date=row['date'],
                        company_name=row['company_name'],
                        organization_type=row['organization_type'],
                        brand=row['brand'],
                        category=row['category'],
                        department=row['department'],
                        buyer_name=row['buyer_name'],
                        designation=row['designation'],
                        country_of_origin=row['coo'],
                        website=row['company_website'],
                        payment_term=row['payment_term'],
                        fabric_reference=row['fabric_reference_dealing_with'],
                        mailing_address=row['mailing_address'],
                        visiting_address=row['visiting_address'],
                        linkedin_profile=row['linkedin_profile_link'],
                        remarks=row['remarks'],
                        concern_fe_rep=row['concern_fe_representative'],
                        tag=tag
                    )
                except Exception as e:
                    messages.error(request, "Invalid data upload. Please check your file and try again.")
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                    request.session.pop('preview_data', None)
                    request.session.pop('temp_file_path', None)
                    return redirect('business_data:buyer-upload')

                if buyer:
                    if row['buyer_email_id']:
                        try:
                            validate_email(row['buyer_email_id'])
                            if not PersonEmail.objects.filter(email=row['buyer_email_id']).exists():
                                PersonEmail.objects.create(email=row['buyer_email_id'], contact_info=buyer)
                        except ValidationError:
                            pass  # Invalid email, skip or handle as needed
                    if row['whatsapp_number']:
                        try:
                            PersonPhone.objects.create(phone=row['whatsapp_number'],is_whatsapp=True, contact_info = buyer)
                        except ValidationError:
                            messages.error(request,ValidationError)

                    
                    if row['phone_number']:
                        try:
                            PersonPhone.objects.create(phone=row['phone_number'], contact_info=buyer)
                        except ValidationError:
                            messages.error(request,ValidationError)

                messages.success(request, "Buyers have been successfully saved.")

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:buyer-upload')
        # return redirect('business_data:upload-success')


### Generate demo csv for buyers
class GenerateCSVBuyer(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_buyer_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "company_name", "organization_type", "brand", "category", "department",
            "buyer_name", "designation", "coo", "buyer_email_id", "whatsapp_number", "phone_number",
            "company_website", "payment_term", "fabric_reference_dealing_with", "mailing_address",
            "visiting_address", "linkedin_profile_link", "remarks", "concern_fe_representative"
        ])
        writer.writerow([
            "2025-05-13", "Acme Textiles", "Manufacturer", "Acme", "Textile", "Sales",
            "John Doe", "Manager", "Bangladesh", "john.doe@acme.com", "+8801777777254", "+8801555555555",
            "https://acme.com", "Net 30", "Cotton, Denim", "123 Main St, Dhaka", "456 Market Rd, Dhaka",
            "https://linkedin.com/in/johndoe", "Top buyer", "Alice Smith"
        ])
        writer.writerow([
            "2025-05-13", "Beta Apparel", "Exporter", "Beta", "Apparel", "Export",
            "Jane Smith", "Director", "India", "jane.smith@beta.com", "+919999999999", "+918888888888",
            "https://beta.com", "Advance", "Knit, Woven", "789 Fashion Ave, Mumbai", "1011 Textile St, Mumbai",
            "https://linkedin.com/in/janesmith", "Prefers organic", "Bob Lee"
        ])

        return response
        
# Buyer list 
class BuyerListView(ListView):
    model = Buyer
    template_name = "business_data/manage_buyers/buyer_list.html"

"""End:: Buyer details"""

"""Begin::Customer Details"""


# upload customer data
class CustomerUploadView(View):
    def get(self, request):
        form = FileUploadForm()
        context = {
            'form': form,
            "title": "Import Customers",
            "header_title": "Import Customers From CSV",
            "card_title": "Import Customers",
            "form_button_title": "Import Customers",
            'csv_generator_url': reverse_lazy('business_data:customer-demo-csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context)

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = extract_data(request,form)
            
            # print(data)
            request.session['preview_customer_data'] = data
            return redirect('business_data:customer-preview')
        context = {
            'form': form,
            "title": "Import Customers",
            "header_title": "Import Customers From CSV",
            "card_title": "Import Customers",
            "form_button_title": "Import Customers",
            'csv_generator_url': reverse_lazy('business_data:customer-demo-csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context)


# preview uploaded data
class CustomerPreviewView(View):
    def get(self, request):
        preview_data = request.session.get('preview_customer_data', [])
        temp_file_path = request.session.get('temp_file_path', None)
        file_info = {}
        if temp_file_path:
            file_name = os.path.basename(temp_file_path)
            file_info = {
                'name': file_name,
                'url': default_storage.url(temp_file_path),
                'uploaded_at': default_storage.get_created_time(temp_file_path) if default_storage.exists(temp_file_path) else None
            }

        context = {
            'customers': preview_data,
            'file_info': file_info,
        }

        return render(request, 'business_data/manage_customers/preview.html', context)

    def post(self, request):
        action = request.POST.get('action')
        file_path = request.session.get('temp_file_path')

        if not file_path:
            return redirect('business_data:customer-upload')

        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if action == 'confirm':
            if file_path.endswith('.csv'):
                df = pd.read_csv(abs_path)
            else:
                df = pd.read_excel(abs_path)

            df.columns = df.columns.str.strip().str.lower()
            def generate_unique_color():
                    return "#{:06x}".format(randint(0, 0xFFFFFF))
            tag = generate_unique_color()
            
            for _, row in df.iterrows():

                try:
                    customer = Customer.objects.create(
                        date=row['date'],
                        company_name=row['company_name'],
                        organization_type=row['organization_type'],
                        brand=row['brand'],
                        # category=row['category'],
                        department=row['department'],
                        customer_name=row['customer_name'],
                        designation=row['designation'],
                        country_of_origin=row['coo'],
                        website=row['company_website'],
                        payment_term=row['payment_term'],
                        fabric_reference=row['fabric_reference_dealing_with'],
                        mailing_address=row['mailing_address'],
                        visiting_address=row['visiting_address'],
                        linkedin_profile=row['linkedin_profile_link'],
                        remarks=row['remarks'],
                        concern_fe_rep=row['concern_fe_representative'],
                        tag=tag
                    )
                except Exception as e:
                    messages.error(request, "Invalid data upload. Please check your file and try again.")
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                    request.session.pop('preview_data', None)
                    request.session.pop('temp_file_path', None)
                    return redirect('business_data:customer-upload')

                if customer:
                    if row['customer_email_id']:
                        try:
                            validate_email(row['customer_email_id'])
                            if not PersonEmail.objects.filter(email=row['customer_email_id']).exists():
                                PersonEmail.objects.create(email=row['customer_email_id'], contact_info=customer)
                        except ValidationError:
                            pass  # Invalid email, skip or handle as needed
                    if row['whatsapp_number']:
                        try:
                            PersonPhone.objects.create(phone=row['whatsapp_number'],is_whatsapp=True, contact_info = customer)
                        except ValidationError:
                            messages.error(request,ValidationError)

                    
                    if row['phone_number']:
                        try:
                            PersonPhone.objects.create(phone=row['phone_number'], contact_info=customer)
                        except ValidationError:
                            messages.error(request,ValidationError)

                messages.success(request, "Customers have been successfully saved.")

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:customer-upload')


class CustomerListView(ListView):
    model = Customer
    template_name= "business_data/manage_customers/customer_list.html"


### Generate demo csv for buyers
class GenerateCSVCustomer(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_customer_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "company_name", "organization_type", "brand", "category", "department",
            "customer_name", "designation", "coo", "customer_email_id", "whatsapp_number", "phone_number",
            "company_website", "payment_term", "fabric_reference_dealing_with", "mailing_address",
            "visiting_address", "linkedin_profile_link", "remarks", "concern_fe_representative"
        ])
        writer.writerow([
            "2025-05-13", "Acme Textiles", "Manufacturer", "Acme", "Textile", "Sales",
            "John Doe", "Manager", "Bangladesh", "john.doe@acme.com", "+8801777777254", "+8801555555555",
            "https://acme.com", "Net 30", "Cotton, Denim", "123 Main St, Dhaka", "456 Market Rd, Dhaka",
            "https://linkedin.com/in/johndoe", "Top customer", "Alice Smith"
        ])
        writer.writerow([
            "2025-05-13", "Beta Apparel", "Exporter", "Beta", "Apparel", "Export",
            "Jane Smith", "Director", "India", "jane.smith@beta.com", "+919999999999", "+918888888888",
            "https://beta.com", "Advance", "Knit, Woven", "789 Fashion Ave, Mumbai", "1011 Textile St, Mumbai",
            "https://linkedin.com/in/janesmith", "Prefers organic", "Bob Lee"
        ])

        return response

"""End::Customer Details"""

"""Begin::Supplier Details"""

### Generate demo csv for suppliers
class GenerateCSVSupplier(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_supplier_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "mill_name", "supplier_name", "concern_person_name", "concern_person_designation", "product_category",
            "product_range", "speciality", "coo", "email_id1","email_id2","email_id3",  "phone_number1","phone_number2","whatsapp_number",
            "wechat_number", "payment_term", "fabric_reference_dealing_with", "mailing_address",
            "visiting_address", "linkedin_profile_link", "remarks", "concern_fe_representative"
        ])
        writer.writerow([
            "2025-05-15", "Sunshine Textiles", "Global Fibers Ltd.", "John Doe", "Procurement Manager", "Cotton",
            "Lightweight", "Organic", "India", "john.doe@globalfibers.com", "doe.j@fibersmail.com", "jd.supply@sunshine.com",
            "+91-9876543210", "+91-9123456789", "+91-9876543210",
            "john_doe123", "Net 30", "Ref001", "123 Mill Road, Mumbai, India",
            "456 Corporate Avenue, Mumbai, India", "https://linkedin.com/in/johndoe", "Reliable supplier with on-time delivery", "Fahim Rahman"
        ])

        writer.writerow([
            "2025-05-15", "Evergreen Mills", "Textura Inc.", "Jane Smith", "Supply Chain Director", "Polyester",
            "Heavyweight", "Water-resistant", "China", "jane.smith@textura.cn", "smith.jane@evergreen.com", "jsupplies@textura.cn",
            "+86-1357924680", "+86-1398765432", "+86-1357924680",
            "jane_smith88", "Net 45", "Ref009", "88 Textile Park, Hangzhou, China",
            "12 Industry Street, Hangzhou, China", "https://linkedin.com/in/janesmith", "Interested in sustainable options", "Hasan Chowdhury"
        ])

        return response



# upload suppliers
class SupplierUploadView(View):
    def get(self, request):
        form = FileUploadForm()
        context = {
            'form': form,
            "title": "Import Suppliers",
            "header_title": "Import Suppliers From CSV",
            "card_title": "Import Suppliers",
            "form_button_title": "Import Suppliers",
            'csv_generator_url': reverse_lazy('business_data:supplier-demo-csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context)

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = extract_data(request,form)
            
            request.session['preview_supplier_data'] = data
            return redirect('business_data:supplier-preview')
        context = {
            'form': form,
            "title": "Import Suppliers",
            "header_title": "Import Suppliers From CSV",
            "card_title": "Import Suppliers",
            "form_button_title": "Import Suppliers",
            'csv_generator_url': reverse_lazy('business_data:supplier-demo-csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context) 


# preview supplier 
class SupplierPreviewView(View):
    def get(self, request):
        preview_data = request.session.get('preview_supplier_data', [])
        temp_file_path = request.session.get('temp_file_path', None)
        file_info = {}
        if temp_file_path:
            file_name = os.path.basename(temp_file_path)
            file_info = {
                'name': file_name,
                'url': default_storage.url(temp_file_path),
                'uploaded_at': default_storage.get_created_time(temp_file_path) if default_storage.exists(temp_file_path) else None
            }

        context = {
            'suppliers': preview_data,
            'file_info': file_info,
        }

        return render(request, 'business_data/manage_suppliers/preview.html', context)

    def post(self, request):
        action = request.POST.get('action')
        file_path = request.session.get('temp_file_path')

        if not file_path:
            return redirect('business_data:supplier-upload')

        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if action == 'confirm':
            if file_path.endswith('.csv'):
                df = pd.read_csv(abs_path)
            else:
                df = pd.read_excel(abs_path)

            df.columns = df.columns.str.strip().str.lower()
            def generate_unique_color():
                    return "#{:06x}".format(randint(0, 0xFFFFFF))
            tag = generate_unique_color()
            try:
                with transaction.atomic():
                    for _, row in df.iterrows():
                        # create row and validate 
                        try:
                            supplier = Supplier.objects.create(
                                date=row.get('date'),
                                mill_name=row.get('mill_name'),
                                supplier_name=row.get('supplier_name'),
                                concern_person=row.get('concern_person_name'),
                                concern_person_designation=row.get('concern_person_designation'),
                                product_category=row.get('product_category'),
                                product_range=row.get('product_range'),
                                speciality=row.get('speciality'),
                                country_of_origin=row.get('coo'),
                                # email 
                                # phone 
                                # whatsapp 
                                wechat_id=row.get('wechat_number'),
                                payment_term=row.get('payment_term'),
                                fabric_reference=row.get('fabric_reference_dealing_with'),
                                mailing_address=row.get('mailing_address'),
                                visiting_address=row.get('visiting_address'),
                                linkedin_profile=row.get('linkedin_profile_link'),
                                remarks=row.get('remarks'),
                                concern_fe_rep=row.get('concern_fe_representative'),
                                tag=tag
                            )
                        except Exception as row_e:
                            logger.error(f'Row import failed: {e}')
                            messages.error(request, f"Row import failed: {row_e}")
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                            request.session.pop('preview_product_data', None)
                            request.session.pop('temp_file_path', None)
                            return redirect('business_data:supplier-upload')

                        if supplier:
                            # email ids
                            if row['email_id1']:
                                try:
                                    validate_email(row['email_id1'])
                                    if not PersonEmail.objects.filter(email=row['email_id1']).exists():
                                        PersonEmail.objects.create(email=row['email_id1'], contact_info=supplier)
                                except ValidationError:
                                    pass  # Invalid email, skip or handle as needed
                            if row['email_id2']:
                                try:
                                    validate_email(row['email_id2'])
                                    if not PersonEmail.objects.filter(email=row['email_id2']).exists():
                                        PersonEmail.objects.create(email=row['email_id2'], contact_info=supplier)
                                except ValidationError:
                                    pass  # Invalid email, skip or handle as needed
                            if row['email_id3']:
                                try:
                                    validate_email(row['email_id3'])
                                    if not PersonEmail.objects.filter(email=row['email_id3']).exists():
                                        PersonEmail.objects.create(email=row['email_id3'], contact_info=supplier)
                                except ValidationError:
                                    pass  # Invalid email, skip or handle as needed
                            
                            # whatsapp number 
                            if row['whatsapp_number']:
                                try:
                                    PersonPhone.objects.create(phone=row['whatsapp_number'],is_whatsapp=True, contact_info = supplier)
                                except ValidationError:
                                    messages.error(request,ValidationError)

                            # phone numbers 
                            if row['phone_number1']:
                                try:
                                    PersonPhone.objects.create(phone=row['phone_number1'], contact_info=supplier)
                                except ValidationError:
                                    messages.error(request,ValidationError)
                            if row['phone_number2']:
                                try:
                                    PersonPhone.objects.create(phone=row['phone_number2'], contact_info=supplier)
                                except ValidationError:
                                    messages.error(request,ValidationError)

                    messages.success(request, "Suppliers have been successfully saved.")

            except Exception as e:
                logger.error(f"Bulk import failed: {e}")
                messages.error(request, "Bulk import failed. Please check your file and try again.")
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                request.session.pop('preview_product_data', None)
                request.session.pop('temp_file_path', None)
                return redirect('business_data:supplier-upload')

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_product_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:supplier-upload') 


# supplier list 
class SupplierListView(ListView):
    model = Supplier
    template_name = "business_data/manage_suppliers/supplier_list.html"

    # def get_queryset(self):
    #     return Supplier.objects.filter(is_deleted=False)


# soft delete supplier 
class DeleteSupplierView(UpdateView,LoginRequiredMixin, PermissionRequiredMixin):
    model = Supplier
    fields= ['is_deleted']
    permission_required = 'business_data.delete_supplier'

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Supplier.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected suppliers deleted successfully.'})

"""End::Supplier Details"""

"""Begin::Product Details"""
# generate csv file of product details 
class GenerateCSVProduct(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_product_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "fabric_article_supplier", "fabric_article_fabric_expo", "fabric_mill_supplier", "rd_generated_date", "fabric_mill_source",
            "coo", "product_category", "mill_reference", "fabric_expo_reference","season","style",  "po","customer_name","composition",
            "construction", "weight", "color", "cut_width",
            "wash", "price_per_yard", "shrinkage_percent", "stock_qty",
            "images", "barcode", "qr_code", "concern_person"
        ])

        writer.writerow([
            "2025-05-16", "ABC Textiles Ltd", "ExpoTex 2025", "Global Mills Co.", "2025-04-01", "China",
            "CN", "Denim", "GM1234", "ETX-567", "Spring/Summer", "ST-001", "PO12345", "Levi's", "98% Cotton, 2% Spandex",
            "3x1 Right Hand Twill", "12 oz", "Indigo Blue", "58 in",
            "Enzyme Wash", "7.50", "2.5", "1200",
            "image1.png", "123456789012", "https://example.com/qrcode1", "John Doe"
        ])

        writer.writerow([
            "2025-05-16", "XYZ Fabrics", "Global Fabric Expo", "TexSource India", "2025-03-20", "India",
            "IN", "Twill", "TX5678", "GFE-789", "Fall/Winter", "ST-002", "PO67890", "Zara", "100% Cotton",
            "2x2 Twill", "10 oz", "Charcoal Grey", "56 in",
            "Stone Wash", "6.80", "3.0", "850",
            "image2.jpg", "987654321098", "https://example.com/qrcode2", "Jane Smith"
        ])

        writer.writerow([
            "2025-05-16", "Elite Textiles", "AsiaTex Show", "Premium Mills", "2025-02-15", "Bangladesh",
            "BD", "Chino", "PM7890", "ATS-234", "Resort", "ST-003", "PO11223", "H&M", "97% Cotton, 3% Elastane",
            "Fine Chino Weave", "8 oz", "Khaki", "60 in",
            "No Wash", "5.95", "1.8", "500",
            "image2.png", "456789123456", "https://example.com/qrcode3", "Alex Lee"
        ])


        return response
 

# upload product details 
class ProductUploadView(View):
    def get(self, request):
        form = FileUploadForm()
        context = {
            'form': form,
            "title": "Import Products",
            "header_title": "Import Products From CSV",
            "card_title": "Import Products",
            "form_button_title": "Import Products",
            'csv_generator_url': reverse_lazy('business_data:product-demo-csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context)

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = extract_data(request,form)
            
            request.session['preview_product_data'] = data
            return redirect('business_data:product-preview')
        context = {
            'form': form,
            "title": "Import Products",
            "header_title": "Import Products From CSV",
            "card_title": "Import Products",
            "form_button_title": "Import Products",
            'csv_generator_url': reverse_lazy('business_data:product_demo_csv'), 
        }
        return render(request, 'business_data/forms/upload.html', context) 



# preview product list 
class ProductPreviewView(View):
    def get(self, request):
        preview_data = request.session.get('preview_product_data', [])
        temp_file_path = request.session.get('temp_file_path', None)
        file_info = {}
        if temp_file_path:
            file_name = os.path.basename(temp_file_path)
            file_info = {
                'name': file_name,
                'url': default_storage.url(temp_file_path),
                'uploaded_at': default_storage.get_created_time(temp_file_path) if default_storage.exists(temp_file_path) else None
            }

        context = {
            'products': preview_data,
            'file_info': file_info,
        }

        return render(request, 'business_data/manage_products/preview.html', context)

    def post(self, request):
        action = request.POST.get('action')
        file_path = request.session.get('temp_file_path')

        if not file_path:
            return redirect('business_data:product-upload')

        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if action == 'confirm':
            if file_path.endswith('.csv'):
                df = pd.read_csv(abs_path)
            else:
                df = pd.read_excel(abs_path)
            
            df.columns = df.columns.str.strip().str.lower()
            def generate_unique_color():
                    return "#{:06x}".format(randint(0, 0xFFFFFF))
            tag = generate_unique_color()
            try:
                with transaction.atomic():
                    for _, row in df.iterrows():
                        try:
                            Product.objects.create(
                                date=row.get('date'),
                                fabric_article_supplier=row.get('fabric_article_supplier', ''),
                                fabric_article_fexpo=row.get('fabric_article_fabric_expo', ''),
                                fabric_mill_supplier=row.get('fabric_mill_supplier', ''),
                                rd_generated_date=row.get('rd_generated_date', ''),
                                fabric_mill_source=row.get('fabric_mill_source', ''),
                                coo=row.get('coo', ''),
                                product_category=row.get('product_category', ''),
                                mill_reference=row.get('mill_reference', ''),
                                fabricexpo_reference=row.get('fabric_expo_reference', ''),
                                season=row.get('season', ''),
                                style=row.get('style', ''),
                                po=row.get('po', ''),
                                customer_name=row.get('customer_name', ''),
                                composition=row.get('composition', ''),
                                construction=row.get('construction', ''),
                                weight=row.get('weight', ''),
                                color=row.get('color', ''),
                                cut_width=row.get('cut_width', ''),
                                wash=row.get('wash', ''),
                                price_per_yard=row.get('price_per_yard', 0),
                                shrinkage_percent=row.get('shrinkage_percent', 0),
                                stock_qty=row.get('stock_qty', 0),
                                barcode=row.get('barcode', ''),
                                qr_code=row.get('qr_code', ''),
                                concern_person=row.get('concern_person', ''),
                                tag=tag
                            )
                        except Exception as row_e:
                            logger.error("Row import failed: %s", row_e)
                            messages.error(request, f"Row import failed: {row_e}")
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                            request.session.pop('preview_product_data', None)
                            request.session.pop('temp_file_path', None)
                            return redirect('business_data:product-upload')
                    messages.success(request, "Products have been successfully saved.")
            except Exception as e:
                logger.error("Bulk import failed: %s", e)
                messages.error(request, "Bulk import failed. Please check your file and try again.")
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                request.session.pop('preview_product_data', None)
                request.session.pop('temp_file_path', None)
                return redirect('business_data:product-upload')


        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_product_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:product-upload') 
# Product list 
class ProductListView(ListView):
    model = Product
    template_name = "business_data/manage_products/product_list.html"


# delete products 
class DeleteProductView(UpdateView,LoginRequiredMixin, PermissionRequiredMixin):
    model = Product
    fields= ['is_deleted']
    permission_required = 'business_data.delete_product'

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Product.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected products deleted successfully.'})


"""End::Product Details"""

