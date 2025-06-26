import pprint
from django.utils import timezone
import uuid

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse

from django.db.models import F
from django.db import transaction
from django.contrib import messages
import csv

# import views 
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from django.utils.decorators import method_decorator
from django_twilio.decorators import twilio_view
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.utils import timezone

# validators 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from phonenumber_field.validators import validate_international_phonenumber
from bulk_whatsapp.tasks import send_whatsapp_message

# models 
from bulk_core.models import RecipientCategory, RecipientDataSheet, TempRecipientDataSheet
from bulk_whatsapp.models import SentMessage, TempRecipient, WhatsappAttachment, WhatsappRecipient, WhatsappSession, WhatsappTemplate
from django.db.models import F

# forms
from bulk_whatsapp.forms import  MessageDraftUpdateForm, TempRecipientImportForm, MessageCreationForm


"""begin:: Utility functions """
# Utility Function to normalize phone numbers to E.164 format (without default region)
import phonenumbers
def normalize_phone_number(number):
    try:
        parsed_number = phonenumbers.parse(number, None)  # Parse without region
        if not phonenumbers.is_valid_number(parsed_number):  # Check if valid
            return None
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)  # Convert to E.164
    except phonenumbers.NumberParseException:
        return None  # Return None if invalid
    
"""end:: Utility functions """


"""begin::manage recipients """
### Generate demo csv for whatsapp
class GenerateCSV(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.add_whatsapprecipient"
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_whatsapp_recipients.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(["name", "whatsapp_no",])
        writer.writerow(['John Doe','+8801777777254', ])
        writer.writerow(['John Doe2','+8801777777354', ])

        return response
        


### import whatsapp recipient from csv file view 
class RecipientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "bulk_whatsapp.add_whatsapprecipient"

    model = TempRecipientDataSheet
    template_name = "bulk_whatsapp/import_recipients.html"
    form_class= TempRecipientImportForm

    def get_success_url(self):
        return reverse('bulk_whatsapp:preview_recipients', kwargs={'datasheet_id': self.object.pk})


### preview recipients list view 
class PreviewRecipientsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.add_whatsapprecipient"
    template_name = "bulk_whatsapp/preview_recipients.html"

    def get(self, request, datasheet_id):
        # Get the uploaded file
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
            if len(row) < 2 or not row[0].strip() or not row[1].strip():  
                continue  # Skip invalid rows
            name, whatsapp_no = row[0].strip(), row[1].strip()

            # check if the number is valid
            try:
                validate_international_phonenumber(whatsapp_no) 
            except ValidationError:
                continue

            # Add valid data into new array
            temp_recipients.append(TempRecipient(
                name=name, 
                recipient_id=whatsapp_no, 
                category=data_sheet.category, 
                temp_id=uuid.uuid4()
            ))

        # store valid data into temporary data table 
        temporary_recipients = TempRecipient.objects.bulk_create(temp_recipients)
        # retrieve unique ids from temporary data 
        recipient_ids = [str(item.temp_id) for item in temporary_recipients]

        return render(request, self.template_name, {
            'recipients': temporary_recipients,
            'data_sheet': data_sheet,
            'recipient_ids': recipient_ids,
        })


### Move data from temporary data table to permanent table 
class ConfirmWhatsappRecipientsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.add_whatsapprecipient"
    
    @transaction.atomic
    def post(self, request, datasheet_id):
        temp_data_sheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)
        temp_ids = request.POST.getlist('recipient_ids[]')
        # print(temp_ids)

        # check if exist temporary data 
        if not temp_ids:
            messages.error(request, 'No recipients selected for confirmation.')
            return redirect('bulk_whatsapp:preview_recipients', datasheet_id=datasheet_id)

        # retrieve temporary data and check if objects are not empty 
        temp_recipients = list(TempRecipient.objects.filter(temp_id__in=temp_ids))
        if not temp_recipients:
            messages.error(request, 'No valid recipients found.')
            return redirect('bulk_whatsapp:preview_recipients', datasheet_id=datasheet_id)

        
        # Normalize phone numbers and filter out None values
        normalized_numbers = [normalize_phone_number(tr.recipient_id) for tr in temp_recipients]
        normalized_numbers = [num for num in normalized_numbers if num is not None]
        print(normalized_numbers)
        # array of all duplicate recipients 
        existing_recipients = {
            recipient.recipient_number: recipient for recipient in WhatsappRecipient.objects.filter(
                recipient_number__in=normalized_numbers
            )
        }

        # create new list for new recipients and update existed recipients if need any
        new_recipients = []
        update_recipients = []

        for tr in temp_recipients:
            # check if exist but update category 
            if normalize_phone_number(tr.recipient_id) in existing_recipients:
                existing_recipient = existing_recipients[normalize_phone_number(tr.recipient_id)]
                if existing_recipient.category != tr.category:
                    existing_recipient.category = tr.category  # Update category
                    update_recipients.append(existing_recipient)
            else:
                # create new recipient's list 
                new_recipients.append(WhatsappRecipient(
                    name=tr.name,
                    recipient_number=tr.recipient_id,
                    category=tr.category
                ))

        # Perform bulk operations
        if new_recipients:
            WhatsappRecipient.objects.bulk_create(new_recipients)  # Insert new records
        if update_recipients:
            WhatsappRecipient.objects.bulk_update(update_recipients, ['category'])  # Update category for existing recipients

        # Save the csv file in permanent storage
        RecipientDataSheet.objects.create(
            data_sheet=temp_data_sheet.data_sheet,
            description=temp_data_sheet.description,
            uploaded_at=temp_data_sheet.uploaded_at,
            category=temp_data_sheet.category
        )

        # Delete temporary data
        TempRecipient.objects.filter(temp_id__in=temp_ids).delete()
        temp_data_sheet.delete()

        messages.success(request, 'Whatsapp recipients confirmed and saved successfully!')
        return JsonResponse({'success': True, 'message': 'Whatsapp recipients confirmed and saved successfully!'},status=200)
    
    

