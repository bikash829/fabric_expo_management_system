from django.urls import reverse

def nav_data(request):
    # if request.user.groups.filter(name='doctor') != 'doctor':
    #     return {}
    try:
        photo_url = request.user.profile_photo.url
    except:
        photo_url = '/static/assets/img/user2-160x160.jpg'
    # photo_url = request.user.profile_photo.url if request.user.profile_photo.url else '/media/profile/avatar/blank-profile-picturepng.png'
    try:
        user_name = request.user.full_name
        if user_name is None:
            user_name = request.user.username
    except:
        user_name = request.username
    nav_data={
        'left_menu_items':[
            {
                'name': 'Home',
                'url': reverse('admin_dashboard:welcome')
            },
            # {
            #     'name': 'Contact',
            #     'url': None
            # }
        ],
        'end_menu_items':{
            'messages':[
                {
                    'divider': True,
                    'url': None,
                    'user_avatar': '/static/assets/img/user8-128x128.jpg',
                    'avatar_alt': 'something alternet',
                    'user_name': 'John Pierce',
                    'message': 'I got your message bro',
                    'time' : '4 Hours Ago',
                    'is_unread': True,
                    'is_important': True,
                },
                {
                    'divider': True,
                    'url': None,
                    'user_avatar': '/static/assets/img/user3-128x128.jpg',
                    'avatar_alt': 'something alternet',
                    'user_name': 'John Pierce',
                    'message': 'I got your message bro',
                    'time' : '4 Hours Ago',
                    'is_unread': False,
                    'is_important': True,
                },
                {
                    'divider': True,
                    'url': None,
                    'user_avatar': '/static/assets/img/user7-128x128.jpg',
                    'avatar_alt': 'something alternet',
                    'user_name': 'John Pierce',
                    'message': 'I got your message bro',
                    'time' : '4 Hours Ago',
                    'is_unread': True,
                    'is_important': False,
                },
                {
                    'divider': True,
                    'user_avatar': '/static/assets/img/avatar.png',
                    'avatar_alt': 'something alternet',
                    'user_name': 'Rango',
                    'message': 'Yoo! what\'s up?',
                    'time' : '10 Hours Ago',
                    'is_unread': False,
                    'is_important': False,
                },
            ],
            'notifications':{
                'total_notifications': 16,
                'notification_list':[
                    {
                        'url': None,
                        'icon': 'bi bi-envelope',
                        'notification_count': 5,
                        'notification_from': 'new messages',
                        'time': '3 mins',
                        'divider': True,
                        'icon': 'bi bi-envelope'

                    },
                    {
                        'url': None,
                        'icon': 'bi bi-people-fill',
                        'notification_count': 8,
                        'notification_from': 'friend requests',
                        'time': '12 hour',
                        'divider': True,
                        'icon': 'bi bi-file-earmark-fill',

                    },
                    {
                        'url': None,
                        'icon': 'bi bi-people-fill',
                        'notification_count': 3,
                        'notification_from': 'new reports',
                        'time': '2 days',
                        'divider': True,
                        'icon': 'bi bi-file-earmark-fill',
                    }
                ]
            }
        },
        'self_info':{
            'name': user_name,
            # 'photo': 'dashboard/assets/img/user2-160x160.jpg',
            'photo': photo_url,
            'photo_alt': 'Admin',
            'designation': 'Web Developer',
            'member_from': request.user.date_joined,
            'profile_link': reverse('accounts:profile'),
        }
     
    }

    # Calculate the count of unread messages
    unread_count = sum(1 for message in nav_data['end_menu_items']['messages'] if message['is_unread'])
    nav_data['end_menu_items']['unread_message_count'] = unread_count

    # Calculate the count of unread notifications

    return  nav_data

