from django.db import models

from bulk_core.models import RecipientCategory
# Create your models here.

class EmailRecipient(models.Model):
    email = models.EmailField(unique=True)
    category = models.ForeignKey(RecipientCategory,on_delete=models.CASCADE)

    def __str__(self):
        return self.email


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