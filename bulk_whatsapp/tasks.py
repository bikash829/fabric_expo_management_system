from celery import shared_task
from bulk_whatsapp.models import (
    SentMessage, 
    WhatsappSession, 
    WhatsappTemplate, 
    WhatsappRecipient, 
    WhatsappAttachment
)
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
# from time import sleep
from fabric_expo_management_system.settings import (
    PROJECT_NAME, 
    TWILIO_ACCOUNT_SID, 
    TWILIO_AUTH_TOKEN, 
    TWILIO_WHATSAPP_NUMBER
)
from twilio.rest import Client

@shared_task
def send_whatsapp_message(user_id, draft_id, recipient_ids, session_id):
    whatsapp_content = get_object_or_404(WhatsappTemplate,pk=draft_id)
    recipients = WhatsappRecipient.objects.filter(id__in=recipient_ids)
    User = get_user_model()
    sender = User.objects.get(pk=user_id)

    # retrieving attachments
    attachments = WhatsappAttachment.objects.filter(template=whatsapp_content)
    # media_urls = [request.build_absolute_uri(attachment.attachment.url) for attachment in attachments]
    media_urls = [
        # "https://demo.twilio.com/owl.png",
        # "https://drive.usercontent.google.com/download?id=0B-olApIC0u0QVjBUY1ctbUsxZjA&export=download&resourcekey=0-5Aqjxlnya5FowVUM8nTr0Q",
        # "https://drive.usercontent.google.com/download?id=0B-olApIC0u0QVjBUY1ctbUsxZjA&export=download&resourcekey=0-5Aqjxlnya5FowVUM8nTr0Q",
    ]
    

    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # results = []

    success_count = 0  
    failure_count = 0

    # Loop through each recipient
    for recipient in recipients:
        # Plain text fallback
        text_body = f"Hello {recipient.name},\n{whatsapp_content.message_content}\nBest Regards,\n{PROJECT_NAME}\n"
        # Send the message
        try:
            message = client.messages.create(
                from_= TWILIO_WHATSAPP_NUMBER,
                body=text_body,
                to=f"whatsapp:{recipient.recipient_number}",
                media_url=media_urls # doesn't support direct file path
            )
            success_count += 1

            # Log successful message
            SentMessage.objects.create(
                recipient_to=recipient,
                message_template=whatsapp_content,
                sent_by=sender,
                sent_at=timezone.now(),  # Set current time
                session_id=session_id,  # Generate unique ID
                status=True,
            )
        except Exception as e:
            failure_count += 1
            # Log unsuccessful message
            SentMessage.objects.create(
                recipient_to=recipient,
                message_template=whatsapp_content,
                sent_by=sender,
                sent_at=timezone.now(),  # Set current time
                session_id=session_id,  # Generate unique ID
                error_message=str(e),
                status=True,
            )
    
    WhatsappSession.objects.update_or_create(
        session_id=session_id,
        defaults={
            'status': 'done' if success_count >= 1 else 'failed',
            'success_count': success_count,
            'failure_count': failure_count
        }
    )
        
