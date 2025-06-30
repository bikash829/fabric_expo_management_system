from business_data.models import CompanyProfile



business_infos =  CompanyProfile.objects.all() 

business_info = business_infos.first() if business_infos.exists() else None


PROJECT_NAME = business_info.get_company_name_display() if business_info else "ExpoSync"
COMPANY_LOGO = "/static/images/logo.png"
COMPANY_LOGO = business_info.logo.url if business_info and business_info.logo else "/static/images/logo.png"
ADDRESS = business_info.address if business_info and business_info.address else ""
PHONE_NUMBER = str(business_info.phone_number) if business_info and business_info.phone_number else ""
EMAIL = business_info.email if business_info and business_info.email else ""
WEBSITE = business_info.website if business_info and business_info.website else ""
ESTABLISHED_DATE = business_info.established_date if business_info and business_info.established_date else None
DESCRIPTION = business_info.description if business_info and business_info.description else ""