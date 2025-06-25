import csv
from decimal import Decimal
import os
from random import randint
import logging
logger = logging.getLogger(__name__)

from django.db import transaction

from datetime import datetime

from django.urls import reverse_lazy
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from business_data.models import Buyer, PersonEmail, PersonPhone, Supplier, Customer, Product

from .forms import BuyerUploadForm, FileUploadForm

from faker import Faker
from random import randint, choice, uniform
from collections import defaultdict
from pprint import pprint
from weasyprint import HTML
from django.template.loader import render_to_string

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
### Generate demo csv for buyers
class GenerateCSVBuyer(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_buyer"
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_buyer_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "company_name", "organization_type", "brand", "category", "department",
            "buyer_name", "designation", "country_of_origin", "buyer_email_id", "whatsapp_number", "phone_number",
            "website", "payment_term", "fabric_reference", "mailing_address",
            "visiting_address", "linkedin_profile", "remarks", "concern_fe_rep"
        ])

        fake = Faker()
        org_types = ["Manufacturer", "Exporter", "Retailer", "Wholesaler"]
        categories = ["Textile", "Apparel", "Fashion", "Accessories"]
        departments = ["Sales", "Export", "Procurement", "Design"]
        designations = ["Manager", "Director", "Executive", "Lead"]
        payment_terms = ["Net 30", "Advance", "LC at Sight"]
        remarks_list = [
            "Top buyer", "Prefers organic", "Bulk buyer", "Fast payment", "Long-term client"
        ]
        for _ in range(10):
            writer.writerow([
                # fake.date_this_decade().strftime("%Y-%m-%d"),
                fake.date_this_decade().strftime("%d/%m/%Y"),
                fake.company(),
                fake.random_element(org_types),
                fake.company_suffix(),
                fake.random_element(categories),
                fake.random_element(departments),
                fake.name(),
                fake.random_element(designations),
                fake.country(),
                fake.email(),
                f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # WhatsApp number (Bangladesh)
                f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # Phone number (Bangladesh)
                fake.url(),
                fake.random_element(payment_terms),
                ", ".join([fake.word().capitalize() for _ in range(2)]),
                fake.address().replace('\n', ', '),
                fake.address().replace('\n', ', '),
                fake.url(),
                fake.random_element(remarks_list),
                fake.name()
            ])

        return response


# upload buyer data
class BuyerUploadView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_buyer"
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
class BuyerPreviewView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_buyer"

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
        
        # List all fields you want to check for duplicates
        fields_to_check = [
            'date','company_name', 'organization_type', 'brand', 'category', 'department',
            'buyer_name', 'designation', 'country_of_origin', 
            'buyer_email_id', 'whatsapp_number', 'phone_number',
            'payment_term', 'fabric_reference', 'mailing_address',
            'visiting_address', 'linkedin_profile', 'remarks', 'concern_fe_rep','website',
        ]

        # Build sets of existing values for each field
        existing_values = defaultdict(set)

        for field in fields_to_check:
            # Direct model fields
            if field in [f.name for f in Buyer._meta.get_fields() if not f.is_relation]:
                existing_values[field] = set(Buyer.objects.values_list(field, flat=True))
            # Related email field
            elif field == 'buyer_email_id':
                existing_values[field] = set(
                    PersonEmail.objects.filter(contact_info_id__in=Buyer.objects.values('id')).values_list('email', flat=True)
                )
            elif field == 'phone_number':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Buyer.objects.values_list('id', flat=True),
                        is_whatsapp=False
                    ).values_list('phone', flat=True)
                )
            elif field == 'whatsapp_number':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Buyer.objects.values_list('id', flat=True),
                        is_whatsapp=True
                    ).values_list('phone', flat=True)
                )

        # Mark duplicates for each cell
        for row in preview_data:
            row['duplicates'] = {}

            for field in fields_to_check:
                value = row.get(field)

                # if field == 'buyer_email_id':
                #     row['duplicates'][field] = value in existing_values[field] if value else False
                if field == 'date':
                    
                    value = datetime.strptime(value, "%d/%m/%Y").date()
                    row['duplicates'][field] = value in existing_values[field] if value else False
                else:
                    row['duplicates'][field] = value in existing_values[field] if value else False

        context = {
            'buyers': preview_data,
            'file_info': file_info,
            'has_duplicates': any(any(row['duplicates'].values()) for row in preview_data),
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
                                # date=row.get('date'),datetime.strptime(date_str, "%d/%m/%Y").date()
                                date= datetime.strptime(row.get('date'), "%d/%m/%Y").date(),
                                company_name=row.get('company_name'),
                                organization_type=row.get('organization_type'),
                                brand=row.get('brand'),
                                category=row.get('category'),
                                department=row.get('department'),
                                buyer_name=row.get('buyer_name'),
                                designation=row.get('designation'),
                                country_of_origin=row.get('country_of_origin'),
                                website=row.get('website'),
                                payment_term=row.get('payment_term'),
                                fabric_reference=row.get('fabric_reference'),
                                mailing_address=row.get('mailing_address'),
                                visiting_address=row.get('visiting_address'),
                                linkedin_profile=row.get('linkedin_profile'),
                                remarks=row.get('remarks'),
                                concern_fe_rep=row.get('concern_fe_rep'),
                                tag=tag
                            )
                        except Exception as e:
                            print(f"Row import failed: {e}")
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


