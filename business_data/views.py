from django.shortcuts import render, redirect
from django.views.generic import CreateView
from business_data.models import Buyer, Supplier, Customer, Product
import os
import pandas as pd
from django.conf import settings
from django.core.files.storage import default_storage
from django.views import View
from django.contrib import messages


from .forms import BuyerUploadForm
from random import randint

class BuyerUploadView(View):
    def get(self, request):
        form = BuyerUploadForm()
        return render(request, 'business_data/manage_buyers/upload.html', {'form': form})

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
            # print(data)
            request.session['preview_buyer_data'] = data
            return redirect('business_data:buyer-preview')

        return render(request, 'business_data/manage_buyers/upload.html', {'form': form})


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
                

                Buyer.objects.create(
                    date=row['date'],
                    company_name=row['company_name'],
                    organization_type=row['organization_type'],
                    brand=row['brand'],
                    department=row['department'],
                    buyer_name=row['buyer_name'],
                    designation=row['designation'],
                    country_of_origin=row['coo'],
                    # email=row['buyer_email_id'],  # foreign
                    # whatsapp_number=row['whatsapp_number'],  # foreign key
                    # phone=row['phone'],  # foreign
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
                messages.success(request, "Buyers have been successfully saved.")

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        request.session.pop('preview_data', None)
        request.session.pop('temp_file_path', None)

        return redirect('business_data:buyer-upload')
        # return redirect('business_data:upload-success')




class CreateBuyerView(CreateView):
    model = Buyer
    form_class = None
    template_name = "business_data/manage_buyers/add_buyers.html"