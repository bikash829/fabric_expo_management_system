import os
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.exceptions import ValidationError

# Maximum allowed file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# List of recipients with names
recipients = [
    ("to1@example.com", "John"),
    ("to2@example.com", "Jane"),
    ("to3@example.com", "Doe"),
]

# List of attachments (file paths)
attachments = ["path/to/file1.pdf", "path/to/file2.jpg", "path/to/file3.docx"]

# Function to validate file size
def validate_attachment(file_path):
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        if file_size > MAX_FILE_SIZE:
            raise ValidationError(f"File {file_path} exceeds the 5MB size limit.")
    else:
        raise ValidationError(f"File {file_path} does not exist.")

# Open a single SMTP connection for efficiency
connection = get_connection()
connection.open()

# Loop through each recipient
for email, name in recipients:
    # Plain text fallback
    text_body = f"""Dear {name},

                Please find the attached files.

                Best Regards,
                Your Company
                """

    # HTML Email (Better Formatting)
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>Dear {name},</p>
        <p>Please find the attached files.</p>
        <p style="margin-top: 20px;">Best Regards,<br><strong>Your Company</strong></p>
    </body>
    </html>
    """

    # Create email
    email_message = EmailMultiAlternatives(
        subject="Personalized Email with Proper Spacing & Attachments",
        body=text_body,  # Plain text version
        from_email="from@example.com",
        to=[email],
        connection=connection,  # Use open connection
    )
    
    # Attach HTML version for better formatting
    email_message.attach_alternative(html_body, "text/html")

    # Attach multiple files with validation
    for file in attachments:
        try:
            validate_attachment(file)  # Validate file size
            with open(file, "rb") as f:
                email_message.attach(os.path.basename(file), f.read())  # Attach file
        except ValidationError as e:
            print(f"Skipping {file}: {e}")  # Log validation error and continue

    # Send the email
    email_message.send()

# Close the connection after all emails are sent
connection.close()

import os
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.exceptions import ValidationError

# Maximum allowed file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def send_personalized_email(subject, recipients, body_text, body_html, attachments=None):
    """
    Sends a personalized email with HTML formatting, proper spacing, and attachments.

    Parameters:
        subject (str): The email subject.
        recipients (list): List of tuples [(email, name)] for personalization.
        body_text (str): Plain text version of the email body.
        body_html (str): HTML version of the email body.
        attachments (list, optional): List of file paths to attach.
    """
    
    # Open SMTP connection for efficiency
    connection = get_connection()
    connection.open()

    # Loop through recipients
    for email, name in recipients:
        # Personalize text and HTML body
        personalized_text = body_text.format(name=name)
        personalized_html = body_html.format(name=name)

        # Create email message
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=personalized_text,  # Plain text fallback
            from_email="from@example.com",
            to=[email],
            connection=connection,
        )

        # Attach HTML version for better formatting
        email_message.attach_alternative(personalized_html, "text/html")

        # Attach files if provided
        if attachments:
            for file in attachments:
                try:
                    if not os.path.exists(file):
                        raise ValidationError(f"File {file} does not exist.")
                    
                    file_size = os.path.getsize(file)
                    if file_size > MAX_FILE_SIZE:
                        raise ValidationError(f"File {file} exceeds the 5MB size limit.")

                    with open(file, "rb") as f:
                        email_message.attach(os.path.basename(file), f.read())

                except ValidationError as e:
                    print(f"Skipping {file}: {e}")  # Log error and continue
        
        # Send the email
        email_message.send()

    # Close SMTP connection after all emails are sent
    connection.close()