# Buyer list 
class BuyerListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "business_data.view_buyer"
    template_name = "business_data/manage_buyers/buyer_list.html"

class BuyerDataSourceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_buyer"
    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_col_index = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', 'asc')

        columns = [
            'id',
            'date',
            'company_name',
            'organization_type',
            'brand',
            'category',
            'department',
            'buyer_name',
            'designation',
            'country_of_origin',
            'website',
            'emails__email',
            'phones__phone',
            'phones__phone',
            'payment_term',
            'fabric_reference',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
            'tag',
        ]

        order_column = columns[order_col_index] if 0 <= order_col_index < len(columns) else 'id'
        if order_dir == 'asc':
            order_column = '-' + order_column

        qs = Buyer.objects.all().prefetch_related('emails', 'phones')

        if search_value:
            search_q = Q()
            search_fields = columns[:-1]
            for field in search_fields:
                search_q |= Q(**{f"{field}__icontains": search_value})
            qs = qs.filter(search_q)

        total_count = Buyer.objects.count()
        filtered_count = qs.count()

        qs = qs.order_by(order_column)[start:start + length]

        data = []
        for obj in qs:
            # emails = ', '.join([email.email for email in obj.emails.all()])
            # whatsapp_numbers = ', '.join([phone.phone for phone in obj.phones.all() if getattr(phone, 'is_whatsapp', False)])
            # phones = ', '.join([
            # phone.phone for phone in obj.phones.all()
            # if not getattr(phone, 'is_whatsapp', False) and not getattr(phone, 'is_wechat', False)
            # ])
            data.append({
                'id': obj.id,
                'date': obj.date,
                'company_name': getattr(obj, 'company_name', ''),
                'organization_type': getattr(obj, 'organization_type', ''),
                'brand': getattr(obj, 'brand', ''),
                'category': getattr(obj, 'category', ''),
                'department': getattr(obj, 'department', ''),
                'buyer_name': getattr(obj, 'buyer_name', ''),
                'designation': getattr(obj, 'designation', ''),
                'country_of_origin': getattr(obj, 'country_of_origin', ''),
                'website': getattr(obj, 'website', ''),
                'emails': ', '.join([email.email for email in obj.emails.all()]),
                'phones': ', '.join([phone.phone for phone in obj.phones.all() if not phone.is_whatsapp]),
                'whatsapp_numbers': ', '.join([phone.phone for phone in obj.phones.all() if phone.is_whatsapp]),
                'payment_term': getattr(obj, 'payment_term', ''),
                'fabric_reference': getattr(obj, 'fabric_reference', ''),
                'mailing_address': getattr(obj, 'mailing_address', ''),
                'visiting_address': getattr(obj, 'visiting_address', ''),
                'linkedin_profile': getattr(obj, 'linkedin_profile', ''),
                'remarks': getattr(obj, 'remarks', ''),
                'concern_fe_rep': getattr(obj, 'concern_fe_rep', ''),
                'tag': getattr(obj, 'tag', ''),
                'DT_RowAttr': {
                    'data-id': obj.id,
                }
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data,
        })

# delete customers 
class DeleteBuyerView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "business_data.delete_buyer"
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

