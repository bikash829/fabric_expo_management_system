from django.urls import path
from . import views

app_name='admin_dashboard'

urlpatterns = [
    path('',views.IndexView.as_view(),name='welcome'),
    # manage user 
    path('create_staff/',views.CreateUserView.as_view(),name="create_staff"),
    path('staff_details/<int:pk>/',views.StaffDetailsView.as_view(),name='user_detail'),
    path('update_staff/<int:pk>/',views.ChangeUserView.as_view(),name="update_staff"),
    path('staff/<int:pk>/delete/',views.DeleteStaffView.as_view(),name="delete_staff"),
    
    # control staff account
    path('deactivate_staff/<int:pk>/', views.DeactivateStaffView.as_view(), name='deactivate_staff'),
    path('activate_staff/<int:pk>/', views.ActivateStaffView.as_view(), name='activate_staff'),

    # manage user permissions and groups 
    path("edit-permissions/<int:pk>/", views.ManageUserPermissionView.as_view(), name="edit_staff_permissions"),
    
    # show users 
    path('active_users/', views.ActiveUserListView.as_view(), name='active_users'),
    path('inactive_users/', views.DeactivatedUserListView.as_view(), name='inactive_users'),
    path('superusers/', views.SuperuserListView.as_view(), name='superusers'),
    path('staff_list/',views.StaffListView.as_view(),name="staff_list"),

    # manage groups and permissions 
    path('create-group/',views.CreateGroupView.as_view(),name="create-group"),
    path('group-list/',views.GroupListView.as_view(),name="group-list"),
    path('update-group/<int:pk>/',views.UpdateGroupPermission.as_view(),name="manage-group-permissions"),
    path('delete-group/<int:pk>/',views.DeleteGroupView.as_view(),name="delete-group"),
    
    
]