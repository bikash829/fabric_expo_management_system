import uuid
from django.db import models
from django.forms import ValidationError
from django.utils.timezone import now, timedelta
import threading
from bulk_core.models import RecipientCategory, RecipientDataSheet
from django.contrib.auth import get_user_model
# Create your models here.

class EmailRecipient(models.Model):
    name = models.CharField(max_length=50,null=True)
    email = models.EmailField(unique=True)
    category = models.ForeignKey(RecipientCategory,on_delete=models.CASCADE)

    def __str__(self):
        return f"Email: {self.email}, Category: {self.category}"
    

class TempEmailRecipient(models.Model):
    name = models.CharField(max_length=50,null=True)
    email = models.EmailField()
    category = models.ForeignKey(RecipientCategory,on_delete=models.CASCADE)
    temp_id = models.CharField(max_length=36,unique=True,default=uuid.uuid4)

    def __str__(self):
        return f"Email: {self.email}, Category: {self.category}"
    
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


# class SentEmail(models.Model):
#     subject = models.CharField(max_length=255)
#     body = models.TextField()
#     sent_at = models.DateTimeField(null=True)
#     created_at = models.DateTimeField(auto_now=True)
#     is_draft = models.BooleanField(default=True)
#     is_sent = models.BooleanField(default=False)
#     recipients = models.ManyToManyField(EmailRecipient, related_name='sent_emails')

#     def __str__(self):
#         return self.subject
    

# class EmailAttachment(models.Model):
#     attachment = models.FileField(blank=True,upload_to="bulk_messages_data/email_attachments")
#     sent_email = models.ForeignKey(SentEmail,on_delete=models.CASCADE)

#     def __str__(self):
#         return self.sent_email


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    # changed_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    # edited_by = models.ForeignKey()
    delete_status =  models.BooleanField(default=False)
    is_saved = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EmailAttachment(models.Model):
    attachment = models.FileField(upload_to="bulk_messages_data/email_attachments")
    template = models.ForeignKey(EmailTemplate,on_delete=models.CASCADE,related_name='attachments')

    def __str__(self):
        return self.attachment.name
    
    def clean(self):
        if self.file.size > 20 * 1024 * 1024:
            raise ValidationError("File size must be under 20MB")



class SentMail(models.Model):
    email = models.ForeignKey(EmailTemplate,on_delete=models.CASCADE)
    recipient_to = models.ForeignKey(EmailRecipient,on_delete=models.CASCADE)
    sent_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now=True)
    session_id = models.CharField(max_length=255)
    error_message = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=False)


    

    def __str__(self):
        return self.email