# utils.py
from django.urls import reverse

# Create sidebar items
def mark_active_sidebar_items(items, current_path):
    any_active = False

    for item in items:
        item['is_active'] = current_path == item['url']
        
        if 'children' in item and item['children']:
            item['children'], child_active = mark_active_sidebar_items(item['children'], current_path)
            item['is_active'] = item['is_active'] or child_active

        any_active = any_active or item['is_active']

    return items, any_active

def get_sidebar_items(request):
    # Admin sidebar
    sidebar_items = [
        {
            'name': 'Dashboard',
            'url': reverse('admin_dashboard:welcome'),
            'icon': 'bi bi-speedometer',
        },
        {
            'divider_header': 'Example Divider',
            'url': None,
        },
        {
            'name': 'Example 1',
            'url': None,
            'icon': 'fa-solid fa-calendar-check',
        },
        {
            'name': 'Example 2',
            'url': None,
            'icon': 'fa-solid fa-hourglass-end',
        },
        {
            'name': 'Noboard',
            'url': "#",
            'icon': 'bi bi-speedometer',
        },
        {
            'divider_header': 'Users',
            'url': None,
        },
        {
            'name': 'Manage User',
            'url': None,
            'icon': 'fa-solid fa-screwdriver-wrench',
            'children':[
                
                {
                    'name': 'Create Staff',
                    'url': reverse('admin_dashboard:create_staff'),
                    'icon': 'fa-solid fa-user-plus',
                },
                {
                    'name': 'Pending Staff',
                    'url': reverse('admin_dashboard:myview'),
                    'icon': 'fa-solid fa-hourglass-end',
                },
                {
                    'name': 'Blocked User',
                    'url': None,
                    'icon': 'fa-solid fa-ban',
                },
                {
                    'name': 'All User',
                    'url': None,
                    'icon': 'fa-solid fa-user-group',
                },
            ]
        },
        
        {
            'divider_header': 'Community',
            'url': None,
        },
        {
            'name': 'Community Forum',
            'url': None,
            'icon': 'fa-solid fa-users'
        },
        {
            'divider_header': 'Notifications and Messages',
            'url': None,
        },
        {
            'name': 'Contact Us Query',
            'url' : None,
            'icon': 'fa-solid fa-envelope',
        },
        
    ]
   

    # if request.user.groups.filter(name='doctor').exists():
    #     sidebar_items, _ = mark_active_sidebar_items(doctor_sidebar_items, request.path)
    # elif request.user.groups.filter(name='counselor').exists():
    #     sidebar_items, _ = mark_active_sidebar_items(counselor_sidebar_items, request.path)
    # elif request.user.is_superuser:
    #     sidebar_items, _ = mark_active_sidebar_items(sidebar_items, request.path)
    # else:
    #     sidebar_items, _ = []
    sidebar_items,_ = mark_active_sidebar_items(sidebar_items,request.path)
    
    return sidebar_items