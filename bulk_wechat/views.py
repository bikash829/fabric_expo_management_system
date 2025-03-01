from django.utils import timezone
import uuid
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse

from django.db import transaction
from django.contrib import messages
import csv
from django.db.models import F

from bulk_wechat.forms import MessageCreationForm, TempRecipientImportForm
from bulk_wechat.models import TempWCRecipient, WeChatAttachment, WeChatRecipient, WeChatTemplate
from bulk_whatsapp.models import WhatsappTemplate
from fabric_expo_management_system import settings
# import views 
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView,DetailView


# validators 
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

# models 
from bulk_core.models import RecipientDataSheet, RecipientCategory, TempRecipientDataSheet
# from bulk_whatsapp.models import SentMessage, TempRecipient, WhatsappRecipient, WhatsappTemplate

# forms
# from bulk_whatsapp.forms import  MessageDraftUpdateForm, TempRecipientImportForm, MessageCreationForm



# Create your views here.
"""begin::manage recipients """
### Generate demo csv for whatsapp
class GenerateCSV(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_wechat_recipients.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(["name", "WeChat id",])
        writer.writerow(['John Doe','alicejohnson789', ])
        writer.writerow(['John Doe2','bobbrown321', ])

        return response
        


### import whatsapp recipient from csv file view 
class RecipientCreateView(CreateView):
    model = TempRecipientDataSheet
    template_name = "bulk_wechat/import_recipients.html"
    form_class= TempRecipientImportForm

    def get_success_url(self):
        return reverse('bulk_wechat:preview_recipients', kwargs={'datasheet_id': self.object.pk})


class PreviewRecipientsView(View):
    template_name = "bulk_wechat/preview_recipients.html"

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
            name, wechat_id = row[0].strip(), row[1].strip()

            # # check if the number is valid
            # try:
            #     validate_international_phonenumber(whatsapp_no) 
            # except ValidationError:
            #     continue

            # Add valid data into new array
            temp_recipients.append(TempWCRecipient(
                name=name, 
                recipient_id=wechat_id, 
                category=data_sheet.category, 
                temp_id=uuid.uuid4()
            ))

        # store valid data into temporary data table 
        temporary_recipients = TempWCRecipient.objects.bulk_create(temp_recipients)
        # retrieve unique ids from temporary data 
        recipient_ids = [str(item.temp_id) for item in temporary_recipients]

        return render(request, self.template_name, {
            'recipients': temporary_recipients,
            'data_sheet': data_sheet,
            'recipient_ids': recipient_ids,
        })




### Move data from temporary data table to permanent table 
class ConfirmWeChatRecipientsView(View):
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
        temp_recipients = list(TempWCRecipient.objects.filter(temp_id__in=temp_ids))
        if not temp_recipients:
            messages.error(request, 'No valid recipients found.')
            return redirect('bulk_whatsapp:preview_recipients', datasheet_id=datasheet_id)

        
        # Normalize phone numbers and filter out None values
        normalized_wc_ids = [tr.recipient_id for tr in temp_recipients]
        # normalized_numbers = [num for num in normalized_numbers if num is not None]
        # print(normalized_numbers)
        # array of all duplicate recipients 
        existing_recipients = {
            recipient.recipient_id: recipient for recipient in WeChatRecipient.objects.filter(
                recipient_id__in=normalized_wc_ids
            )
        }

        # create new list for new recipients and update existed recipients if need any
        new_recipients = []
        update_recipients = []
        print(new_recipients)
        print(update_recipients)

        for tr in temp_recipients:
            # check if exist but update category 
            if tr.recipient_id in existing_recipients:
                existing_recipient = existing_recipients[tr.recipient_id]
                if existing_recipient.category != tr.category:
                    existing_recipient.category = tr.category  # Update category
                    update_recipients.append(existing_recipient)
            else:
                # create new recipient's list 
                new_recipients.append(WeChatRecipient(
                    name=tr.name,
                    recipient_id=tr.recipient_id,
                    category=tr.category
                ))

        # Perform bulk operations
        if new_recipients:
            WeChatRecipient.objects.bulk_create(new_recipients)  # Insert new records
        if update_recipients:
            WeChatRecipient.objects.bulk_update(update_recipients, ['category'])  # Update category for existing recipients

        # Save the csv file in permanent storage
        RecipientDataSheet.objects.create(
            data_sheet=temp_data_sheet.data_sheet,
            description=temp_data_sheet.description,
            uploaded_at=temp_data_sheet.uploaded_at,
            category=temp_data_sheet.category
        )

        # Delete temporary data
        TempWCRecipient.objects.filter(temp_id__in=temp_ids).delete()
        temp_data_sheet.delete()

        messages.success(request, 'WeChat recipients confirmed and saved successfully!')
        return JsonResponse({'success': True, 'message': 'WeChat recipients confirmed and saved successfully!'},status=200)
    
    

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
                TempWCRecipient.objects.filter(temp_id__in=recipients_temp_id).delete()


            # Delete datasheet
            datasheet.delete()

            return JsonResponse({'success': True, 'message': 'Datasheet deleted successfully'},status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        

### Recipient list view 
class RecipientListView(ListView):
    model = WeChatRecipient
    template_name = "bulk_core/manage_recipient/recipient_list.html"
    context_object_name = 'recipient_list' 

    # def get_queryset(self):
    #     # Query the data and rename the column
    #     queryset = super().get_queryset().annotate(
    #         recipient_id=F('recipient_id')  # Rename the 'email' column to 'recipient_email'
    #     )
    #     return queryset
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['source'] = 'bulk_wechat'
        context['source_title'] = 'wechat'
        return context


### Export recipient list view 
class ExportRecipientToCSVView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="wechat_recipients.csv"'},
        )

        recipients = WeChatRecipient.objects.all()

        writer = csv.writer(response)
        writer.writerow(["name", "wechat_id","category","id"])
        for item in recipients:
            writer.writerow([item.name,item.recipient_id,item.category,item.pk, ])

        return response

    
"""end::manage recipients """


"""begin::Mange messages"""
### WA create message 
class CreateMessageView(CreateView):
    template_name = "bulk_wechat/manage_messages/create_message.html"
    form_class = MessageCreationForm
    success_url = reverse_lazy('bulk_wechat:draft_list')

    

    def form_valid(self, form):
        # Save the email template instance
        wc_template = form.save(commit=False)
        wc_template.created_by = self.request.user
        wc_template.save()
        
        # Handle file attachments
        for file in self.request.FILES.getlist('attachment'):
            WeChatAttachment.objects.create(attachment=file,template=wc_template)

        
        messages.success(self.request, f'WeChat message draft "{form.instance.name}" has been created successfully!')
        return super().form_valid(form)
    


### WA draft view 
class DraftView(ListView):
    template_name = "bulk_wechat/manage_messages/draft_list.html" 
    model = WeChatTemplate


