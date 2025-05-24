import csv
import os
from random import randint
import logging
logger = logging.getLogger(__name__)

from django.db import transaction

from django.urls import reverse_lazy
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from business_data.models import Buyer, PersonEmail, PersonPhone, Supplier, Customer, Product

from .forms import BuyerUploadForm, FileUploadForm

from faker import Faker
from random import randint, choice, uniform

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
    print(data)
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

            try: 
                with transaction.atomic():
                    for _, row in df.iterrows():
                        try:
                            buyer = Buyer.objects.create(
                                date=row.get('date'),
                                company_name=row.get('company_name'),
                                organization_type=row.get('organization_type'),
                                brand=row.get('brand'),
                                category=row.get('category'),
                                department=row.get('department'),
                                buyer_name=row.get('buyer_name'),
                                designation=row.get('designation'),
                                country_of_origin=row.get('coo'),
                                website=row.get('company_website'),
                                payment_term=row.get('payment_term'),
                                fabric_reference=row.get('fabric_reference_dealing_with'),
                                mailing_address=row.get('mailing_address'),
                                visiting_address=row.get('visiting_address'),
                                linkedin_profile=row.get('linkedin_profile_link'),
                                remarks=row.get('remarks'),
                                concern_fe_rep=row.get('concern_fe_representative'),
                                tag=tag
                            )
                        except Exception as e:
                            messages.error(request, "Invalid data upload. Please check your file and try again.")
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                            request.session.pop('preview_buyer_data', None)
                            request.session.pop('temp_file_path', None)
                            return redirect('business_data:buyer-upload')

                        if buyer:
                            if row['buyer_email_id']:
                                try:
                                    validate_email(row['buyer_email_id'])
                                    if not PersonEmail.objects.filter(email=row['buyer_email_id']).exists():
                                        PersonEmail.objects.create(email=row['buyer_email_id'], contact_info=buyer)
                                    else:
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

            except Exception as e:
                logger.error(f"Bulk import failed: {e}")
                messages.error(request, "Bulk import failed. Please check your file and try again.")
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                request.session.pop('preview_buyer_data', None)
                request.session.pop('temp_file_path', None)
                return redirect('business_data:buyer-upload')


        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_buyer_data', None)
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


# delete customers 
class DeleteBuyerView(UpdateView,LoginRequiredMixin, PermissionRequiredMixin):
    model = Buyer
    fields = ['is_deleted']
    permission_required = 'business_data.delete_buyer'

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Buyer.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected buyers deleted successfully.'})

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

            try:
                with transaction.atomic():
                    for _, row in df.iterrows():
                        try:
                            customer = Customer.objects.create(
                                date=row.get('date'),
                                company_name=row.get('company_name'),
                                organization_type=row.get('organization_type'),
                                brand=row.get('brand'),
                                # category=row['category'],
                                department=row.get('department'),
                                customer_name=row.get('customer_name'),
                                designation=row.get('designation'),
                                country_of_origin=row.get('coo'),
                                website=row.get('company_website'),
                                payment_term=row.get('payment_term'),
                                fabric_reference=row.get('fabric_reference_dealing_with'),
                                mailing_address=row.get('mailing_address'),
                                visiting_address=row.get('visiting_address'),
                                linkedin_profile=row.get('linkedin_profile_link'),
                                remarks=row.get('remarks'),
                                concern_fe_rep=row.get('concern_fe_representative'),
                                tag=tag
                            )
                        # if any error occurs return the with error 
                        except Exception as e:
                            logger.error(f"Row import failed: {e}")
                            messages.error(request, f"Row import failed: {e}")
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                            request.session.pop('preview_customer_data', None)
                            request.session.pop('temp_file_path', None)
                            return redirect('business_data:customer-upload')

                        # insert emails and other relational data
                        if customer:
                            if row['customer_email_id']:
                                print(row.get('customer_email_id'))
                                email = row.get('customer_email_id')
                                try:
                                    validate_email(email)
                                    # if not PersonEmail.objects.filter(email=email).exists():
                                        # print("Here you are ======================")

                                    PersonEmail.objects.create(email=email, contact_info=customer)

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

                    messages.success(request, "Customers has been successfully saved.")
            except Exception as e:
                logger.error(f"Bulk import failed: {e}")
                messages.error(request, "Bulk import failed. Please check your file and try again.")
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                request.session.pop('preview_customer_data', None)
                request.session.pop('temp_file_path', None)
                return redirect('business_data:supplier-upload')

        
        # request from another place 
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_customer_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:customer-upload')


