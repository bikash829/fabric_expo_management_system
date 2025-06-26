import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.db import transaction
from bulk_core.models import RecipientDataSheet, RecipientCategory, TempRecipientDataSheet
from bulk_email.forms import  EmailChangeForm, EmailCreationForm, TempEmailRecipientImportForm
from .models import EmailAttachment, EmailRecipient, EmailSession, EmailTemplate, SentMail,TempEmailRecipient
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
import csv
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError


import mimetypes
from premailer import transform
from bulk_core.utils import replace_hsl_with_rgb
from .tasks import send_mail_queue
from django.core.exceptions import PermissionDenied
"""begin::manage email recipients """
### Generate demo csv file 
class GenerateCSV(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo_email_recipients.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(["name", "email",])
        writer.writerow(['John Doe','example@example.com', ])
        writer.writerow(['John Doe1','example@example1.com', ])
        writer.writerow(['John Doe2','example@example2.com', ])

        return response
        


### import recipient from csv file 
class EmailRecipientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'bulk_email.add_emailrecipient'
    model = TempRecipientDataSheet
    template_name = "bulk_email/import_recipients.html"
    form_class= TempEmailRecipientImportForm

    def get_success_url(self):
        return reverse('bulk_email:preview_recipients', kwargs={'datasheet_id': self.object.pk})


### Preview recipient list imported from csv file 
class PreviewEmailRecipientsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bulk_email:add_emailrecipient'
    template_name = "bulk_email/preview_recipients.html"

    def get(self, request, datasheet_id):
        # Get the uploaded temporary csv file
        data_sheet = get_object_or_404(TempRecipientDataSheet,id=datasheet_id)

        # Read CSV file 
        csv_file = data_sheet.data_sheet
        csv_file.open()
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        csv_file.close()  

        reader = csv.reader(decoded_file)
        next(reader,None)  # Skip header row
        
        temp_recipients = []
        # checking valid data 
        for row in reader:
            if len(row) < 2 or not row[0].strip() or not row[1].strip():  
                continue  # Skip invalid rows
            name, email = row[0].strip(), row[1].strip()

            # check if the email is valid
            try:
                validate_email(email) 
            except ValidationError:
                continue
            # create a list for temporary email recipient object 
            temp_recipients.append(TempEmailRecipient(
                name=name, 
                email=email, 
                category=data_sheet.category, 
                temp_id=uuid.uuid4()
            ))
        # save list into temporary data table 
        temporary_recipients = TempEmailRecipient.objects.bulk_create(temp_recipients)
        recipient_ids = [str(item.temp_id) for item in temporary_recipients]

        return render(request, self.template_name, {
            'recipients': temporary_recipients,
            'data_sheet': data_sheet,
            'recipient_ids': recipient_ids,
        })


class ConfirmEmailRecipientsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bulk_email:add_emailrecipient'

    @transaction.atomic
    def post(self, request, datasheet_id):
        temp_data_sheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)
        temp_ids = request.POST.getlist('recipient_ids')
        
        # check if exist temporary data 
        if not temp_ids:
            messages.error(request, 'No recipients selected for confirmation.')
            return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)

        # retrieve temporary data and check if objects are not empty 
        temp_recipients = list(TempEmailRecipient.objects.filter(temp_id__in=temp_ids))
        if not temp_recipients:
            messages.error(request, 'No valid recipients found.')
            return redirect('bulk_email:preview_recipients', datasheet_id=datasheet_id)
        
        # Array of all duplicate recipients 
        existing_emails = {
            recipient.email: recipient for recipient in EmailRecipient.objects.filter(
                email__in=[tr.email for tr in temp_recipients]
            )
        }

        # create new list for new recipients and update existed recipients if need any
        new_recipients = []
        update_recipients = []

        for tr in temp_recipients:
            # check if exist but update category 
            if tr.email in existing_emails:
                existing_recipient = existing_emails[tr.email]
                if existing_recipient.category != tr.category:
                    existing_recipient.category = tr.category  # Update category
                    update_recipients.append(existing_recipient)
            else:
                # create new recipient's list 
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

        # Save the csv file in permanent storage
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
class DataSheetDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bulk_email.add_emailrecipient'
    def post(self, request, datasheet_id, *args, **kwargs):
        
        try:
            # Get datasheet
            datasheet = get_object_or_404(TempRecipientDataSheet, id=datasheet_id)

            # Get recipient IDs from form data
            recipients_temp_id = request.POST.getlist('recipient_ids[]')

            # Delete selected recipients
            if recipients_temp_id:
                TempEmailRecipient.objects.filter(temp_id__in=recipients_temp_id).delete()
            # Delete datasheet
            datasheet.delete()

            return JsonResponse({'success': True, 'message': 'Data sheet deleted successfully',},status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        


# email categories 
class EmailCategories(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required  = 'bulk_email.view_emailrecipient'
    model = RecipientCategory
    template_name = 'bulk_email/category.html'


# Recipient list based on categories 
class EmailCategoriesRecipientList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required  = 'bulk_email.view_emailrecipient'

    model = EmailRecipient
    template_name = "bulk_email/recipient_list.html"
    context_object_name = "recipients"  # Name for template access

    def get_queryset(self):
        category_id = self.kwargs.get('pk')  # Assuming pk refers to category
        return EmailRecipient.objects.filter(category_id=category_id)
    

# Recipient list view 
class RecipientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'bulk_email.view_emailrecipient'
    model = EmailRecipient
    template_name = "bulk_core/manage_recipient/recipient_list.html"
    context_object_name = 'recipient_list'

    def get_queryset(self):
        # Query the data and rename the column
        queryset = super().get_queryset().annotate(
            recipient_id=F('email')  # Rename the 'email' column to 'recipient_email'
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source'] = 'bulk_email'  # Add extra context
        context['source_title'] = 'email'  # Add extra context
        context['total_recipients'] = self.get_queryset().count()  # Example: Count total recipients
        return context
    


### Export recipient list view 
class ExportRecipientToCSVView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bulk_email.view_emailrecipient'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="email_recipients.csv"'},
        )

        recipients = EmailRecipient.objects.all()

        writer = csv.writer(response)
        writer.writerow(["name", "email","category","id"])
        for item in recipients:
            writer.writerow([item.name,item.email,item.category,item.pk, ])

        return response

    
"""end::manage email recipients """

"""begin::writing email """
class CreateEmail(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'bulk_email.add_emailtemplate'

    template_name = "bulk_email/create_email.html" 
    form_class = EmailCreationForm 
    success_url = reverse_lazy('bulk_email:draft_list')


    def form_valid(self, form):
        form.instance.created_by = self.request.user 

        # Save the email template instance
        email_template = form.save(commit=False)
        email_template.created_by = self.request.user
        email_template.save()
    
        # Handle file attachments
        for file in self.request.FILES.getlist('attachment'):
            EmailAttachment.objects.create(attachment=file,template=email_template)

        messages.success(self.request, "Email draft created successfully.")
    
        return super().form_valid(form)

class EmailDraftListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ['bulk_email.view_emailtemplate']
    model = EmailTemplate
    template_name = "bulk_email/email_draft.html"

    def handle_no_permission(self):
        # Redirect to a custom page if permission is denied
        return redirect('bulk_email:create_email')


    def get_queryset(self):
        return self.model.objects.filter(delete_status=False)  # Only active drafts

# Update email draft form 
class EmailChangeView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'bulk_email.change_emailtemplate'
    model = EmailTemplate
    template_name = "bulk_email/open_draft.html"
    form_class = EmailChangeForm
    success_url = reverse_lazy('bulk_email:draft_list')



    def form_valid(self, form):
        response = super().form_valid(form)  # Correct method call
        # email_template = self.object
        #         # Handle file attachments
        # if 'attachment' in self.request.FILES:
        #     for file in self.request.FILES.getlist('attachment'):
        #         EmailAttachment.objects.create(attachment=file, template=email_template)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Draft Updated'})

        return response  # Return normal response for non-AJAX requests
    
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        return super().form_invalid(form)


### add attachment 
class AddAttachmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):

        draft_id = kwargs.get('draft_id')
        email_template = get_object_or_404(EmailTemplate, id=draft_id)

        # Calculate total size of existing attachments
        existing_attachments = EmailAttachment.objects.filter(template=email_template)
        existing_size_mb = sum(item.attachment.size for item in existing_attachments) / (1024 * 1024)

        # Calculate total size of new files
        new_files = request.FILES.getlist('attachment')
        new_files_size_mb = sum(file.size for file in new_files) / (1024 * 1024)

        total_size_mb = existing_size_mb + new_files_size_mb

        # Ensure the total size does not exceed the 20MB limit
        if total_size_mb > 20:
            response = JsonResponse({'success': False, 'error': 'Total file size exceeds the 20MB limit.'}, status=400)
            print(f"Returning response: {response.content}, status: {response.status_code}")
            return response
        else:
            try:
                # Handle file attachments
                if new_files:
                    for file in new_files:
                        EmailAttachment.objects.create(attachment=file, template=email_template)

                return JsonResponse({'success': True, 'message': 'Attachments added successfully'}, status=200)

            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)

