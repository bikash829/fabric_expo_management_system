import uuid
from django.db import models
from django.utils.timezone import now, timedelta
import threading
from bulk_core.models import RecipientCategory, RecipientDataSheet
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



class SentEmail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now=True)
    recipients = models.ManyToManyField(EmailRecipient, related_name='sent_emails')

    def __str__(self):
        return self.subject


class EmailAttachment(models.Model):
    attachment = models.FileField(blank=True,upload_to="bulk_messages_data/email_attachments")
    sent_email = models.ForeignKey(SentEmail,on_delete=models.CASCADE)

    def __str__(self):
        return self.sent_email