class CustomerListView(ListView):
    model = Customer
    template_name= "business_data/manage_customers/customer_list.html"


# delete customers 
class DeleteCustomerView(UpdateView,LoginRequiredMixin, PermissionRequiredMixin):
    model = Customer
    fields = ['is_deleted']
    permission_required = 'business_data.delete_customer'

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        print(ids)
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Customer.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected customers deleted successfully.'})


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
                            logger.error(f'Row import failed: {row_e}')
                            messages.error(request, f"Row import failed: {row_e}")
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                            request.session.pop('preview_supplier_data', None)
                            request.session.pop('temp_file_path', None)
                            return redirect('business_data:supplier-upload')

                        if supplier:
                            # email ids
                            if row['email_id1']:
                                try:
                                    validate_email(row['email_id1'])
                                    if not PersonEmail.objects.filter(email=row['email_id1']).exists():
                                        PersonEmail.objects.create(email=row['email_id1'], contact_info=supplier)
                                    else:
                                        PersonEmail.objects.create(email=row['email_id1'], contact_info=supplier)
                                except ValidationError:
                                    pass  # Invalid email, skip or handle as needed
                            if row['email_id2']:
                                try:
                                    validate_email(row['email_id2'])
                                    if not PersonEmail.objects.filter(email=row['email_id2']).exists():
                                        PersonEmail.objects.create(email=row['email_id2'], contact_info=supplier)
                                    else:
                                        PersonEmail.objects.create(email=row['email_id2'], contact_info=supplier)
                                except ValidationError:
                                    pass  # Invalid email, skip or handle as needed
                            if row['email_id3']:
                                try:
                                    validate_email(row['email_id3'])
                                    if not PersonEmail.objects.filter(email=row['email_id3']).exists():
                                        PersonEmail.objects.create(email=row['email_id3'], contact_info=supplier)
                                    else:
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
                request.session.pop('preview_supplier_data', None)
                request.session.pop('temp_file_path', None)
                return redirect('business_data:supplier-upload')

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_supplier_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:supplier-upload') 


# supplier list 
class SupplierListView(ListView):
    model = Supplier
    template_name = "business_data/manage_suppliers/supplier_list.html"


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

        """begin::faker"""
        fake = Faker()
        categories = ["Denim", "Twill", "Chino", "Cotton", "Polyester"]
        seasons = ["Spring/Summer", "Fall/Winter", "Resort"]
        washes = ["Enzyme Wash", "Stone Wash", "No Wash", "Acid Wash"]
        colors = ["Indigo Blue", "Charcoal Grey", "Khaki", "Black", "White"]
        images = ["image1.png", "image2.jpg", "image2.png"]

        for _ in range(10):  # Change to any number you want
            writer.writerow([
                fake.date_this_decade().strftime("%Y-%m-%d"),
                fake.company(),
                fake.company(),
                fake.company(),
                fake.date_this_decade().strftime("%Y-%m-%d"),
                fake.country(),
                fake.country_code(),
                choice(categories),
                fake.bothify(text="??####"),
                fake.bothify(text="??-###"),
                choice(seasons),
                fake.bothify(text="ST-###"),
                fake.bothify(text="PO#####"),
                fake.company(),
                f"{randint(90, 100)}% Cotton, {randint(0, 10)}% Spandex",
                fake.word().capitalize() + " Weave",
                f"{randint(7, 14)} oz",
                choice(colors),
                f"{randint(50, 65)} in",
                choice(washes),
                round(uniform(3.0, 15.0), 2),
                round(uniform(1.0, 5.0), 2),
                randint(100, 5000),
                choice(images),
                fake.ean13(),
                fake.url(),
                fake.name()
            ])

        """end::faker"""
        # writer.writerow([
        #     "2025-05-16", "ABC Textiles Ltd", "ExpoTex 2025", "Global Mills Co.", "2025-04-01", "China",
        #     "CN", "Denim", "GM1234", "ETX-567", "Spring/Summer", "ST-001", "PO12345", "Levi's", "98% Cotton, 2% Spandex",
        #     "3x1 Right Hand Twill", "12 oz", "Indigo Blue", "58 in",
        #     "Enzyme Wash", "7.50", "2.5", "1200",
        #     "image1.png", "123456789012", "https://example.com/qrcode1", "John Doe"
        # ])

        # writer.writerow([
        #     "2025-05-16", "XYZ Fabrics", "Global Fabric Expo", "TexSource India", "2025-03-20", "India",
        #     "IN", "Twill", "TX5678", "GFE-789", "Fall/Winter", "ST-002", "PO67890", "Zara", "100% Cotton",
        #     "2x2 Twill", "10 oz", "Charcoal Grey", "56 in",
        #     "Stone Wash", "6.80", "3.0", "850",
        #     "image2.jpg", "987654321098", "https://example.com/qrcode2", "Jane Smith"
        # ])

        # writer.writerow([
        #     "2025-05-16", "Elite Textiles", "AsiaTex Show", "Premium Mills", "2025-02-15", "Bangladesh",
        #     "BD", "Chino", "PM7890", "ATS-234", "Resort", "ST-003", "PO11223", "H&M", "97% Cotton, 3% Elastane",
        #     "Fine Chino Weave", "8 oz", "Khaki", "60 in",
        #     "No Wash", "5.95", "1.8", "500",
        #     "image2.png", "456789123456", "https://example.com/qrcode3", "Alex Lee"
        # ])


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

