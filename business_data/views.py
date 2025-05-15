import csv
import os
from random import randint

from django.urls import reverse_lazy
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from business_data.models import Buyer, PersonEmail, PersonPhone, Supplier, Customer, Product
import phonenumber_field

from .forms import BuyerUploadForm, FileUploadForm

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
                        PersonPhone.objects.create(phone=row['whatsapp_number'],is_whatsapp=True, contact_info = buyer)
                        try:
                            PersonPhone.objects.create(phone=row['whatsapp_number'], contact_info=buyer)
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
                        PersonPhone.objects.create(phone=row['whatsapp_number'],is_whatsapp=True, contact_info = customer)
                        try:
                            PersonPhone.objects.create(phone=row['whatsapp_number'], contact_info=customer)
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
"""End::Supplier Details"""

"""Begin::Product Details"""
"""End::Product Details"""