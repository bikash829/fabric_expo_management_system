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
    sidebar_items = dict()

    """begin::section 0 dashboard"""
    sidebar_items['dashboard'] = {
            'name': 'Dashboard',
            'code_name': '',
            'url': reverse('admin_dashboard:welcome'),
            'icon': 'bi bi-speedometer',
    }
    """end::section 0 dashboard"""

    """begin:: section 1 manage group """
    # create divider and parent group extender if any permission is available
    if request.user.has_perm('auth.add_group') or request.user.has_perm('auth.view_group'):
        sidebar_items.update({
            'groups_and_permission_divider': {
                'divider_header': 'Groups & Permissions',
                'code_name': 'groups_and_permission_divider',
                'url': None,
            },
            'manage_group': {
                'name': 'Manage GP',
                'code_name': 'manage_group',
                'url': None,
                'icon': 'fa-solid fa-screwdriver-wrench',
                'children':[]
            }
        })

    # add group permission
    if request.user.has_perm('auth.add_group'):
        sidebar_items['manage_group']['children'].append(
            {
                'name': 'Create Group',
                'url': reverse('admin_dashboard:create-group'),
                'icon': 'fa-solid fa-user-plus',
            }
        )

    # view group 
    if request.user.has_perm('auth.view_group'):
        sidebar_items['manage_group']['children'].append(
            {
                'name': 'All Groups',
                'url': reverse('admin_dashboard:group-list'),
                'icon': 'fa-solid fa-list-ul',
            }
        )

    """begin:: manage group """

    """begin::section 2 Manage Users"""
    if request.user.has_perm('accounts.add_user') or request.user.has_perm('accounts.view_user'):
        sidebar_items.update({
            'manage_users_divider' : {
                'code_name': '',
                'divider_header': 'Users',
                'url': None,
            },
            'manage_user' : {
                'name': 'Manage User',
                'code_name': 'manage_user',
                'url': None,
                'icon': 'fa-solid fa-screwdriver-wrench',
                'children':[]
            }
        })

    # add group permission
    if request.user.has_perm('accounts.add_user'):
            sidebar_items['manage_user']['children'].append(
                {
                    'name': 'Create Staff',
                    'url': reverse('admin_dashboard:create_staff'),
                    'icon': 'fa-solid fa-user-plus',
                }
            )

    # can_view_active_inactive_users 
    if request.user.has_perm('accounts.can_view_active_inactive_users'):
        sidebar_items['manage_user']['children'].extend([
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
        ])
        # view user 
        if request.user.has_perm('accounts.view_user'):
            sidebar_items['manage_user']['children'].append(
                {
                    'name': 'All Staff',
                    'url': reverse('admin_dashboard:staff_list'),
                    'icon': 'fa-solid fa-user-group',
                }
            )
    """end::section 2 Manage Users"""


    """ begin::section 3 bulk messaging"""
    sidebar_items.update({
        'bulk_messaging_divider' : {
            'divider_header': 'Bulk Messaging',
            'code_name': 'bulk_messaging_divider',
            'url': None,
        },
        'manage_category' : {
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
        'import_recipients' : {
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
        'view_recipients' : {
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
        'send_bulk_message' : {
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
                            'name': 'Email Queue',
                            'code_name': 'email_queue',
                            'url': reverse('bulk_email:email_queue'),
                            'icon': "fa-solid fa-envelope-open-text",
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
        }
    })
    """ end::section 3 bulk messaging """

    """ begin:: section 4 manage business data """
    sidebar_items.update({
        'manager_buyers' : {
            'divider_header': 'Manage Business Data',
            'code_name': 'manager_buyers',
            'url': None,
        },
    })

    # manage buyers 
    if (
    request.user.has_perm('master_data.view_buyer') or
    request.user.has_perm('master_data.add_buyer') or
    request.user.has_perm('master_data.change_buyer') or
    request.user.has_perm('master_data.delete_buyer')
    ):
        sidebar_items['manage_buyers'] = {
            'name': 'Manage Buyers',
            'code_name': 'manage_buyers',
            'url': None,
            'icon': 'fa-solid fa-briefcase',
            'children':[]
        }
    
    if request.user.has_perm('master_data.add_buyer'):
        sidebar_items['manage_buyers']['children'].append(
            {
                'name': 'Add Buyers',
                'url': reverse('business_data:buyer-upload'),
                'icon': 'fa-solid fa-user-plus',
            },
        )
    if request.user.has_perm('master_data.view_buyer'):
        sidebar_items['manage_buyers']['children'].append(
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
        sidebar_items['manage_customers'] = {
            'name': 'Manage Customers',
            'code_name': 'manage_customers',
            'url': None,
            'icon': 'fa-solid fa-users',
            'children':[]
        }

    if request.user.has_perm('master_data.add_customer'):
            sidebar_items['manage_customers']['children'].append(
                {
                    'name': 'Add Customers',
                    'url': reverse('business_data:customer-upload'),
                    'icon': 'fa-solid fa-user-plus',
                },
            )
        
    if request.user.has_perm('master_data.view_customer'):
        sidebar_items['manage_customers']['children'].append(
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
        sidebar_items['manage_suppliers'] = {
            'name': 'Manage Suppliers',
            'code_name': 'manage_suppliers',
            'url': None,
            'icon': 'fa-solid fa-truck',
            'children':[]
        }
        
    if request.user.has_perm('master_data.add_supplier'):
        sidebar_items['manage_suppliers']['children'].append(
            {
                'name': 'Add Supplier',
                'url': reverse('business_data:supplier-upload'),
                'icon': 'fa-solid fa-plus',
            },
        )
    if request.user.has_perm('master_data.view_supplier'):
        sidebar_items['manage_suppliers']['children'].append(
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
        sidebar_items['manage_products'] = {
            'name': 'Manage Products',
            'code_name': 'manage_products',
            'url': None,
            'icon': 'fa-solid fa-box',
            'children':[]
        }

    if request.user.has_perm('master_data.add_product'):
        sidebar_items['manage_products']['children'].append(
            {
                'name': 'Add Product',
                'url': reverse('business_data:product-upload'),
                'icon': 'fa-solid fa-plus',
            },
        )

    if request.user.has_perm('master_data.view_product'):
        sidebar_items['manage_products']['children'].append(
            {
                'name': 'View Products',
                'url': reverse('business_data:product-list'),
                'icon': 'fa-solid fa-eye',
            },
        )


    """ end:: section 4 manage business data """




    sidebar_items,_ = mark_active_sidebar_items(sidebar_items.values(),request.path)
    
    return sidebar_items