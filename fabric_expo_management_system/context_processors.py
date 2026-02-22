from admin_dashboard.aside_items import get_sidebar_items
from decouple import config
# from admin_dashboard import nav_data
from admin_dashboard import nav_data
# from fabric_expo_management_system.info import PROJECT_NAME,COMPANY_LOGO,business_infos
from fabric_expo_management_system.info import get_project_settings, get_business_info
from fabric_expo_management_system.version import __version__ as APP_VERSION



def sidebar_items(request):
    
    # if request.user.is_superuser:
    #     nav_data = admin_nav.nav_data(request)
    # else:
    #     nav_data = {}
    # fetch data from nav_data file
    # data = nav_data.nav_data(request)
    # sidebar_items = get_sidebar_items(request)
    
    # return {'sidebar_items': sidebar_items,'top_nav': data}
    if request.user.is_authenticated:
        data = nav_data.nav_data(request)
        sidebar_items = get_sidebar_items(request)
        return {
            'top_nav': data,
            'sidebar_items': sidebar_items,
        }
    else:
        return {}
    

def system_info(request):
    # business info 
    business_info = get_business_info()
    project_settings = get_project_settings()
    data = {
        'PROJECT_NAME': project_settings["PROJECT_NAME"],
        'COMPANY_LOGO': project_settings["COMPANY_LOGO"],
        'APP_VERSION': f"{APP_VERSION}",
        'business_infos': business_info,
    }

    return data