### Delete Datasheet/Temporary csv file
class DataSheetDeleteView(View):
    def post(self, request, datasheet_id, *args, **kwargs):
        
        try:
            # Get the temporary datasheet
            datasheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)

            # Get recipient IDs from form data
            recipients_temp_id = request.POST.getlist('recipient_ids[]')

            # Delete selected recipients
            if recipients_temp_id:
                TempRecipient.objects.filter(temp_id__in=recipients_temp_id).delete()


            # Delete datasheet
            datasheet.delete()

            return JsonResponse({'success': True, 'message': 'Datasheet deleted successfully'},status=200)
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

### Recipient list view 
class RecipientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "bulk_whatsapp.view_whatsapprecipient"
    model = WhatsappRecipient
    template_name = "bulk_core/manage_recipient/recipient_list.html"
    context_object_name = 'recipient_list' 

    def get_queryset(self):
        # Query the data and rename the column
        queryset = super().get_queryset().annotate(
            recipient_id=F('recipient_number')  # Rename the 'email' column to 'recipient_email'
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['source'] = 'bulk_whatsapp'
        context['source_title'] = 'whatsapp'
        return context


### Export recipient list view 
class ExportRecipientToCSVView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.view_whatsapprecipient"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="whatsapp_recipients.csv"'},
        )

        recipients = WhatsappRecipient.objects.all()

        writer = csv.writer(response)
        writer.writerow(["name", "whatsapp_no","category","id"])
        for item in recipients:
            writer.writerow([item.name,item.recipient_number,item.category,item.pk, ])

        return response

    
"""end::manage recipients """


"""begin::Mange messages"""
### WA create message 
class CreateMessageView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "bulk_whatsapp.add_whatsapptemplate"

    template_name = "bulk_whatsapp/manage_messages/create_message.html"
    form_class = MessageCreationForm
    success_url = reverse_lazy('bulk_whatsapp:draft_list')

    

    def form_valid(self, form):
        # Save the email template instance
        wa_template = form.save(commit=False)
        wa_template.created_by = self.request.user
        wa_template.save()
        
        # Handle file attachments
        for file in self.request.FILES.getlist('attachment'):
            WhatsappAttachment.objects.create(attachment=file,template=wa_template)

        
        messages.success(self.request, f'Whatsapp message draft "{form.instance.name}" has been created successfully!')
        return super().form_valid(form)
    


### WA draft view 
class DraftView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "bulk_whatsapp.view_whatsapptemplate"

    template_name = "bulk_whatsapp/manage_messages/draft_list.html" 
    model = WhatsappTemplate

    def handle_no_permission(self):
        # Redirect to a custom page if permission is denied
        return redirect('bulk_whatsapp:create_message')

    
    def get_queryset(self):
        return self.model.objects.filter(delete_status=False)  # Only active drafts


### add attachment 
class AddAttachmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        draft_id = kwargs.get('draft_id')
        wa_template = get_object_or_404(WhatsappTemplate, id=draft_id)

        # Calculate total size of existing attachments
        existing_attachments = WhatsappAttachment.objects.filter(template=wa_template)
        existing_size_mb = sum(item.attachment.size for item in existing_attachments) / (1024 * 1024)

        # Calculate total size of new files
        new_files = request.FILES.getlist('attachment')
        new_files_size_mb = sum(file.size for file in new_files) / (1024 * 1024)
        total_size_mb = existing_size_mb + new_files_size_mb

        # Ensure the total size does not exceed the 20MB limit
        if total_size_mb > 20:
            response = JsonResponse({'success': False, 'error': 'Total file size exceeds the 20MB limit.'}, status=400)
            return response
        else:
            try:
                # Handle file attachments
                if new_files:
                    for file in new_files:
                        WhatsappAttachment.objects.create(attachment=file, template=wa_template)

                return JsonResponse({'success': True, 'message': 'Attachments added successfully'}, status=200)

            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)

