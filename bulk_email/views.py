from django.shortcuts import redirect,render
from django.views import View
from bulk_core.models import RecipientDataSheet, RecipientCategory
from bulk_email.forms import EmailRecipientImportForm
from .models import EmailRecipient
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
import csv

# Create your views here.
class EmailRecipientCreateView(CreateView):
    model = RecipientDataSheet
    form_class = EmailRecipientImportForm
    template_name = "bulk_email/import_recipients.html"


    def form_valid(self, form):
        csv_file = self.request.FILES['data_sheet']
        category = form.cleaned_data['category']
      

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        next(reader)  # Skip the header row
        recipients = [{'name': row[0], 'email': row[1]} for row in reader]
        self.request.session['recipients'] = recipients
        self.request.session['category'] = category.id
        print(category)


        # Save the form data
        data_sheet = form.save()

        return render(self.request, 'bulk_email/preview_recipients.html', {'recipients': recipients, 'data_sheet':data_sheet })

class ConfirmEmailRecipientsView(View):
    def post(self, request):
        recipients = request.session.get('recipients', [])
        category_id = request.session.get('category')
        category = RecipientCategory.objects.get(pk=category_id)
        for recipient in recipients:
            existing_recipient = EmailRecipient.objects.filter(email=recipient['email']).first()
            if existing_recipient:
                if existing_recipient.category != category:
                    existing_recipient.category = category
                    existing_recipient.save()
            else:
                EmailRecipient.objects.create(name=recipient['name'], email=recipient['email'], category=category)
        messages.success(request, 'Emails recipients saved successfully!')
        return redirect('bulk_email:import_recipients')


class DataSheetDeleteView(DeleteView):
    model = RecipientDataSheet
    success_url = reverse_lazy("bulk_email:import_recipients")