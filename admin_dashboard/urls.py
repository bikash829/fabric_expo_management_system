from django.urls import path
from . import views

app_name='admin_dashboard'

urlpatterns = [
    path('',views.IndexView.as_view(),name='welcome'),
    path('myview/',views.MyView.as_view(),name='myview'),
    path('create_staff/',views.CreateUserView.as_view(),name="create_staff"),
]