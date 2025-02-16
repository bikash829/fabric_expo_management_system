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
            'divider_header': 'Bulk Messaging',
            'code_name': '',
            'url': None,
        },
        {
            'name': 'Manage Category',
            'code_name': 'manage_category',
            'url': None,
            'icon': 'fa-solid fa-layer-group',
            'children':[
                {
                    'name': 'Create Category',
                    'code_name': 'create_category',
                    'url': reverse('bulk_core:create_category'),
                    'icon': "fa-solid fa-plus",
                },
                {
                    'name': 'Category List',
                    'code_name': 'category_list',
                    'url': reverse('bulk_core:category_list'),
                    'icon': "fa-solid fa-list-ol",
                },
            ]
        },
        {
            'name': 'Import Recipients',
            'code_name': 'import_recipients',
            'url': None,
            'icon': 'fa-solid fa-file-circle-plus',
            'children':[
                {
                    'name': 'Import Email CSV',
                    'code_name': 'import_email',
                    'url': reverse('bulk_email:import_recipients'),
                    'icon': "fa-solid fa-at",
                },
                {
                    'name': 'Import Whatsapp CSV',
                    'code_name': 'import_whatsapp',
                    'url': None,
                    'icon': "fa-solid fa-address-book",
                },
                {
                    'name': 'Import WeChat CSV',
                    'code_name': 'import_wechat',
                    'url': None,
                    'icon': "fa-brands fa-weixin",
                },
            ]
        },
        {
            'name': 'Send Bulk Message',
            'code_name': 'send_bulk_message',
            'url': None,
            'icon': 'fa-solid fa-paper-plane',
            'children':[
                {
                    'name': 'Send Mail',
                    'code_name': 'send_mail',
                    # 'url': reverse('bulk_email:email_category'),
                    'url': None,
                    'icon': "fa-solid fa-envelope",
                    'children':[
                        {
                            'name': 'Create Email',
                            'code_name': 'create_email',
                            'url': reverse('bulk_email:create_email'),
                            'icon': "fa-solid fa-pen-to-square",
                        },
                        {
                            'name': 'Email Drafts',
                            'code_name': 'select_email_draft',
                            'url': reverse('bulk_email:draft_list'),
                            'icon': "fa-regular fa-folder-open",
                        },
                    ]
                },
                {
                    'name': 'Send Whatsapp Message',
                    'code_name': 'send_wh_msg',
                    'url': None,
                    'icon': "fa-solid fa-message",
                },
                {
                    'name': 'Send WeChat Message',
                    'code_name': 'send_wechat_msg',
                    'url': None,
                    'icon': "fa-solid fa-comments",
                },
            ]
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


    """begin:: manage group """
    # create divider and parent group extender if any permission is available
    if request.user.has_perm('auth.add_group') or request.user.has_perm('auth.view_group'):
        sidebar_items.insert(
            1,
            {
                'divider_header': 'Groups & Permissions',
                'code_name': '',
                'url': None,
            }
        )
        sidebar_items.insert(
            2,
            {
                'name': 'Manage GP',
                'code_name': 'manage_group',
                'url': None,
                'icon': 'fa-solid fa-screwdriver-wrench',
                'children':[]
            }
        )
    
    # create nav menu if permission available 
    for index,item in enumerate(sidebar_items):
        # add group permission
        if request.user.has_perm('auth.add_group'):
            if item.get('code_name') == 'manage_group':
                sidebar_items[index]['children'].insert(
                    0,
                    {
                        'name': 'Create Group',
                        'url': reverse('admin_dashboard:create-group'),
                        'icon': 'fa-solid fa-user-plus',
                    }
                )
        # view group 
        if request.user.has_perm('auth.view_group'):
            if item.get('code_name') == 'manage_group':
                sidebar_items[index]['children'].insert(
                    1,
                    {
                        'name': 'All Groups',
                        'url': reverse('admin_dashboard:group-list'),
                        'icon': 'fa-solid fa-list-ul',
                    },
                )
    """begin:: manage group """

    
    """begin: Manage Users"""
    # create divider and parent group extender if any permission is available
    if request.user.has_perm('accounts.add_user') or request.user.has_perm('accounts.view_user'):
        sidebar_items.insert(
            3,
            {
                'code_name': '',
                'divider_header': 'Users',
                'url': None,
            },
        )
        sidebar_items.insert(
            4,
            {
                'name': 'Manage User',
                'code_name': 'manage_user',
                'url': None,
                'icon': 'fa-solid fa-screwdriver-wrench',
                'children':[]
            }
        )


        # create nav menu if permission available 
        for index,item in enumerate(sidebar_items):
            # add group permission
            if request.user.has_perm('accounts.add_user'):
                if item.get('code_name') == 'manage_user':
                    sidebar_items[index]['children'].insert(
                        0,
                        {
                            'name': 'Create Staff',
                            'url': reverse('admin_dashboard:create_staff'),
                            'icon': 'fa-solid fa-user-plus',
                        },
                    )

        
            # can_view_active_inactive_users 
            if request.user.has_perm('accounts.can_view_active_inactive_users'):
                if item.get('code_name') == 'manage_user':
                    user_nav_list = [
                        {
                            'name': 'Inactive Accounts',
                            'url': reverse('admin_dashboard:inactive_users'),
                            'icon': 'fa-solid fa-ban',
                        },
                        {
                            'name': 'Active Accounts',
                            'url': reverse('admin_dashboard:active_users'),
                            'icon': 'fa-solid fa-user-check',
                        }
                    ]
                    sidebar_items[index]['children'].extend(user_nav_list)


            # view group 
            if request.user.has_perm('accounts.view_user'):
                if item.get('code_name') == 'manage_user':
                    sidebar_items[index]['children'].append(
                        {
                            'name': 'All Staff',
                            'url': reverse('admin_dashboard:staff_list'),
                            'icon': 'fa-solid fa-user-group',
                        },
                    )
            
    """end: Manage Users"""

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