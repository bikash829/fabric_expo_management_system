from django.utils import timezone
import uuid
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse

from django.db import transaction
from django.contrib import messages


from fabric_expo_management_system import settings
# from .models import EmailRecipient, EmailTemplate, SentMail,TempEmailRecipient
# import views 
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView,DetailView

import csv
# validators 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from phonenumber_field.validators import validate_international_phonenumber

from django.core.mail import EmailMessage
# models 
from bulk_core.models import RecipientDataSheet, RecipientCategory, TempRecipientDataSheet
from bulk_whatsapp.models import TempRecipient, WhatsappRecipient

# forms
from bulk_whatsapp.forms import  TempRecipientImportForm


"""begin::import recipients """
class GenerateCSV(View):
    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_whatsapp_recipients.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(["name", "whatsapp_no",])
        writer.writerow(['John Doe','+8801777777254', ])
        writer.writerow(['John Doe2','01777777254', ])

        return response
        



class RecipientCreateView(CreateView):
    model = TempRecipientDataSheet
    template_name = "bulk_whatsapp/import_recipients.html"
    form_class= TempRecipientImportForm

    def get_success_url(self):
        return reverse('bulk_whatsapp:preview_recipients', kwargs={'datasheet_id': self.object.pk})


class PreviewRecipientsView(View):
    template_name = "bulk_whatsapp/preview_recipients.html"

    def get(self, request, datasheet_id):
        # Get the uploaded file
        # data_sheet = TempRecipientDataSheet.objects.get(id=datasheet_id)
        data_sheet = get_object_or_404(TempRecipientDataSheet,id=datasheet_id)

        # Read CSV and store in TempRecipient
        temp_recipients = []
        csv_file = data_sheet.data_sheet
        csv_file.open()
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        csv_file.close()  

        reader = csv.reader(decoded_file)
        next(reader,None)  # Skip header row

        # checking valid data 
        for row in reader:
            if len(row) < 2 or not row[0].strip() or not row[1].strip():  # Check for missing fields
                continue  # Skip invalid rows
            name, whatsapp_no = row[0].strip(), row[1].strip()

            # check if the mail is valid
            try:
                validate_international_phonenumber(whatsapp_no) 
            except ValidationError:
                continue


            temp_recipients.append(TempRecipient(
                name=name, 
                recipient_id=whatsapp_no, 
                category=data_sheet.category, 
                temp_id=uuid.uuid4()
            ))


        temporary_recipients = TempRecipient.objects.bulk_create(temp_recipients)

        recipient_ids = [str(item.temp_id) for item in temporary_recipients]

        return render(request, self.template_name, {
            'recipients': temporary_recipients,
            'data_sheet': data_sheet,
            'recipient_ids': recipient_ids,
        })


class ConfirmEmailRecipientsView(View):
    @transaction.atomic
    def post(self, request, datasheet_id):
        temp_data_sheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)
        temp_ids = request.POST.getlist('recipient_ids')

        if not temp_ids:
            messages.error(request, 'No recipients selected for confirmation.')
            return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

        temp_recipients = list(TempRecipient.objects.filter(temp_id__in=temp_ids))

        if not temp_recipients:
            messages.error(request, 'No valid recipients found.')
            return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

        existing_emails = {
            recipient.email: recipient for recipient in WhatsappRecipient.objects.filter(
                email__in=[tr.email for tr in temp_recipients]
            )
        }

        new_recipients = []
        update_recipients = []

        for tr in temp_recipients:
            if tr.email in existing_emails:
                existing_recipient = existing_emails[tr.email]
                if existing_recipient.category != tr.category:
                    existing_recipient.category = tr.category  # Update category
                    update_recipients.append(existing_recipient)
            else:
                new_recipients.append(WhatsappRecipient(
                    name=tr.name,
                    email=tr.email,
                    category=tr.category
                ))

        # Perform bulk operations
        if new_recipients:
            WhatsappRecipient.objects.bulk_create(new_recipients)  # Insert new records
        if update_recipients:
            WhatsappRecipient.objects.bulk_update(update_recipients, ['category'])  # Update category for existing emails

        # Save the datasheet in permanent storage
        RecipientDataSheet.objects.create(
            data_sheet=temp_data_sheet.data_sheet,
            description=temp_data_sheet.description,
            uploaded_at=temp_data_sheet.uploaded_at,
            category=temp_data_sheet.category
        )

        # Delete temporary data
        TempRecipient.objects.filter(temp_id__in=temp_ids).delete()
        temp_data_sheet.delete()

        messages.success(request, 'Email recipients confirmed and saved successfully!')
        return redirect('bulk_email:import_recipients')


# Delete Datasheet/Temporary Datasheet
class DataSheetDeleteView(View):
    def post(self, request, datasheet_id, *args, **kwargs):
        
        try:
            # Get datasheet
            datasheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)

            # Get recipient IDs from form data
            recipients_temp_id = request.POST.getlist('recipient_ids[]')

            # Delete selected recipients
            if recipients_temp_id:
                TempRecipient.objects.filter(temp_id__in=recipients_temp_id).delete()


            # Delete datasheet
            datasheet.delete()

            return JsonResponse({'success': True, 'message': 'Datasheet deleted successfully'})
            # return redirect('bulk_email:import_recipients')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        


# email categories 
# class EmailCategories(ListView):
#     model = RecipientCategory
#     template_name = 'bulk_email/category.html'


# # Recipient list based on categories 
# class EmailCategoriesRecipientList(ListView):
#     model = EmailRecipient
#     template_name = "bulk_email/recipient_list.html"
#     context_object_name = "recipients"  # Name for template access

#     def get_queryset(self):
#         category_id = self.kwargs.get('pk')  # Assuming pk refers to category
#         return EmailRecipient.objects.filter(category_id=category_id)
    
"""end::import email """