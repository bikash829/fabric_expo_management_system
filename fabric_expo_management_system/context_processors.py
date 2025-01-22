from admin_dashboard.aside_items import get_sidebar_items
from django.urls import reverse
# from admin_dashboard import nav_data
from admin_dashboard import nav_data

def sidebar_items(request):
    
    # if request.user.is_superuser:
    #     nav_data = admin_nav.nav_data(request)
    # else:
    #     nav_data = {}
    # fetch data from nav_data file
    data = nav_data.nav_data(request)


    sidebar_items = get_sidebar_items(request)

    print(data)
    print("=================================")

    
    return {'sidebar_items': sidebar_items,'top_nav': data}