### Generate demo csv for customer
class GenerateCSVCustomer(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_customer"
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_customer_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "company_name", "organization_type", "brand", "category", "department",
            "customer_name", "designation", "country_of_origin", "customer_email_id", "whatsapp_number", "phone_number",
            "website", "payment_term", "fabric_reference", "mailing_address",
            "visiting_address", "linkedin_profile", "remarks", "concern_fe_rep"
        ])

        fake = Faker()
        org_types = ["Manufacturer", "Exporter", "Retailer", "Wholesaler"]
        categories = ["Textile", "Apparel", "Fashion", "Accessories"]
        departments = ["Sales", "Export", "Procurement", "Design"]
        designations = ["Manager", "Director", "Executive", "Lead"]
        payment_terms = ["Net 30", "Advance", "LC at Sight"]
        remarks_list = [
            "Top customer", "Prefers organic", "Bulk buyer", "Fast payment", "Long-term client"
        ]
        for _ in range(20):
            writer.writerow([
            # fake.date_this_decade().strftime("%Y-%m-%d"),
            fake.date_this_decade().strftime("%d/%m/%Y"),
            fake.company(),
            fake.random_element(org_types),
            fake.company_suffix(),
            fake.random_element(categories),
            fake.random_element(departments),
            fake.name(),
            fake.random_element(designations),
            fake.country(),
            fake.email(),
            # fake.phone_number(),
            # fake.phone_number(),
            f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # WhatsApp number (Bangladesh)
            f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # Phone number (Bangladesh)
            fake.url(),
            fake.random_element(payment_terms),
            ", ".join([fake.word().capitalize() for _ in range(2)]),
            fake.address().replace('\n', ', '),
            fake.address().replace('\n', ', '),
            fake.url(),
            fake.random_element(remarks_list),
            fake.name()
            ])
        
        return response



# upload customer data
class CustomerUploadView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_customer"

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
class CustomerPreviewView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_customer"

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

        # List all fields you want to check for duplicates
        fields_to_check = [
            "date", "company_name", "organization_type", "brand", "category", "department",
            "customer_name", "designation", "country_of_origin", "customer_email_id", "whatsapp_number", "phone_number",
            "website", "payment_term", "fabric_reference", "mailing_address",
            "visiting_address", "linkedin_profile", "remarks", "concern_fe_rep"
        ]

        # Build sets of existing values for each field
        existing_values = defaultdict(set)

        for field in fields_to_check:
            # Direct model fields
            if field in [f.name for f in Customer._meta.get_fields() if not f.is_relation]:
                existing_values[field] = set(Customer.objects.values_list(field, flat=True))
            
            # Related email field
            elif field == 'customer_email_id':
                existing_values[field] = set(
                    PersonEmail.objects.filter(contact_info_id__in=Customer.objects.values('id')).values_list('email', flat=True)
                )

            elif field == 'phone_number':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Customer.objects.values_list('id', flat=True),
                        is_whatsapp=False
                    ).values_list('phone', flat=True)
                )

            elif field == 'whatsapp_number':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Customer.objects.values_list('id', flat=True),
                        is_whatsapp=True
                    ).values_list('phone', flat=True)
                )

        # Mark duplicates for each cell
        for row in preview_data:
            row['duplicates'] = {}

            for field in fields_to_check:
                value = row.get(field)

                if field == 'date':
                    value = datetime.strptime(value, "%d/%m/%Y").date()
                    row['duplicates'][field] = value in existing_values[field] if value else False
                else:
                    row['duplicates'][field] = value in existing_values[field] if value else False

        
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
                                date=datetime.strptime(row.get('date'), "%d/%m/%Y").date(),
                                company_name=row.get('company_name'),
                                organization_type=row.get('organization_type'),
                                brand=row.get('brand'),
                                # category=row['category'],
                                department=row.get('department'),
                                customer_name=row.get('customer_name'),
                                designation=row.get('designation'),
                                country_of_origin=row.get('country_of_origin'),
                                website=row.get('website'),
                                payment_term=row.get('payment_term'),
                                fabric_reference=row.get('fabric_reference'),
                                mailing_address=row.get('mailing_address'),
                                visiting_address=row.get('visiting_address'),
                                linkedin_profile=row.get('linkedin_profile'),
                                remarks=row.get('remarks'),
                                concern_fe_rep=row.get('concern_fe_rep'),
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


class CustomerListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "business_data.view_customer"

    template_name= "business_data/manage_customers/customer_list.html"


