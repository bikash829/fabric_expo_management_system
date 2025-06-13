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


    """ begin:: section 3 bulk messaging"""
    """ end::section 3 bulk messaging """




    sidebar_items,_ = mark_active_sidebar_items(sidebar_items.values(),request.path)
    
    return sidebar_items