class ProductListView(TemplateView):
    # model = Product
    template_name = "business_data/manage_products/product_list.html"

class ProductDataSourceView(View):
    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_column_index = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', 'asc')  # safer default

        columns = [
            'id', 'date', 'fabric_article_supplier', 'fabric_article_fexpo', 'fabric_mill_supplier',
            'rd_generated_date', 'fabric_mill_source', 'coo', 'product_category', 'mill_reference',
            'fabricexpo_reference', 'season', 'style', 'po', 'customer_name', 'composition',
            'construction', 'weight', 'color', 'cut_width', 'wash', 'price_per_yard',
            'shrinkage_percent', 'stock_qty', 'images', 'barcode', 'qr_code', 'concern_person'
        ]

        # order_field = columns[int(order_column_index)] if int(order_column_index) < len(columns) else 'id'
        # if order_dir == 'desc':
        #     order_field = '-' + order_field
        if 0 <= order_column_index < len(columns):
            order_field = columns[order_column_index]
            if order_dir == 'desc':
                order_field = '-' + order_field
        else:
            order_field = 'id'  # fallback


        qs = Product.objects.all()

        if search_value:
            search_q = Q()
            # List of fields to search (including id and all relevant fields)
            search_fields = [
            'id',
            'date',
            'fabric_article_supplier',
            'fabric_article_fexpo',
            'fabric_mill_supplier',
            'rd_generated_date',
            'fabric_mill_source',
            'coo',
            'product_category',
            'mill_reference',
            'fabricexpo_reference',
            'season',
            'style',
            'po',
            'customer_name',
            'composition',
            'construction',
            'weight',
            'color',
            'cut_width',
            'wash',
            'price_per_yard',
            'shrinkage_percent',
            'stock_qty',
            'barcode',
            'qr_code',
            'concern_person',
            'tag',
            ]
            for col in search_fields:
                search_q |= Q(**{f"{col}__icontains": search_value})
            qs = qs.filter(search_q)

        total_count = Product.objects.count()
        filtered_count = qs.count()

        qs = qs.order_by(order_field)[start:start+length]

        data = []
        for idx,obj in enumerate(qs,start=start+1):
        
            data.append([
                idx,  # For Count column (can be filled on client side)
                obj.id,
                obj.date,
                obj.fabric_article_supplier,
                obj.fabric_article_fexpo,
                obj.fabric_mill_supplier,
                obj.rd_generated_date,
                obj.fabric_mill_source,
                obj.coo,
                obj.product_category,
                obj.mill_reference,
                obj.fabricexpo_reference,
                obj.season,
                obj.style,
                obj.po,
                obj.customer_name,
                obj.composition,
                obj.construction,
                obj.weight,
                obj.color,
                obj.cut_width,
                obj.wash,
                obj.price_per_yard,
                obj.shrinkage_percent,
                obj.stock_qty,
                '',  # images (handle as needed)
                obj.barcode,
                obj.qr_code,
                obj.concern_person,
            ])

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data,
        })
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