# customer data source 
class CustomerDataSourceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_customer"

    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get('draw',1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_col_index = request.GET.get('order[0][column]', 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')


        columns = [
            'id',
            'date',
            'company_name',
            'organization_type',
            'brand',
            # 'category',  # commented out in model creation
            'department',
            'customer_name',
            'designation',
            'country_of_origin',
            'website',
            'emails__email',
            'phones__phone',
            'phones__phone',
            'payment_term',
            'fabric_reference',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
            'tag',
        ]

        order_column = columns[int(order_col_index)]
        if order_dir == 'asc':
            order_column = '-' + order_column

        # get supplier list 
        qs = Customer.objects.all()
        
        if search_value:
            search_q = Q()
            # List of fields to search (including id and all relevant fields)
            search_fields = [
                'id',
                'date',
                'company_name',
                'organization_type',
                'brand',
                # 'category',
                'department',
                'customer_name',
                'designation',
                'country_of_origin',
                'website',
                'emails__email',
                'phones__phone',
                'payment_term',
                'fabric_reference',
                'mailing_address',
                'visiting_address',
                'linkedin_profile',
                'remarks',
                'concern_fe_rep',
            ]

            for col in search_fields:
                search_q |= Q(**{f"{col}__icontains": search_value})
            qs = qs.filter(search_q)

        total_count = Product.objects.count()
        filtered_count = qs.count()

        # Ordering and pagination
        qs = qs.order_by(order_column)[start:start + length]

        data = []
        for obj in qs:
            data.append({
                'id': obj.id,
                'date': obj.date,
                'company_name': getattr(obj, 'company_name', ''),
                'organization_type': getattr(obj, 'organization_type', ''),
                'brand': getattr(obj, 'brand', ''),
                # 'category': getattr(obj, 'category', ''),
                'department': getattr(obj, 'department', ''),
                'customer_name': getattr(obj, 'customer_name', ''),
                'designation': getattr(obj, 'designation', ''),
                'country_of_origin': getattr(obj, 'country_of_origin', ''),
                'website': getattr(obj, 'website', ''),
                'emails': ', '.join([p.email for p in obj.emails.all()]),
                'phones': ', '.join([p.phone for p in obj.phones.all() if not p.is_whatsapp]),
                'whatsapp_numbers': ', '.join([p.phone for p in obj.phones.all() if p.is_whatsapp]),
                'payment_term': getattr(obj, 'payment_term', ''),
                'fabric_reference': getattr(obj, 'fabric_reference', ''),
                'mailing_address': getattr(obj, 'mailing_address', ''),
                'visiting_address': getattr(obj, 'visiting_address', ''),
                'linkedin_profile': getattr(obj, 'linkedin_profile', ''),
                'remarks': getattr(obj, 'remarks', ''),
                'concern_fe_rep': getattr(obj, 'concern_fe_rep', ''),
                'tag': getattr(obj, 'tag', ''),
                'DT_RowAttr': {
                    'data-id': obj.id,
                }
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data,
        })


# delete customers 
class DeleteCustomerView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "business_data.delete_customer"

    model = Customer
    fields = ['is_deleted']

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        print(ids)
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Customer.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected customers deleted successfully.'})


"""End::Customer Details"""

"""Begin::Supplier Details"""

### Generate demo csv for suppliers
class GenerateCSVSupplier(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_supplier"
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_supplier_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "mill_name", "supplier_name", "concern_person", "concern_person_designation", "product_category",
            "product_range", "speciality", "country_of_origin", "email_id1","email_id2","email_id3",  "phone_number1","phone_number2","whatsapp_number",
            "wechat_id", "payment_term", "fabric_reference", "mailing_address",
            "visiting_address", "linkedin_profile", "remarks", "concern_fe_rep"
        ])

        fake = Faker()
        categories = ["Cotton", "Polyester", "Denim", "Linen", "Wool"]
        ranges = ["Lightweight", "Heavyweight", "Mediumweight", "Stretch", "Non-stretch"]
        specialities = ["Organic", "Water-resistant", "Sustainable", "Recycled", "Premium"]
        designations = ["Procurement Manager", "Supply Chain Director", "Sales Lead", "Account Manager", "Operations Head"]
        payment_terms = ["Net 30", "Net 45", "Advance", "LC at Sight"]
        remarks_list = [
            "Reliable supplier with on-time delivery",
            "Interested in sustainable options",
            "Excellent quality control",
            "Flexible payment terms",
            "Fast response time"
        ]
        for _ in range(10):
            name1 = fake.name()
            name2 = fake.name()
            email1 = fake.email()
            email2 = fake.email()
            email3 = fake.email()
            # phone1 =  f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # WhatsApp number (Bangladesh)
            # phone2 =  f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # Phone number (Bangladesh)
            # whatsapp =  f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # Phone number (Bangladesh)
            # phone1 = fake.phone_number()
            # phone2 = fake.phone_number()
            # whatsapp = fake.phone_number()
            wechat = fake.user_name()

            writer.writerow([
                fake.date_this_decade().strftime("%d/%m/%Y"),
                fake.company(),
                fake.company(),
                name1,
                choice(designations),
                choice(categories),
                choice(ranges),
                choice(specialities),
                fake.country(),
                email1,
                email2,
                email3,
                f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # WhatsApp number (Bangladesh)
                f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # Phone number (Bangladesh)
                f"+8801{randint(3,9)}{randint(10000000,99999999)}",  # Phone number (Bangladesh)
                wechat,
                choice(payment_terms),
                fake.bothify(text="Ref###"),
                fake.address().replace('\n', ', '),
                fake.address().replace('\n', ', '),
                fake.url(),
                choice(remarks_list),
                name2
            ])

        return response


# upload suppliers
class SupplierUploadView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_supplier"

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
class SupplierPreviewView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_supplier"

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

        # List all fields you want to check for duplicates
        fields_to_check = [
            "date", "mill_name", "supplier_name", "concern_person", "concern_person_designation", "product_category",
            "product_range", "speciality", "country_of_origin", "email_id1","email_id2","email_id3",  "phone_number1","phone_number2", "whatsapp_number",
            "wechat_id", "payment_term", "fabric_reference", "mailing_address",
            "visiting_address", "linkedin_profile", "remarks", "concern_fe_rep"
        ]

        # Build sets of existing values for each field
        existing_values = defaultdict(set)
        for field in fields_to_check:
            # Direct model fields
            if field in [f.name for f in Supplier._meta.get_fields() if not f.is_relation]:
                existing_values[field] = set(Supplier.objects.values_list(field, flat=True))
            
            # Related email field
            elif field == 'email_id1':
                existing_values[field] = set(
                    PersonEmail.objects.filter(contact_info_id__in=Supplier.objects.values('id')).values_list('email', flat=True)
                )
            # Related email field
            elif field == 'email_id2':
                existing_values[field] = set(
                    PersonEmail.objects.filter(contact_info_id__in=Supplier.objects.values('id')).values_list('email', flat=True)
                )
            # Related email field
            elif field == 'email_id3':
                existing_values[field] = set(
                    PersonEmail.objects.filter(contact_info_id__in=Supplier.objects.values('id')).values_list('email', flat=True)
                )

            elif field == 'phone_number1':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Supplier.objects.values_list('id', flat=True),
                        is_whatsapp=False
                    ).values_list('phone', flat=True)
                )
            elif field == 'phone_number2':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Supplier.objects.values_list('id', flat=True),
                        is_whatsapp=False
                    ).values_list('phone', flat=True)
                )

            elif field == 'whatsapp_number':
                existing_values[field] = set(
                    PersonPhone.objects.filter(
                        contact_info_id__in=Supplier.objects.values_list('id', flat=True),
                        is_whatsapp=True
                    ).values_list('phone', flat=True)
                )
            

        # Mark duplicates for each cell
        for row in preview_data:
            row['duplicates'] = {}

            for field in fields_to_check:
                value = row.get(field)

                if field == 'date':
                    value = datetime.strptime(value, "%d/%m/%Y").date()
                    row['duplicates'][field] = value in existing_values[field] if value else False
                else:
                    row['duplicates'][field] = value in existing_values[field] if value else False


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
                                date=datetime.strptime(row.get('date'), "%d/%m/%Y").date(),
                                mill_name=row.get('mill_name'),
                                supplier_name=row.get('supplier_name'),
                                concern_person=row.get('concern_person'),
                                concern_person_designation=row.get('concern_person_designation'),
                                product_category=row.get('product_category'),
                                product_range=row.get('product_range'),
                                speciality=row.get('speciality'),
                                country_of_origin=row.get('country_of_origin'),
                                # email 
                                # phone 
                                # whatsapp 
                                wechat_id=row.get('wechat_id'),
                                payment_term=row.get('payment_term'),
                                fabric_reference=row.get('fabric_reference'),
                                mailing_address=row.get('mailing_address'),
                                visiting_address=row.get('visiting_address'),
                                linkedin_profile=row.get('linkedin_profile'),
                                remarks=row.get('remarks'),
                                concern_fe_rep=row.get('concern_fe_rep'),
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
class SupplierListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "business_data.view_supplier"
    template_name = "business_data/manage_suppliers/supplier_list.html"


