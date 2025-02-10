from django.urls import path,include, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path(
        "password_change/", auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("accounts:password_change_done")
        ), name="password_change"
    ),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'), # must maintain order
    path("", include("django.contrib.auth.urls")),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
        
    # user info
    path('profile/',views.ProfileView.as_view(),name="profile"),
    path('change_profile_photo/<int:pk>/',views.change_profile_photo,name='change_profile_photo'),
    path('change_email/<int:pk>/',views.EmailChangeView.as_view(),name='change_email'),
    path('change-username/<int:pk>/',views.UsernameChangeView.as_view(),name='change_username'),
    path('update-profile/<int:pk>/',views.UpdateProfileView.as_view(),name='update_profile'),





 


]