### remove attachment 
class RemoveAttachmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        attachment_id = self.request.POST.get('id')
        attachment = get_object_or_404(EmailAttachment, id=attachment_id)

        try:
            attachment.delete()
            return JsonResponse({'success': True, 'message': 'Attachment deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        

### soft delete email draft  
class DeleteEmailDraftView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'bulk_email.delete_emailtemplate'

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
class SelectRecipientsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bulk_email.sendmail_emailtemplate'
    template_name = "bulk_email/recipient_list.html"

    def get(self, request, *args, **kwargs):
        email_content = get_object_or_404(EmailTemplate,id=kwargs.get('draft_id'))
        recipients = EmailRecipient.objects.all()
        recipients_category = RecipientCategory.objects.all()
        return render(request, self.template_name, {
            'recipients': recipients,
            'email_content': email_content,
            'recipients_category': recipients_category,
        })


# sendmail view 
class SendEmailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'bulk_email.sendmail_emailtemplate'

    def post(self,request,*args,**kwargs):

        draft_id = kwargs.get('draft_id')
        recipient_category_ids = request.POST.getlist('selectedRecipientsCategoriesId[]')
        selectedCompanyId = request.POST.get('selectedCompanyId')
        session_id = str(uuid.uuid4())
        sender_id = request.user.id

        EmailSession.objects.create(
            session_id=session_id,
            sender_id=sender_id,
            draft_id=draft_id,
            status='processing'
        )

        send_mail_queue.delay(
            recipient_category_ids=recipient_category_ids,
            draft_id=draft_id, 
            sender_id = sender_id,
            session_id = session_id,
            company = selectedCompanyId,
        )

        # return JsonResponse({"success_count": success_count, "failure_count": failure_count,'message':f"Email has been sent with {success_count} success and {failure_count} failed attempts."})
        return JsonResponse({'message': "Email sending is processing. We will notify you after completion."})
        # return redirect('bulk_email:email_queue')


class EmailSessionListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'bulk_email.view_emailsession'
    template_name = 'bulk_email/email_queue.html'

class EmailSessionAjaxData(View):
    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_column_index = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', 'asc')  # safer default


        columns = [
            'id', 'created_at', 'draft__subject', 'success_count', 'failure_count', 'status'
        ]

        order_field = columns[int(order_column_index)] if int(order_column_index) < len(columns) else 'id'
        if order_dir == 'asc':
            order_field = '-' + order_field



        qs = EmailSession.objects.all()

        if search_value:
            search_q = Q()
            # List of fields to search (including id and all relevant fields)
            search_fields = columns
            for col in search_fields:
                search_q |= Q(**{f"{col}__icontains": search_value})
            qs = qs.filter(search_q)

        total_count = EmailSession.objects.count()
        filtered_count = qs.count()

        qs = qs.order_by(order_field)[start:start+length]

        data = []
        for obj in qs:
            data.append({
                # idx,  # For Count column (can be filled on client side)
                'id' : obj.id,
                'created_at' : obj.created_at.strftime('%Y-%m-%d %H:%M'),
                'subject': obj.draft.subject,
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

"""end::sending email"""


"""begin::sent email"""
class SenTEmailSessionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'bulk_email.view_sentmail'
    model = SentMail
    template_name = "bulk_email/sent_email_session_list.html"

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

 

"""end::sent email"""