# data-table source for supplier list 
class SupplierDataSourceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_supplier"

    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get('draw',1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_col_index = request.GET.get('order[0][column]', 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')
       

        # sorting columns
        columns = [
            'id',
            'date',
            'mill_name',
            'supplier_name',
            'concern_person',
            'concern_person_designation',
            'product_category',
            'product_range',
            'speciality',
            'country_of_origin',
            'emails__email',
            'phones__phone',
            'phones__phone',
            'wechat_id',
            'payment_term',
            'fabric_reference',
            'mailing_address',
            'visiting_address',
            'linkedin_profile',
            'remarks',
            'concern_fe_rep',
        ]
        # Sorting
        # if order_col_index < 0 or order_col_index >= len(columns):
        #     order_col_index = 0
        order_column = columns[int(order_col_index)]
        if order_dir == 'asc':
            order_column = '-' + order_column


        # get supplier list 
        qs = Supplier.objects.all().prefetch_related('emails', 'phones')
        
        if search_value:
            search_q = Q()
            # List of fields to search (including id and all relevant fields)
            search_fields = [
                'id',
                'date',
                'mill_name',
                'supplier_name',
                'concern_person',
                'concern_person_designation',
                'product_category',
                'product_range',
                'speciality',
                'country_of_origin',
                'emails__email',
                'phones__phone',
                # 'personphone__is_whatsapp',
                'wechat_id',
                'payment_term',
                'fabric_reference',
                'mailing_address',
                'visiting_address',
                'linkedin_profile',
                'remarks',
                'concern_fe_rep',
            ]

            for col in search_fields:
                search_q |= Q(**{f"{col}__icontains": search_value})
            qs = qs.filter(search_q)

        total_count = Supplier.objects.count()
        filtered_count = qs.count()
        
        # Ordering and pagination
        qs = qs.order_by(order_column)[start:start + length]

        data = []
        for obj in qs:
            data.append({
                'id': obj.id,
                'date': obj.date,
                'mill_name': getattr(obj, 'mill_name', ''),
                'supplier_name': getattr(obj, 'supplier_name', ''),
                'concern_person': getattr(obj, 'concern_person', ''),
                'concern_person_designation': getattr(obj, 'concern_person_designation', ''),
                'product_category': getattr(obj, 'product_category', ''),
                'product_range': getattr(obj, 'product_range', ''),
                'speciality': getattr(obj, 'speciality', ''),
                'country_of_origin': getattr(obj, 'country_of_origin', ''),
                'emails': ', '.join([p.email for p in obj.emails.all()]),
                'phones': ', '.join([p.phone for p in obj.phones.all() if not p.is_whatsapp]),
                'whatsapp_numbers': ', '.join([p.phone for p in obj.phones.all() if p.is_whatsapp]),
                # 'emails': [p.email for p in obj.emails],
                # 'phones': [p.phone for p in obj.phones if not p.is_whatsapp],
                # 'whatsapp_numbers': [p.phone for p in obj.phones if p.is_whatsapp],
                'wechat_id': getattr(obj, 'wechat_id', ''),
                'payment_term': getattr(obj, 'payment_term', ''),
                'fabric_reference': getattr(obj, 'fabric_reference', ''),
                'mailing_address': getattr(obj, 'mailing_address', ''),
                'visiting_address': getattr(obj, 'visiting_address', ''),
                'linkedin_profile': getattr(obj, 'linkedin_profile', ''),
                'remarks': getattr(obj, 'remarks', ''),
                'concern_fe_rep': getattr(obj, 'concern_fe_rep', ''),
                'tag': getattr(obj, 'tag', ''),
                # Add custom row attributes:
                'DT_RowAttr': {
                    'data-id': obj.id,
                    # 'data-status': 'active' if obj.is_active else 'inactive',
                }
            })


        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data,
        })


