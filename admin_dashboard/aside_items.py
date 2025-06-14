from django.urls import reverse


# check permissions 
def build_children(request, perms_and_items):
    """Helper to build children based on permissions."""
    children = []
    for perm, item in perms_and_items:
        if request.user.has_perm(perm):
            children.append(item)
    return children

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
    if request.user.has_perm('accounts.can_view_active_inactive_users') or request.user.has_perm('accounts.can_activate_deactivate_account'):
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
    message_elements = dict()

    """begin::manage recipient category"""
    message_elements['manage_category'] = {
        'name': 'Manage Category',
        'code_name': 'manage_category',
        'url': None,
        'icon': 'fa-solid fa-layer-group',
        'children':[]
    }

    # check if the user has permission to add recipient category
    if request.user.has_perm('bulk_core.add_recipientcategory'):
        message_elements['manage_category']['children'].append(
            {
                'name': 'Create Category',
                'code_name': 'create_category',
                'url': reverse('bulk_core:create_category'),
                'icon': "fa-solid fa-plus",
            }
        )
    
    # check if the user has permission to view recipient category
    if request.user.has_perm('bulk_core.view_recipientcategory'):
        message_elements['manage_category']['children'].append(
            {
                'name': 'Category List',
                'code_name': 'category_list',
                'url': reverse('bulk_core:category_list'),
                'icon': "fa-solid fa-list-ol",
            }
        )

    # remove parent if the child element is empty
    if not message_elements['manage_category']['children']:
        message_elements.pop('manage_category')

    """end::manage recipient category"""
    
    """begin::import recipients """
    message_elements['import_recipients'] = {
        'name': 'Import Recipients',
        'code_name': 'import_recipients',
        'url': None,
        'icon': 'fa-solid fa-file-circle-plus',
        'children':[]
    }

    # add email recipient permission 
    if request.user.has_perm('bulk_email.add_emailrecipient'):
        message_elements['import_recipients']['children'].append(
            {
                'name': 'Import Email CSV',
                'code_name': 'import_email',
                'url': reverse('bulk_email:import_recipients'),
                'icon': "fa-solid fa-at",
            }
        )
    
    # add whatsapp recipient permission 
    if request.user.has_perm('bulk_whatsapp.add_whatsapprecipient'):
        message_elements['import_recipients']['children'].append(
            {
                'name': 'Import Whatsapp CSV',
                'code_name': 'import_whatsapp',
                'url': reverse('bulk_whatsapp:import_recipients'),
                'icon': "fa-solid fa-address-book",
            }
        )
    
    # add wechat recipient permission 
    if request.user.has_perm('bulk_wechat.add_wechatrecipient'):
        message_elements['import_recipients']['children'].append(
            {
                'name': 'Import WeChat CSV',
                'code_name': 'import_wechat',
                'url': reverse('bulk_wechat:import_recipients'),
                'icon': "fa-brands fa-weixin",
            }
        )

    # remove import recipient parent element 
    if not message_elements['import_recipients']['children']:
        message_elements.pop('import_recipients')
    """end::import recipients """


    """begin::View recipients"""
    message_elements['view_recipients'] = {
        'name': 'View Recipients',
        'code_name': 'view_recipients',
        'url': None,
        'icon': 'fa-solid fa-eye',
        'children':[]
    }

    # view email recipient permission 
    if request.user.has_perm('bulk_email.view_emailrecipient'):
        message_elements['view_recipients']['children'].append(
            {
                'name': 'Email Recipients',
                'code_name': 'email_recipients_list',
                'url': reverse('bulk_email:recipient_list'),
                # 'icon': "bi bi-circle-fill",
                'icon': "bi bi-record-circle-fill",
            }
        )

    # view whatsapp recipient permission 
    if request.user.has_perm('bulk_whatsapp.view_whatsapprecipient'):
        message_elements['view_recipients']['children'].append(
            {
                'name': 'WA Recipients',
                'code_name': 'whatsapp_recipients_list',
                'url': reverse('bulk_whatsapp:recipient_list'),
                # 'icon': "bi bi-circle-fill",
                'icon': "bi bi-record-circle-fill",
            }
        )

    # view wechat recipient permission 
    if request.user.has_perm('bulk_wechat.view_wechatrecipient'):
        message_elements['view_recipients']['children'].append(
            {
                'name': 'WeChat Recipients',
                'code_name': 'wechat_recipients_list',
                'url': reverse('bulk_wechat:recipient_list'),
                # 'icon': "bi bi-circle-fill",
                'icon': "bi bi-record-circle-fill",
            }
        )

    # remove view recipient's parent element 
    if not message_elements['view_recipients']['children']:
        message_elements.pop('view_recipients')
    """end::View recipients"""


    """begin::Bulk messaging"""
    # parent messaging element
    message_elements['send_bulk_message'] = {
        'name': 'Send Bulk Message',
        'code_name': 'send_bulk_message',
        'url': None,
        'icon': 'fa-solid fa-paper-plane',
        'children':[]
    }

    # sub-parent send mail element 
    message_elements['send_bulk_message']['children'].append({
        'name': 'Send Mail',
        'code_name': 'send_mail',
        # 'url': reverse('bulk_email:email_category'),
        'url': None,
        'icon': "fa-solid fa-envelope",
        'children':[]
    }) 

    # sub-parent send whatsapp message element 
    message_elements['send_bulk_message']['children'].append({
        'name': 'Send wa Message',
        'code_name': 'send_wh_msg',
        'url': None,
        'icon': "fa-brands fa-whatsapp",
        'children':[]
    })

    # sub-parent send wechat message element 
    message_elements['send_bulk_message']['children'].append({
        'name': 'Send WeChat Message',
        'code_name': 'send_wechat_msg',
        'url': None,
        'icon': "fa-brands fa-weixin",
        'children':[]
    }) 


    remove_elements = []
    # sub-parent element 
    for index,item in enumerate(message_elements['send_bulk_message']['children']):
        # send mail section 
        if item['code_name'] == 'send_mail':
            # check permission add_email template
            if request.user.has_perm('bulk_email.add_emailtemplate'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Create Email',
                        'code_name': 'create_email',
                        'url': reverse('bulk_email:create_email'),
                        'icon': "fa-solid fa-pen-to-square",
                    },
                )

            # check permission view_email template/draft 
            if request.user.has_perm('bulk_email.view_emailtemplate'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Email Drafts',
                        'code_name': 'select_email_draft',
                        'url': reverse('bulk_email:draft_list'),
                        'icon': "fa-regular fa-folder-open",
                    },
                )

            # check permission view_queued email 
            if request.user.has_perm('bulk_email.view_emailsession'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Email Queue',
                        'code_name': 'email_queue',
                        'url': reverse('bulk_email:email_queue'),
                        'icon': "fa-solid fa-envelope-open-text",
                    }
                )
            
            # check permission view_log email 
            if request.user.has_perm('bulk_email.view_sentmail'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Sent Records',
                        'code_name': 'sent_records',
                        'url': reverse('bulk_email:sent_email_session'),
                        'icon': "fa-solid fa-envelope-circle-check",
                    }
                )

            # remove empty sub-parent element
            if not message_elements['send_bulk_message']['children'][index]['children']:
                # message_elements['send_bulk_message']['children'].pop(index)
                remove_elements.append(index)

            
                

        # send whatsapp message section 
        if item['code_name'] == 'send_wh_msg':
            # check permission add_whatsapp template
            if request.user.has_perm('bulk_whatsapp.add_whatsapptemplate'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Create Message',
                        'code_name': 'create_wa_message',
                        'url': reverse('bulk_whatsapp:create_message'),
                        'icon': "fa-solid fa-pen-to-square",
                    }
                )
            
            # check permission view_whatsapp template/draft
            if request.user.has_perm('bulk_whatsapp.view_whatsapptemplate'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'WA draft',
                        'code_name': 'select_wa_draft',
                        'url': reverse('bulk_whatsapp:draft_list'),
                        'icon': "fa-regular fa-folder-open",
                    }
                )
            
            # check permission view_sentwhatsapp template
            if request.user.has_perm('bulk_whatsapp.view_sentmessage'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Sent Records',
                        'code_name': 'sent_wa_records',
                        'url': reverse('bulk_whatsapp:sent_message_session'),
                        'icon': "fa-solid fa-check",
                    }
                )

            # remove empty sub-parent element
            if not message_elements['send_bulk_message']['children'][index]['children']:
                remove_elements.append(index)
          
             
        
        # send wechat message section 
        if item['code_name'] == 'send_wechat_msg':
            # check permission add_wechat template
            if request.user.has_perm('bulk_wechat.add_wechattemplate'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Create Message',
                        'code_name': 'create_wc_message',
                        'url': reverse('bulk_wechat:create_message'),
                        'icon': "fa-solid fa-pen-to-square",
                    }
                )
            
            # check permission view_wechat template/draft
            if request.user.has_perm('bulk_wechat.view_wechattemplate'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'WC draft',
                        'code_name': 'select_wc_draft',
                        'url':  reverse('bulk_wechat:draft_list'),
                        'icon': "fa-regular fa-folder-open",
                    }
                )
            
            # check permission view_sent message log
            if request.user.has_perm('bulk_wechat.view_sentwcmessage'):
                message_elements['send_bulk_message']['children'][index]['children'].append(
                    {
                        'name': 'Sent Records',
                        'code_name': 'sent_wc_records',
                        'url': "#",
                        'icon': "fa-solid fa-check",
                    }
                )
            

            # remove empty sub-parent element
            if not message_elements['send_bulk_message']['children'][index]['children']:
                remove_elements.append(index)
    
    # remove sub-elements 
    message_elements['send_bulk_message']['children'] = [
        item for idx,item in enumerate(message_elements['send_bulk_message']['children']) if idx not in remove_elements
    ]
    
    # remove view recipient's parent element 
    if not message_elements['send_bulk_message']['children']:
        message_elements.pop('send_bulk_message')

    """begin::End messaging"""

    ### create divider if it's not empty
    if message_elements: 
        sidebar_items['bulk_messaging_divider'] = {
                'divider_header': 'Bulk Messaging',
                'code_name': 'bulk_messaging_divider',
                'url': None,
        }
        sidebar_items.update(message_elements)

    """ end::section 3 bulk messaging """

    """ begin:: section 4 manage business data """
    business_data_elements = dict()

    aside_items = {
        'manage_buyers':{
            'name': 'Manage Buyers',
            'code_name': 'manage_buyers',
            'url': None,
            'icon': 'fa-solid fa-briefcase',
            'perms_and_items': [
                ('business_data.add_buyer',{
                    'name': 'Add Buyers',
                    'url': reverse('business_data:buyer-upload'),
                    'icon': 'fa-solid fa-user-plus',
                }),
                ('business_data.view_buyer',{
                    'name': 'View Buyers',
                    'url': reverse('business_data:buyer_list'),
                    'icon': 'fa-solid fa-eye',
                })
            ]
        },
        'manage_customers':{
            'name': 'Manage Customers',
            'code_name': 'manage_customers',
            'url': None,
            'icon': 'fa-solid fa-users',
            'perms_and_items': [
                ('business_data.add_customer',{
                    'name': 'Add Customers',
                    'url': reverse('business_data:customer-upload'),
                    'icon': 'fa-solid fa-user-plus',
                }),
                ('business_data.view_customer',{
                    'name': 'View Customers',
                    'url': reverse('business_data:customer-list'),
                    'icon': 'fa-solid fa-eye',
                })
            ]
        },
        'manage_suppliers':{
            'name': 'Manage Suppliers',
            'code_name': 'manage_suppliers',
            'url': None,
            'icon': 'fa-solid fa-truck',
            'perms_and_items': [
                ('business_data.add_supplier',{
                    'name': 'Add Supplier',
                    'url': reverse('business_data:supplier-upload'),
                    'icon': 'fa-solid fa-plus',
                }),
                ('business_data.view_supplier',{
                    'name': 'View Suppliers',
                    'url': reverse('business_data:supplier-list'),
                    'icon': 'fa-solid fa-eye',
                })
            ]
        },
        'manage_products':{
            'name': 'Manage Products',
            'code_name': 'manage_products',
            'url': None,
            'icon': 'fa-solid fa-box',
            'perms_and_items': [
                ('business_data.add_product',{
                    'name': 'Add Product',
                    'url': reverse('business_data:product-upload'),
                    'icon': 'fa-solid fa-plus',
                }),
                ('business_data.view_product',{
                    'name': 'View Products',
                    'url': reverse('business_data:product-list'),
                    'icon': 'fa-solid fa-eye',
                })
            ]
        },
    }

    # Build sub-parents with their permitted children for business data
    for sub in aside_items.values():
        children = build_children(request, sub['perms_and_items'])
        if children:
            business_data_elements.update({
                 sub['code_name'] : {
                    'name' : sub['name'],
                    'code_name': sub['code_name'],
                    'url': sub['url'],
                    'icon': sub['icon'],
                    'children': children                     
                 }
            })


    ### create divider if it's not empty
    if business_data_elements: 
        sidebar_items['manager_buyers'] = {
                'divider_header': 'Bulk Messaging',
                'code_name': 'bulk_messaging_divider',
                'url': None,
        }
        sidebar_items.update(business_data_elements)

    """ end:: section 4 manage business data """




    sidebar_items,_ = mark_active_sidebar_items(sidebar_items.values(),request.path)
    
    return sidebar_items