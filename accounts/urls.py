from django.urls import path,include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path("", include("django.contrib.auth.urls")),

    # user info
    path('profile/',views.ProfileView.as_view(),name="profile"),
    path('change_profile_photo/<int:pk>/',views.change_profile_photo,name='change_profile_photo'),
]