# soft delete supplier 
class DeleteSupplierView(LoginRequiredMixin, PermissionRequiredMixin,UpdateView):
    permission_required = 'business_data.delete_supplier'
    model = Supplier
    fields= ['is_deleted']

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Supplier.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected suppliers deleted successfully.'})

"""End::Supplier Details"""

"""Begin::Product Details"""
# generate csv file of product details 
class GenerateCSVProduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_product"
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_product_details.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "date", "fabric_article_supplier", "fabric_article_fexpo", "fabric_mill_supplier", "rd_generated_date", "fabric_mill_source",
            "coo", "product_category", "mill_reference", "fabricexpo_reference","season","style",  "po","customer_name","composition",
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

        for _ in range(50):  # Change to any number you want
            writer.writerow([
                fake.date_this_decade().strftime("%d/%m/%Y"),
                fake.company(),
                fake.company(),
                fake.company(),
                fake.date_this_decade().strftime("%d/%m/%Y"),
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
class ProductUploadView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.add_product"
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
class ProductPreviewView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'business_data.add_product'
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

        # List all fields you want to check for duplicates
        fields_to_check = [
            "date", "fabric_article_supplier", "fabric_article_fexpo", "fabric_mill_supplier", "rd_generated_date", "fabric_mill_source",
            "coo", "product_category", "mill_reference", "fabricexpo_reference","season","style",  "po","customer_name","composition",
            "construction", "weight", "color", "cut_width",
            "wash", "price_per_yard", "shrinkage_percent", "stock_qty",
            "images", "barcode", "qr_code", "concern_person"
        ]

        # Build sets of existing values for each field
        existing_values = defaultdict(set)
        for field in fields_to_check:
            # Direct model fields
            if field in [f.name for f in Product._meta.get_fields() if not f.is_relation]:
                 
                existing_values[field] = set(Product.objects.values_list(field, flat=True))
            
            # # Related email field
            # elif field == 'email_id1':
            #     existing_values[field] = set(
            #         PersonEmail.objects.filter(contact_info_id__in=Product.objects.values('id')).values_list('email', flat=True)
            #     )
            # # Related email field
            # elif field == 'email_id2':
            #     existing_values[field] = set(
            #         PersonEmail.objects.filter(contact_info_id__in=Product.objects.values('id')).values_list('email', flat=True)
            #     )
            # # Related email field
            # elif field == 'email_id3':
            #     existing_values[field] = set(
            #         PersonEmail.objects.filter(contact_info_id__in=Product.objects.values('id')).values_list('email', flat=True)
            #     )

            # elif field == 'phone_number1':
            #     existing_values[field] = set(
            #         PersonPhone.objects.filter(
            #             contact_info_id__in=Product.objects.values_list('id', flat=True),
            #             is_whatsapp=False
            #         ).values_list('phone', flat=True)
            #     )
            # elif field == 'phone_number2':
            #     existing_values[field] = set(
            #         PersonPhone.objects.filter(
            #             contact_info_id__in=Product.objects.values_list('id', flat=True),
            #             is_whatsapp=False
            #         ).values_list('phone', flat=True)
            #     )

            # elif field == 'whatsapp_number':
            #     existing_values[field] = set(
            #         PersonPhone.objects.filter(
            #             contact_info_id__in=Product.objects.values_list('id', flat=True),
            #             is_whatsapp=True
            #         ).values_list('phone', flat=True)
            #     )


        # Mark duplicates for each cell
        for row in preview_data:
            row['duplicates'] = {}

            for field in fields_to_check:
                value = row.get(field)

                if field == 'date' or field == 'rd_generated_date':
                    value = datetime.strptime(value, "%d/%m/%Y").date()
                elif field == 'barcode':
                    value = str(value)
                elif field == 'price_per_yard' or field == 'shrinkage_percent':
                    value = round(Decimal(value), 2)
                
                row['duplicates'][field] = value in existing_values[field] if value else False

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
                                date=datetime.strptime(row.get('date'), "%d/%m/%Y").date(),
                                fabric_article_supplier=row.get('fabric_article_supplier', ''),
                                fabric_article_fexpo=row.get('fabric_article_fexpo', ''),
                                fabric_mill_supplier=row.get('fabric_mill_supplier', ''),
                                rd_generated_date=datetime.strptime(row.get('rd_generated_date', ''), "%d/%m/%Y").date(),
                                fabric_mill_source=row.get('fabric_mill_source', ''),
                                coo=row.get('coo', ''),
                                product_category=row.get('product_category', ''),
                                mill_reference=row.get('mill_reference', ''),
                                fabricexpo_reference=row.get('fabricexpo_reference', ''),
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
                                # barcode=row.get('barcode', ''),
                                # qr_code=row.get('qr_code', ''),
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
class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "business_data.view_product"
    # model = Product
    template_name = "business_data/manage_products/product_list.html"

# product list 
class ProductDataSourceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'business_data.view_product'
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

        order_field = columns[int(order_column_index)] if int(order_column_index) < len(columns) else 'id'
        if order_dir == 'asc':
            order_field = '-' + order_field



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
                # idx,  # For Count column (can be filled on client side)
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
                # '',  # images (handle as needed)
                # '',  # images (handle as needed)
                # '',  # images (handle as needed)
                # obj.barcode,
                # obj.qr_code,
                obj.concern_person,
                obj.get_absolute_url(), 
            ])
        print("Data:", data)
  

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data,
        })

