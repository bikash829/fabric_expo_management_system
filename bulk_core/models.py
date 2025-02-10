import uuid
from django.db import models
from datetime import datetime
from django.urls import reverse

# Create your models here.
def generate_upload_path(instance, filename, base_dir):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Generate a unique filename using UUID
    unique_filename = f'{uuid.uuid4()}.{ext}'
    # Get the current date
    current_date = datetime.now().strftime('%Y/%m/%d')
    # Construct the upload path

    return f'{base_dir}/{current_date}/{unique_filename}'

def bulk_recipient_directory_path(instance, filename):
    return generate_upload_path(instance, filename, 'bulk_messages_data/bulk_recipients_data_sheet')

PLATFORM_CHOICE = [
        ("whatsapp","WhatsApp"),
        ("wechat","WeChat"),
        ("email","Email"),
    ]

class RecipientDataSheet(models.Model):
    data_sheet = models.FileField(upload_to=bulk_recipient_directory_path) # f"{settings.MEDIA_URL}profile/avatar/blank-profile-picture.png"
    description = models.CharField(max_length=50,null=True,blank=True)
    uploaded_at = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICE)

    def __str__(self):
        return f"Platform: {self.platform}|Upload date: {self.uploaded_at}|sheet name: {self.data_sheet}"
    

class RecipientCategory(models.Model):
    name = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=100)


    def get_absolute_url(self):
        return reverse("bulk_core:category_details", kwargs={"pk": self.pk})


# class MessageLog(models.Model):
#     PLATFORM_CHOICES = [
#         ('email', 'Email'),
#         ('whatsapp', 'WhatsApp'),
#         ('wechat', 'WeChat'),
#     ]

#     session = models.ForeignKey("MessageSession", on_delete=models.CASCADE, related_name="logs")
#     platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
#     recipient = models.CharField(max_length=255)  # Email or phone number
#     status = models.CharField(max_length=10, choices=[('success', 'Success'), ('failed', 'Failed')])
#     error_message = models.TextField(blank=True, null=True)
#     sent_at = models.DateTimeField(auto_now_add=True)

#     # Platform-specific fields
#     email_subject = models.CharField(max_length=255, blank=True, null=True)
#     email_body = models.TextField(blank=True, null=True)
#     media_url = models.URLField(blank=True, null=True)  # For WhatsApp/WeChat
#     message_type = models.CharField(max_length=20, blank=True, null=True)  # For WeChat

#     def __str__(self):
#         return f"{self.platform} - {self.recipient} - {self.status}"



    
