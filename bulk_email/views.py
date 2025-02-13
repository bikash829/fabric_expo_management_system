import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from bulk_core.models import RecipientDataSheet, RecipientCategory, TempRecipientDataSheet
from bulk_email.forms import TempEmailRecipientImportForm
from .models import EmailRecipient,TempEmailRecipient
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView,DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
import csv
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

# from bulk_email.tasks import process_csv_file

class EmailRecipientCreateView(CreateView):
    model = TempRecipientDataSheet
    template_name = "bulk_email/import_recipients.html"
    form_class= TempEmailRecipientImportForm

    def get_success_url(self):
        return reverse('bulk_email:preview_recipients', kwargs={'datasheet_id': self.object.pk})


class PreviewEmailRecipientsView(View):
    template_name = "bulk_email/preview_recipients.html"

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
            name, email = row[0].strip(), row[1].strip()

            # check if the mail is valid
            try:
                validate_email(email) 
            except ValidationError:
                continue

            temp_recipients.append(TempEmailRecipient(
                name=name, 
                email=email, 
                category=data_sheet.category, 
                temp_id=uuid.uuid4()
            ))

        temporary_recipients = TempEmailRecipient.objects.bulk_create(temp_recipients)

        return render(request, self.template_name, {
            'recipients': temporary_recipients,
            'data_sheet': data_sheet
        })
    

from django.db import transaction
"""without checking duplicate errors"""
# class ConfirmEmailRecipientsView(View):
#     @transaction.atomic
#     def post(self, request,datasheet_id):
#         # temp_data_sheet = TempRecipientDataSheet.objects.get(id=datasheet_id)
#         temp_data_sheet = get_object_or_404(TempRecipientDataSheet,id=datasheet_id)
#         temp_ids = request.POST.getlist('recipient_ids')

#         # check if temp id is not empty
#         if not temp_ids:
#             messages.error(request, 'No recipients selected for confirmation.')
#             return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

#         temp_recipients = TempEmailRecipient.objects.filter(temp_id__in=temp_ids)
#         # check if there is no valid email 
#         if not temp_recipients:
#             messages.error(request, 'No valid recipients found.')
#             return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

       
#         # create recipients 
#         create_recipients = [
#             EmailRecipient(name=temp_recipient.name, email=temp_recipient.email, category=temp_recipient.category)
#             for temp_recipient in temp_recipients
#         ]
#         # save email to main table
#         EmailRecipient.objects.bulk_create(create_recipients)

#         # Create datasheet and email recipients in one atomic transaction
#         RecipientDataSheet.objects.create(
#             data_sheet=temp_data_sheet.data_sheet,
#             description=temp_data_sheet.description,
#             uploaded_at=temp_data_sheet.uploaded_at,
#             category=temp_data_sheet.category
#         )


#         # Delete temporary data only if everything above succeeds
#         temp_recipients.delete()
#         temp_data_sheet.delete()

#         messages.success(request, 'Email recipients confirmed and saved successfully!')
#         return redirect('bulk_email:import_recipients')
"""end duplicate error """


class ConfirmEmailRecipientsView(View):
    @transaction.atomic
    def post(self, request, datasheet_id):
        temp_data_sheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)
        temp_ids = request.POST.getlist('recipient_ids')

        if not temp_ids:
            messages.error(request, 'No recipients selected for confirmation.')
            return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

        temp_recipients = list(TempEmailRecipient.objects.filter(temp_id__in=temp_ids))

        if not temp_recipients:
            messages.error(request, 'No valid recipients found.')
            return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

        existing_emails = {
            recipient.email: recipient for recipient in EmailRecipient.objects.filter(
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
                new_recipients.append(EmailRecipient(
                    name=tr.name,
                    email=tr.email,
                    category=tr.category
                ))

        # Perform bulk operations
        if new_recipients:
            EmailRecipient.objects.bulk_create(new_recipients)  # Insert new records
        if update_recipients:
            EmailRecipient.objects.bulk_update(update_recipients, ['category'])  # Update category for existing emails

        # Save the datasheet in permanent storage
        RecipientDataSheet.objects.create(
            data_sheet=temp_data_sheet.data_sheet,
            description=temp_data_sheet.description,
            uploaded_at=temp_data_sheet.uploaded_at,
            category=temp_data_sheet.category
        )

        # Delete temporary data
        TempEmailRecipient.objects.filter(temp_id__in=temp_ids).delete()
        temp_data_sheet.delete()

        messages.success(request, 'Email recipients confirmed and saved successfully!')
        return redirect('bulk_email:import_recipients')



# class DataSheetDeleteView(DeleteView):
#     model = TempRecipientDataSheet
#     success_url = reverse_lazy("bulk_email:import_recipients")

class DataSheetDeleteView(View):
    print("here you are")
    def post(self, request, datasheet_id, *args, **kwargs):
        
        try:
            # Get datasheet
            datasheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)

            # Get recipient IDs from form data
            recipients_temp_id = request.POST.getlist('recipient_ids')

            print(f"entered {recipients_temp_id}")
            # Delete selected recipients
            if recipients_temp_id:
                TempEmailRecipient.objects.filter(temp_id__in=recipients_temp_id).delete()


            # Delete datasheet
            datasheet.delete()

            return JsonResponse({'success': True, 'message': 'Datasheet deleted successfully'})
            # return redirect('bulk_email:import_recipients')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)