# delete products 
class DeleteProductView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'business_data.delete_product'

    model = Product
    fields= ['is_deleted']

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selectedIds[]')
        if not ids:
            return JsonResponse({'error': 'No IDs provided.'}, status=400)
        Product.objects.filter(id__in=ids).soft_delete()
        return JsonResponse({'message': 'Selected products deleted successfully.'})
    

# public product detail view 
class PublicProductDetailView(DetailView):
    model = Product
    template_name = 'business_data/manage_products/public_product_detail.html'
    context_object_name = 'product'


# view product details 
class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "business_data.view_product"

    model = Product
    template_name = 'business_data/manage_products/product_detail.html'  # Customize the path if needed
    context_object_name = 'product'
    redirect_field_name = 'next'
    
    def get_login_url(self):
        return reverse_lazy('business_data:product-detail-sticker', kwargs={'pk': self.kwargs['pk']})


     
class ProductDetailViewSticker(DetailView):
    model = Product
    
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        template = 'business_data/manage_products/print_labels/details_label.html'
        
        context = {
            'product': product,
            # 'base_url': base_url
        }

        html_string = render_to_string(template, context)
        
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{product.fabric_article_fexpo}_label.pdf"'
        return response
     

class ProductDetailListPDFView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_product"


    def get(self, request, *args, **kwargs):
        product_ids = request.GET.getlist('ids[]')

        if not product_ids:
            return HttpResponse("No product IDs provided.", status=400)

        products = Product.objects.filter(id__in=product_ids)

        html_string = render_to_string('business_data/manage_products/print_labels/product_detail_sticker_list.html', {'products': products})

        pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="product_details_list.pdf"'
        # response = render(request,'business_data/manage_products/print_labels/product_detail_sticker_list.html', {'products': products})
        return response
 