### remove attachment 
class RemoveAttachmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        attachment_id = self.request.POST.get('id')
        attachment = get_object_or_404(WhatsappAttachment, id=attachment_id)

        try:
            attachment.delete()
            return JsonResponse({'success': True, 'message': 'Attachment deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        


### WA draft delete view 
class DraftDeleteView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "bulk_whatsapp.delete_whatsapptemplate"

    model = WhatsappTemplate
    fields = ['delete_status']
    success_url = reverse_lazy('bulk_whatsapp:draft_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete_status = True  # Mark as deleted
        self.object.save()
        messages.success(request, f"Draft '{self.object.name}' has been deleted.")  # Fixed message
       
        return redirect(self.success_url)
     


## WA template update view 
class DraftUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "bulk_whatsapp.change_whatsapptemplate"
    template_name = "bulk_whatsapp/manage_messages/open_draft.html"
    model = WhatsappTemplate
    form_class = MessageDraftUpdateForm
    success_url = reverse_lazy('bulk_email:draft_list')


    
    def form_valid(self, form):
        response = super().form_valid(form)  # Correct method call

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Draft Updated'},status=200)

        return response  # Return normal response for non-AJAX requests
    
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        return super().form_invalid(form)

### select recipients to send message 
class SelectRecipientsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.sendmessage_whatsapptemplate"
    template_name = "bulk_whatsapp/manage_messages/recipient_list.html"

    def get(self, request, *args, **kwargs):
        whatsapp_content = get_object_or_404(WhatsappTemplate,id=kwargs.get('draft_id'))
        recipients = WhatsappRecipient.objects.all()
        recipients_category = RecipientCategory.objects.all()

        return render(request, self.template_name, {
            'recipients': recipients,
            'message_content': whatsapp_content,
            'recipients_category': recipients_category,
        })
    

class SendMessageView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.sendmessage_whatsapptemplate"

    def post(self,request,*args,**kwargs):
        # whatsapp_content = get_object_or_404(WhatsappTemplate,id=kwargs.get('draft_id'))
        # recipients = WhatsappRecipient.objects.filter(id__in=recipient_ids)
        recipient_category_ids = request.POST.getlist('selectedRecipientsCategoriesId[]')
        company_id = request.POST.get('selectedCompanyId')
        session_id = str(uuid.uuid4())
        user_id = request.user.pk
        draft_id=kwargs.get('draft_id')

        WhatsappSession.objects.create(
            session_id=session_id,
            sender_id=user_id,
            draft_id=draft_id,
            status='processing'
        )
        
        send_whatsapp_message.delay(
            user_id= user_id,
            draft_id=draft_id,
            recipient_category_ids = recipient_category_ids,
            session_id = session_id,
            company_id = company_id,
        )
        
        # Add success message
        # return JsonResponse({"success_count": success_count, "failure_count": failure_count,'message':f"Message has been sent with {success_count} success and {failure_count} failed attempts."})
        return JsonResponse({'message': "Messages sending are processing. Check queued message status."})


class SendMessageQueueListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "bulk_whatsapp.view_whatsappsession"
    template_name = "bulk_whatsapp/manage_messages/message_queue.html"


class SendMessageQueueAjaxListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "bulk_whatsapp.view_whatsappsession"
    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_column_index = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', 'asc')  # safer default


        columns = [
            'id', 'session_id', 'created_at', 'draft__name', 'success_count', 'failure_count', 'status'
        ]

        order_field = columns[int(order_column_index)] if int(order_column_index) < len(columns) else 'id'
        if order_dir == 'asc':
            order_field = '-' + order_field



        qs = WhatsappSession.objects.all()

        if search_value:
            search_q = Q()
            # List of fields to search (including id and all relevant fields)
            search_fields = columns
            for col in search_fields:
                search_q |= Q(**{f"{col}__icontains": search_value})
            qs = qs.filter(search_q)

        total_count = WhatsappSession.objects.count()
        filtered_count = qs.count()

        qs = qs.order_by(order_field)[start:start+length]

        data = []
        for obj in qs:
            # Convert UTC time to local time for display
            local_created_at = timezone.localtime(obj.created_at)
            data.append({
                'id': obj.id,
                'session_id': obj.session_id,
                'created_at': local_created_at.strftime('%Y-%m-%d %H:%M'),
                'subject': obj.draft.name,
                'success': obj.success_count,
                'failed': obj.failure_count,
                'status': obj.get_status_display(),
            })

  

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data,
        })



"""end::manage messages """
class SenTMessageSessionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "bulk_whatsapp.view_sentmessage"
    model = SentMessage
    template_name = "bulk_whatsapp/manage_messages/sent_message_session_list.html"

    def get_queryset(self):
        return super().get_queryset().order_by('-id')
