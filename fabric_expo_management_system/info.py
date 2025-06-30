from business_data.models import CompanyProfile

business_info = CompanyProfile.objects.first()

PROJECT_NAME = (
    business_info.get_company_name_display()
    if business_info else "ExpoSync"
)

COMPANY_LOGO = (
    getattr(business_info, 'logo', None).url
    if business_info and getattr(business_info, 'logo', None)
    else "/static/images/logo.png"
)

ADDRESS = getattr(business_info, 'address', "")
PHONE_NUMBER = str(getattr(business_info, 'phone_number', "")) or ""
EMAIL = getattr(business_info, 'email', "")
WEBSITE = getattr(business_info, 'website', "")
ESTABLISHED_DATE = getattr(business_info, 'established_date', None)
DESCRIPTION = getattr(business_info, 'description', "")