# import tempfile
class ProductLabelPrintView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_product"
    def get(self, request, pk, label_type):
        product = Product.objects.get(pk=pk)
        
        # Render different templates based on label type
        if label_type == 'barcode':
            template = 'business_data/manage_products/print_labels/barcode_label.html'
        elif label_type == 'qrcode':
            template = 'business_data/manage_products/print_labels/qrcode_label.html'
        else:  # default to details
            template = 'business_data/manage_products/print_labels/details_label.html'
        

        # base_url = request.build_absolute_uri('/')[:-1]  # Gets domain without trailing slash
        context = {
            'product': product,
            # 'base_url': base_url
        }

        html_string = render_to_string(template, context)
        
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{product.fabric_article_fexpo}_{label_type}_label.pdf"'
        return response
    

# generate qrcode list 
class ProductQRCodePDFView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_product"

    def get(self, request, *args, **kwargs):
        product_ids = request.GET.getlist('ids[]')

        if not product_ids:
            return HttpResponse("No product IDs provided.", status=400)

        products = Product.objects.filter(id__in=product_ids).only('id', 'qr_code')

        # return render(request,'business_data/manage_products/print_labels/qr_code_list.html', {'products': products, 'is_qrcode':True})
        html_string = render_to_string('business_data/manage_products/print_labels/qr_code_list.html', {'products': products, 'is_qrcode':True})

        pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="product_qrcodes.pdf"'
        return response


# generate barcode list 
class ProductBarCodePDFView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "business_data.view_product"

    def get(self, request, *args, **kwargs):
        product_ids = request.GET.getlist('ids[]')

        if not product_ids:
            return HttpResponse("No product IDs provided.", status=400)

        # products = Product.objects.filter(id__in=product_ids)
        products = Product.objects.filter(id__in=product_ids).only('id','barcode')

        # return render(request,'business_data/manage_products/print_labels/qr_code_list.html', {'products': products, 'is_barcode':True})
        html_string = render_to_string('business_data/manage_products/print_labels/qr_code_list.html', {'products': products,'is_barcode':True})

        pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="product_barcodes.pdf"'
        return response

"""End::Product Details"""

