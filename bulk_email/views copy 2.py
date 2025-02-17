from django.utils import timezone
import uuid
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from bulk_core.models import RecipientDataSheet, RecipientCategory, TempRecipientDataSheet
from bulk_email.forms import EmailChangeForm, EmailCreationForm, TempEmailRecipientImportForm
from fabric_expo_management_system import settings
from .models import EmailRecipient, EmailTemplate, SentMail,TempEmailRecipient
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView,DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
import csv
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
# from bulk_email.tasks import process_csv_file

"""begin::import email """
class GenerateCSV(View):
    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_email_recipients.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(["name", "email",])
        writer.writerow(['John Doe','example@example.com', ])

        return response
        



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


# Delete Datasheet/Temporary Datasheet
class DataSheetDeleteView(View):
    def post(self, request, datasheet_id, *args, **kwargs):
        
        try:
            # Get datasheet
            datasheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)

            # Get recipient IDs from form data
            recipients_temp_id = request.POST.getlist('recipient_ids')

            # Delete selected recipients
            if recipients_temp_id:
                TempEmailRecipient.objects.filter(temp_id__in=recipients_temp_id).delete()


            # Delete datasheet
            datasheet.delete()

            return JsonResponse({'success': True, 'message': 'Datasheet deleted successfully'})
            # return redirect('bulk_email:import_recipients')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        


# email categories 
class EmailCategories(ListView):
    model = RecipientCategory
    template_name = 'bulk_email/category.html'


# Recipient list based on categories 
class EmailCategoriesRecipientList(ListView):
    model = EmailRecipient
    template_name = "bulk_email/recipient_list.html"
    context_object_name = "recipients"  # Name for template access

    def get_queryset(self):
        category_id = self.kwargs.get('pk')  # Assuming pk refers to category
        return EmailRecipient.objects.filter(category_id=category_id)
    
"""end::import email """

"""begin::writing email """
class CreateEmail(CreateView):
    template_name = "bulk_email/create_email.html" 
    form_class = EmailCreationForm 
    success_url = reverse_lazy('bulk_email:draft_list')


    def form_valid(self, form):
        form.instance.created_by = self.request.user 
        return super().form_valid(form)
    

class EmailDraftListView(ListView):
    model = EmailTemplate
    template_name = "bulk_email/email_draft.html"

    def get_queryset(self):
        return self.model.objects.filter(delete_status=False)  # Only active drafts

# Update email draft form 
class EmailChangeView(UpdateView):
    model = EmailTemplate
    template_name = "bulk_email/open_draft.html"
    form_class = EmailChangeForm
    success_url = reverse_lazy('bulk_email:draft_list')


