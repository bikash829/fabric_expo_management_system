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
            'code_name': '',
            'url': reverse('admin_dashboard:welcome'),
            'icon': 'bi bi-speedometer',
        },
        {
            'divider_header': 'Example Divider',
            'code_name': '',
            'url': None,
        },
        {
            'name': 'Example 1',
            'code_name': '',
            'url': None,
            'icon': 'fa-solid fa-calendar-check',
        },
        {
            'name': 'Example 2',
            'code_name': '',
            'url': None,
            'icon': 'fa-solid fa-hourglass-end',
        },
        {
            'name': 'Noboard',
            'code_name': '',
            'url': "#",
            'icon': 'bi bi-speedometer',
        },
        {
            'divider_header': 'Groups & Permissions',
            'code_name': '',
            'url': None,
        },
        {
            'name': 'Manage GP',
            'code_name': 'manage_group',
            'url': None,
            'icon': 'fa-solid fa-screwdriver-wrench',
            'children':[
                {
                    'name': 'All Groups',
                    'url': reverse('admin_dashboard:group-list'),
                    'icon': 'fa-solid fa-list-ul',
                },
            ]
        },
        {
            'code_name': '',
            'divider_header': 'Users',
            'url': None,
        },
        {
            'name': 'Manage User',
            'code_name': 'manage_user',
            'url': None,
            'icon': 'fa-solid fa-screwdriver-wrench',
            'children':[
                
                {
                    'name': 'Create Staff',
                    'url': reverse('admin_dashboard:create_staff'),
                    'icon': 'fa-solid fa-user-plus',
                },
                {
                    'name': 'Inactive Accounts',
                    'url': reverse('admin_dashboard:inactive_users'),
                    'icon': 'fa-solid fa-ban',
                },
                {
                    'name': 'Active Accounts',
                    'url': reverse('admin_dashboard:active_users'),
                    'icon': 'fa-solid fa-user-check',
                },
                {
                    'name': 'Super Users',
                    'url': reverse('admin_dashboard:superusers'),
                    'icon': 'fa-solid fa-user-shield',
                },
                {
                    'name': 'All Staff',
                    'url': reverse('admin_dashboard:staff_list'),
                    'icon': 'fa-solid fa-user-group',
                },
            ]
        },
        
        {
            'divider_header': 'Community',
            'code_name': '',
            'url': None,
        },
        {
            'name': 'Community Forum',
            'code_name': '',
            'url': None,
            'icon': 'fa-solid fa-users'
        },
        {
            'divider_header': 'Notifications and Messages',
            'code_name': '',
            'url': None,
        },
        {
            'name': 'Contact Us Query',
            'code_name': '',
            'url' : None,
            'icon': 'fa-solid fa-envelope',
        },
        
    ]

    for index,item in enumerate(sidebar_items):
        print(item.get('name'))
        print("permission close=======================")

        if request.user.has_perm('auth.add_group'):
            if item.get('code_name') == 'manage_group':
                print("permission granted=======================7")
                # sidebar_items[item]['children'].append({
                #     'name': 'Create Group',
                #     'url': reverse('admin_dashboard:create-group'),
                #     'icon': 'fa-solid fa-user-plus',
                # })

                sidebar_items[index]['children'].insert(
                    0,
                    {
                        'name': 'Create Group',
                        'url': reverse('admin_dashboard:create-group'),
                        'icon': 'fa-solid fa-user-plus',
                    }
                )
                

                print(sidebar_items[index])

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