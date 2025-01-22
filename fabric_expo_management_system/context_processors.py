from admin_dashboard.aside_items import get_sidebar_items
from django.urls import reverse
# from admin_dashboard import nav_data
from admin_dashboard import nav_data as admin_nav

def sidebar_items(request):
    
    if request.user.is_superuser:
        nav_data = admin_nav.nav_data(request)
    else:
        nav_data = {}



    sidebar_items = get_sidebar_items(request)

    
    return {'sidebar_items': sidebar_items,'top_nav': nav_data}