# soft delete email draft  
class DeleteEmailDraftView(UpdateView):
    model = EmailTemplate
    fields = ['delete_status']
    success_url = reverse_lazy('bulk_email:draft_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete_status = True  # Mark as deleted
        self.object.save()
        messages.success(request, f"Draft '{self.object.name}' has been deleted.")  # Fixed message
       
        return redirect(self.success_url)
     
"""end::writing email"""
    

"""begin::sending email"""
class SelectRecipientsView(View):
    template_name = "bulk_email/recipient_list.html"

    def get(self, request, *args, **kwargs):
        email_content = get_object_or_404(EmailTemplate,id=kwargs.get('draft_id'))
        recipients = EmailRecipient.objects.all()
        return render(request, self.template_name, {
            'recipients': recipients,
            'email_content': email_content
        })


# class SendEmailView(View):
#     # template_name = 
#     def post(self,request,*args,**kwargs):
#         email_content = get_object_or_404(EmailTemplate,id=kwargs.get('draft_id'))
#         recipient_ids = request.POST.getlist('selectedRecipientIds[]')
#         recipients = EmailRecipient.objects.filter(id__in=recipient_ids)
#         session_id = str(uuid.uuid4())
#         sender = request.user


#         # Track success and failure
#         success_count = 0
#         failure_count = 0

#         for recipient in recipients:
#             try:
#                 # Create email message
#                 email = EmailMessage(
#                     subject=email_content.subject,
#                     body=email_content.body,
#                     from_email=settings.EMAIL_HOST_USER,  # Set your sender email
#                     to=[recipient.email],  # Send individually (no CC or BCC)
#                 )

#                 # Attach files
#                 # for attachment in attachments:
#                 #     email.attach_file(attachment.attachment.path)

#                 # Send email
#                 email.send()
#                 success_count += 1

#                 # Log successful email
#                 SentMail.objects.create(
#                     recipient_to=recipient,
#                     email=email_content,
#                     sent_by=sender,
#                     sent_at=timezone.now(),  # Set current time
#                     session_id=session_id,  # Generate unique ID
#                     status=True,
#                 )
#             except Exception as e:
#                 failure_count += 1

#                 # Log failed email
#                 SentMail.objects.create(
#                     email=email_content,
#                     recipient_to=recipient,
#                     sent_by=sender,
#                     sent_at=timezone.now(),  # Set current time
#                     session_id=session_id,  # Generate unique ID
#                     error_message=str(e),
#                     status=False,
#                 )

#         # Add success message
#         messages.success(request, f"{success_count} emails sent successfully, {failure_count} failed.")

#         return JsonResponse({"success_count": success_count, "failure_count": failure_count})
# 
### progress update function 
# from django.core.cache import cache
# def email_progress(request):
#     progress = cache.get("email_progress", 0)  # Retrieve progress from cache
#     return JsonResponse({"progress": progress})

import os
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.exceptions import ValidationError
class SendEmailView(View):
    def post(self,request,*args,**kwargs):
        email_content = get_object_or_404(EmailTemplate,id=kwargs.get('draft_id'))
        recipient_ids = request.POST.getlist('selectedRecipientIds[]')
        recipients = EmailRecipient.objects.filter(id__in=recipient_ids)
        session_id = str(uuid.uuid4())
        sender = request.user

        # Maximum allowed file size (5MB)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes


        # # List of attachments (file paths)
        # attachments = ["path/to/file1.pdf", "path/to/file2.jpg", "path/to/file3.docx"]

        # # Function to validate file size
        # def validate_attachment(file_path):
        #     if os.path.exists(file_path):
        #         file_size = os.path.getsize(file_path)  # Get file size in bytes
        #         if file_size > MAX_FILE_SIZE:
        #             raise ValidationError(f"File {file_path} exceeds the 5MB size limit.")
        #     else:
        #         raise ValidationError(f"File {file_path} does not exist.")

        # Open a single SMTP connection for efficiency
        connection = get_connection()
        connection.open()

        # Track success and failure
        success_count = 0
        failure_count = 0

        # process count
        # total_recipients = len(recipient_ids)
        # processed_count = 0

        # Loop through each recipient
        for recipient in recipients:
            # Plain text fallback
            text_body = f"""Dear {recipient.name}\n\n,

                            {email_content.body}\n\n

                            Best Regards,\n
                            Fabric Expo Management\n
                        """

            # HTML Email (Better Formatting)
            html_body = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                                <p>Dear {recipient.name},</p>
                                <p>{email_content.body}</p>
                                <p style="margin-top: 20px;">Best Regards,<br>
                                <strong>Fabric Expo Management</strong></p>
                            </body>
                            </html>
                        """

            # Create email
            email_message = EmailMultiAlternatives(
                subject=email_content.subject,
                body=text_body,  # Plain text version
                # from_email=settings.EMAIL_HOST_USER,
                from_email="admin@email.com",
                to=[recipient.email],
                connection=connection,  # Use open connection
            )
            
            # Attach HTML version for better formatting
            email_message.attach_alternative(html_body, "text/html")

            # Attach multiple files with validation
            # for file in attachments:
            #     try:
            #         validate_attachment(file)  # Validate file size
            #         with open(file, "rb") as f:
            #             email_message.attach(os.path.basename(file), f.read())  # Attach file
            #     except ValidationError as e:
            #         print(f"Skipping {file}: {e}")  # Log validation error and continue

            # Send the email
            try:
                email_message.send()
                success_count += 1

                # Log successful email
                SentMail.objects.create(
                    recipient_to=recipient,
                    email=email_content,
                    sent_by=sender,
                    sent_at=timezone.now(),  # Set current time
                    session_id=session_id,  # Generate unique ID
                    status=True,
                )
            except Exception as e:
                # Log failed email
                failure_count += 1
                SentMail.objects.create(
                    email=email_content,
                    recipient_to=recipient,
                    sent_by=sender,
                    sent_at=timezone.now(),  # Set current time
                    session_id=session_id,  # Generate unique ID
                    error_message=str(e),
                    status=False,
                )
            
            # Simulate delay & update progress
            # processed_count += 1
            # progress = (processed_count / total_recipients) * 100
            # cache.set("email_progress", progress, timeout=60)

            time.sleep(1)  # Simulate processing time

        # Close the connection after all emails are sent
        connection.close()

        # cache.set("email_progress", 100, timeout=60)  # Ensure 100% completion
        # Add success message
        # messages.success(request, f"{success_count} emails sent successfully, {failure_count} failed.")
        return JsonResponse({"success_count": success_count, "failure_count": failure_count,'message':f"Email has been sent with {success_count} success and {failure_count} failed attempts."})
        
"""end::sending email"""
