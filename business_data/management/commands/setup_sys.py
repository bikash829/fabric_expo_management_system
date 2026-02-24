from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from business_data.models import CompanyProfile
# from apps.dashboard.models import *  # Replace with actual models you need permissions for

# class Command(BaseCommand):
#     help = 'Setup user groups and permissions'

#     def handle(self, *args, **kwargs):
#         # Define roles
        

#         pass
        # self.stdout.write(self.style.SUCCESS('Roles have been set up.'))
# your_app/management/commands/system_setup.py
COMPANY_DATA = [
    {
        "company_name": "FABRIC_EXPO",
        "address": "Dhaka, Bangladesh",
        "phone_number": "",
        "logo": "company_logos/fabric_expo.jpeg",
    },
    {
        "company_name": "REPUBLIC_EXPORT",
        "address": "Dhaka, Bangladesh",
        "phone_number": "",
        "logo": "company_logos/republic_expo.jpeg",
    },
    {
        "company_name": "INTEXTILE",
        "address": "Dhaka, Bangladesh",
        "phone_number": "",
        "logo": "company_logos/intextile.jpeg",
    },
]


class Command(BaseCommand):
    help = "Initial system setup: create default business info"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for data in COMPANY_DATA:
            # Skip if already exists
            if CompanyProfile.objects.filter(company_name=data["company_name"]).exists():
                self.stdout.write(self.style.WARNING(f"{data['company_name']} already exists. Skipping..."))
                continue

            # Create company profile
            obj = CompanyProfile.objects.create(
                company_name=data["company_name"],
                address=data["address"],
                phone_number=data["phone_number"],
                logo=data["logo"]
            )

            

        self.stdout.write(self.style.SUCCESS("System setup completed successfully."))