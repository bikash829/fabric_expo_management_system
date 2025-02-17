import os
from django.core import mail
from django.core.exceptions import ValidationError



# Maximum allowed file size (5MB)
MAX_FILE_SIZE = 25 * 1024 * 1024  # 5MB in bytes

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
connection = mail.get_connection()
connection.open()

# Loop through each recipient
for email, name in recipients:
    email_message = mail.EmailMessage(
        subject="Personalized Email with Multiple Attachments",
        body=f"Dear {name},\n\nPlease find the attached files.\n\nBest Regards,\nYour Company",
        from_email="from@example.com",
        to=[email],
        connection=connection,  # Use open connection
    )

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
