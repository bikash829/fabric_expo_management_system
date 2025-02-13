from celery import shared_task
import csv
from bulk_email.models import TempRecipient
from bulk_core.models import RecipientDataSheet

def parse_csv(file):
    with open(file.path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [{"name": row["name"], "email": row["email"]} for row in reader]

@shared_task
def process_csv_file(datasheet_id):
    data_sheet = RecipientDataSheet.objects.get(id=datasheet_id)
    parsed_data = parse_csv(data_sheet.data_sheet)

    temp_recipients = [
        TempRecipient(name=item["name"], email=item["email"], data_sheet=data_sheet, category=data_sheet.category)
        for item in parsed_data
    ]
    TempRecipient.objects.bulk_create(temp_recipients)