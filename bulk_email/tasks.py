from celery import shared_task
import mimetypes
from premailer import transform
from bulk_core.utils import replace_hsl_with_rgb
from django.core.mail import EmailMultiAlternatives, get_connection
from .models import EmailAttachment, EmailSession, SentMail, EmailRecipient, EmailTemplate
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from fabric_expo_management_system.settings import  EMAIL_HOST_USER
from fabric_expo_management_system.info import PROJECT_NAME


# def parse_csv(file):
#     with open(file.path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         return [{"name": row["name"], "email": row["email"]} for row in reader]

# @shared_task
# def process_csv_file(datasheet_id):
#     data_sheet = RecipientDataSheet.objects.get(id=datasheet_id)
#     parsed_data = parse_csv(data_sheet.data_sheet)

#     temp_recipients = [
#         TempRecipient(name=item["name"], email=item["email"], data_sheet=data_sheet, category=data_sheet.category)
#         for item in parsed_data
#     ]
#     TempRecipient.objects.bulk_create(temp_recipients)

@shared_task
def send_mail_queue(**kwargs):
    User = get_user_model()
    email_content = get_object_or_404(EmailTemplate,id=kwargs.get('draft_id'))
    recipients = EmailRecipient.objects.filter(id__in=kwargs['recipient_ids'])
    sender = User.objects.get(id=kwargs.get('sender_id'))

    # Open a single SMTP connection for efficiency
    connection = get_connection()
    connection.open()

    # Track success and failure
    success_count = 0
    failure_count = 0

    # Loop through each recipient
    for recipient in recipients:
        # Plain text fallback
        text_body = f"""Dear {recipient.name},\n

                        {email_content.body}\n\n

                        Best Regards,\n
                        {PROJECT_NAME}\n
                    """

        # HTML Email (Better Formatting)
        html_body = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                            Dear {recipient.name},
                            <p>{email_content.body}</p>
                            <p style="margin-top: 20px;">Best Regards,<br>
                            <strong>{PROJECT_NAME}</strong></p>
                        </body>
                        </html>
                    """
        
        # Transform HSL to RGB
        html_body = transform(replace_hsl_with_rgb(html_body))
        
        # Create email
        email_message = EmailMultiAlternatives(
            subject=email_content.subject,
            # body=text_body,  # Plain text version
            from_email=EMAIL_HOST_USER,
            # from_email="admin@email.com",
            to=[recipient.email],
            connection=connection,  # Use open connection
        )
        
        # Attach HTML version for better formatting
        email_message.attach_alternative(html_body, "text/html")
        # Attach files
        attachments = EmailAttachment.objects.filter(template=email_content)
        for attachment in attachments:
            file_path = attachment.attachment.path
            file_name = attachment.attachment.name
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'rb') as f:
                email_message.attach(file_name, f.read(), mime_type)
        # Send the email
        try:
            email_message.send()
            success_count += 1

            # Log successful email
            SentMail.objects.create(
                recipient_to=recipient,
                email=email_content,
                sent_by= sender,
                sent_at=timezone.now(),  # Set current time
                session_id= kwargs['session_id'],  # Generate unique ID
                status=True,
            )
        except Exception as e:
            # Log failed email
            failure_count += 1
            SentMail.objects.create(
                email=email_content,
                recipient_to=recipient,
                sent_by=sender,
                sent_at=timezone.now(),  # Set current time
                session_id=kwargs['session_id'],  # Generate unique ID
                error_message=str(e),
                status=False,
            )
        
    
    # Close the connection after all emails are sent
    connection.close()

    EmailSession.objects.update_or_create(
        session_id=kwargs['session_id'],
        defaults={
            'status': 'done' if success_count >= 1 else 'failed',
            'success_count': success_count,
            'failure_count': failure_count
        }
    )
    # print(f"Email has been sent with {success_count} success and {failure_count} failed attempts.")