import uuid
from django.db import models
from django.utils.timezone import now, timedelta
import threading
from bulk_core.models import RecipientCategory, RecipientDataSheet
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.
from django.contrib.auth import get_user_model
User = get_user_model()

class WhatsappRecipient(models.Model):
    name = models.CharField(max_length=50,null=True)
    recipient_number = PhoneNumberField(unique=True)
    category = models.ForeignKey(RecipientCategory,on_delete=models.CASCADE)

    def __str__(self):
        return f"Whatsapp number: {self.recipient_number}, Category: {self.category}"
    

class TempRecipient(models.Model):
    name = models.CharField(max_length=50,null=True)
    recipient_id = models.CharField(max_length=100)
    category = models.ForeignKey(RecipientCategory,on_delete=models.CASCADE)
    temp_id = models.CharField(max_length=36,unique=True,default=uuid.uuid4)

    def __str__(self):
        return f"Recipient ID: {self.recipient_id}, Category: {self.category}"
    
    def schedule_deletion(self):
        threading.Timer(10, self.delete).start()

    @classmethod
    def cleanup_old_entries(cls, category=None):
        time_threshold = now() - timedelta(minutes=1)

        query = cls.objects.filter(uploaded_at__lt=time_threshold)
        if category:
            query = query.filter(category=category)

        for entry in query:
            entry.delete()


class WhatsappTemplate(models.Model):
    name = models.CharField(max_length=255)
    message_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    delete_status =  models.BooleanField(default=False)
    is_saved = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            ("sendmessage_whatsapptemplate", "Can send whatsapp messages"),
        ]


class WhatsappAttachment(models.Model):
    attachment = models.FileField(upload_to="bulk_messages_data/whatsapp_attachment")
    template = models.ForeignKey(WhatsappTemplate,on_delete=models.CASCADE,related_name='attachments')

    def __str__(self):
        return self.attachment.name



class SentMessage(models.Model):
    message_template = models.ForeignKey(WhatsappTemplate,on_delete=models.CASCADE)
    recipient_to = models.ForeignKey(WhatsappRecipient,on_delete=models.CASCADE)
    sent_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now=True)
    session_id = models.CharField(max_length=255)
    error_message = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=False)
    

    def __str__(self):
        return self.message_template
    

class WhatsappSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    draft = models.ForeignKey(WhatsappTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('processing', 'Processing'), ('done', 'Done'), ('failed', 'Failed')], default='processing')
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)