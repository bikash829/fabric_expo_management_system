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
                    'url': reverse('bulk_whatsapp:import_recipients'),
                    'icon': "fa-solid fa-address-book",
                },
                {
                    'name': 'Import WeChat CSV',
                    'code_name': 'import_wechat',
                    'url': reverse('bulk_wechat:import_recipients'),
                    'icon': "fa-brands fa-weixin",
                },
            ]
        },
        {
            'name': 'View Recipients',
            'code_name': 'view_recipients',
            'url': None,
            'icon': 'fa-solid fa-eye',
            'children':[
                {
                    'name': 'Email Recipients',
                    'code_name': 'email_recipients_list',
                    'url': reverse('bulk_email:recipient_list'),
                    # 'icon': "bi bi-circle-fill",
                    'icon': "bi bi-record-circle-fill",
                },
                {
                    'name': 'WA Recipients',
                    'code_name': 'whatsapp_recipients_list',
                    'url': reverse('bulk_whatsapp:recipient_list'),
                    # 'icon': "bi bi-circle-fill",
                    'icon': "bi bi-record-circle-fill",
                },
                {
                    'name': 'WeChat Recipients',
                    'code_name': 'wechat_recipients_list',
                    'url': reverse('bulk_wechat:recipient_list'),
                    # 'icon': "bi bi-circle-fill",
                    'icon': "bi bi-record-circle-fill",
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
                        {
                            'name': 'Sent Records',
                            'code_name': 'sent_records',
                            'url': reverse('bulk_email:sent_email_session'),
                            'icon': "fa-solid fa-envelope-circle-check",
                        },
                    ]
                },
                {
                    'name': 'Send wa Message',
                    'code_name': 'send_wh_msg',
                    'url': None,
                    'icon': "fa-brands fa-whatsapp",
                    'children':[
                        {
                            'name': 'Create Message',
                            'code_name': 'create_wa_message',
                            'url': reverse('bulk_whatsapp:create_message'),
                            'icon': "fa-solid fa-pen-to-square",
                        },
                        {
                            'name': 'WA draft',
                            'code_name': 'select_wa_draft',
                            'url': reverse('bulk_whatsapp:draft_list'),
                            'icon': "fa-regular fa-folder-open",
                        },
                        {
                            'name': 'Sent Records',
                            'code_name': 'sent_wa_records',
                            'url': reverse('bulk_whatsapp:sent_message_session'),
                            'icon': "fa-solid fa-check",
                        },
                    ]
                },
                {
                    'name': 'Send WeChat Message',
                    'code_name': 'send_wechat_msg',
                    'url': None,
                    'icon': "fa-brands fa-weixin",
                    'children':[
                        {
                            'name': 'Create Message',
                            'code_name': 'create_wc_message',
                            'url': reverse('bulk_wechat:create_message'),
                            'icon': "fa-solid fa-pen-to-square",
                        },
                        {
                            'name': 'WC draft',
                            'code_name': 'select_wc_draft',
                            'url':  reverse('bulk_wechat:draft_list'),
                            'icon': "fa-regular fa-folder-open",
                        },
                        {
                            'name': 'Sent Records',
                            'code_name': 'sent_wc_records',
                            'url': "#",
                            'icon': "fa-solid fa-check",
                        },
                    ]
                },
            ]
        },
        {
            'divider_header': 'Manage Business Data',
            'code_name': 'manager_buyers',
            'url': None,
        },
        # {
        #     'divider_header': 'Example Divider',
        #     'code_name': '',
        #     'url': None,
        # },
        # {
        #     'name': 'Example 1',
        #     'code_name': '',
        #     'url': None,
        #     'icon': 'fa-solid fa-calendar-check',
        # },
        # {
        #     'name': 'Example 2',
        #     'code_name': '',
        #     'url': None,
        #     'icon': 'fa-solid fa-hourglass-end',
        # },
        # {
        #     'name': 'Noboard',
        #     'code_name': '',
        #     'url': "#",
        #     'icon': 'bi bi-speedometer',
        # },
        # {
        #     'divider_header': 'Community',
        #     'code_name': '',
        #     'url': None,
        # },
        # {
        #     'name': 'Community Forum',
        #     'code_name': '',
        #     'url': None,
        #     'icon': 'fa-solid fa-users'
        # },
        # {
        #     'divider_header': 'Notifications and Messages',
        #     'code_name': '',
        #     'url': None,
        # },
        # {
        #     'name': 'Contact Us Query',
        #     'code_name': '',
        #     'url' : None,
        #     'icon': 'fa-solid fa-envelope',
        # },
        
    ]


    """begin:: section 1 manage group """
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

    
    """begin: section 2 Manage Users"""
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

    """ begin:: section 3 bulk messaging"""
    """ end::section 3 bulk messaging """

    """ begin : section 4 manage business data """
    # manage buyers 
    if (
    request.user.has_perm('master_data.view_buyer') or
    request.user.has_perm('master_data.add_buyer') or
    request.user.has_perm('master_data.change_buyer') or
    request.user.has_perm('master_data.delete_buyer')
    ):
        buyer_menu = {
            'name': 'Manage Buyers',
            'code_name': 'manage_buyers',
            'url': None,
            'icon': 'fa-solid fa-briefcase',
            'children':[]
            
        }
        sidebar_items.append(buyer_menu)

        if request.user.has_perm('master_data.add_buyer'):
            buyer_menu['children'].append(
                {
                    'name': 'Add Buyers',
                    'url': reverse('business_data:buyer-upload'),
                    'icon': 'fa-solid fa-user-plus',
                },
            )
        if request.user.has_perm('master_data.view_buyer'):
            buyer_menu['children'].append(
                {
                    'name': 'View Buyers',
                    'url': reverse('business_data:buyer_list'),
                    'icon': 'fa-solid fa-eye',
                },
            )

    # manage customers 
    if (
    request.user.has_perm('master_data.view_customer') or
    request.user.has_perm('master_data.add_customer') or
    request.user.has_perm('master_data.change_customer') or
    request.user.has_perm('master_data.delete_customer')
    ):
        customer_menu = {
            'name': 'Manage Customers',
            'code_name': 'manage_customers',
            'url': None,
            'icon': 'fa-solid fa-users',
            'children':[]
        }
        sidebar_items.append(customer_menu)
        if request.user.has_perm('master_data.add_customer'):
            customer_menu['children'].append(
                {
                    'name': 'Add Customers',
                    'url': reverse('business_data:customer-upload'),
                    'icon': 'fa-solid fa-user-plus',
                },
            )
        
        if request.user.has_perm('master_data.view_customer'):
            customer_menu['children'].append(
                {
                    'name': 'View Customers',
                    'url': reverse('business_data:customer-list'),
                    'icon': 'fa-solid fa-eye',
                },
            )
        

    # manage suppliers 
    if (
    request.user.has_perm('master_data.view_supplier') or
    request.user.has_perm('master_data.add_supplier') or
    request.user.has_perm('master_data.change_supplier') or
    request.user.has_perm('master_data.delete_supplier')
    ):
        supplier_menu = {
            'name': 'Manage Suppliers',
            'code_name': 'manage_suppliers',
            'url': None,
            'icon': 'fa-solid fa-truck',
            'children':[]
        }
        sidebar_items.append(supplier_menu)
        if request.user.has_perm('master_data.add_supplier'):
            supplier_menu['children'].append(
                {
                    'name': 'Add Supplier',
                    'url': reverse('business_data:supplier-upload'),
                    'icon': 'fa-solid fa-plus',
                },
            )
        if request.user.has_perm('master_data.view_supplier'):
            supplier_menu['children'].append(
                {
                    'name': 'View Suppliers',
                    'url': reverse('business_data:supplier-list'),
                    'icon': 'fa-solid fa-eye',
                },
            )
        
    # manage products 
    if (
    request.user.has_perm('master_data.view_product') or
    request.user.has_perm('master_data.add_product') or
    request.user.has_perm('master_data.change_product') or
    request.user.has_perm('master_data.delete_product')
    ):
        product_menu = {
            'name': 'Manage Products',
            'code_name': 'manage_products',
            'url': None,
            'icon': 'fa-solid fa-box',
            'children':[]
        }
        sidebar_items.append(product_menu)
        if request.user.has_perm('master_data.view_product'):
            product_menu['children'].append(
                {
                    'name': 'View Products',
                    'url': None,
                    'icon': 'fa-solid fa-eye',
                },
            )
        if request.user.has_perm('master_data.add_product'):
            product_menu['children'].append(
                {
                    'name': 'Add Product',
                    'url': None,
                    'icon': 'fa-solid fa-plus',
                },
            )

    """ end: section 4 manage business data """

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