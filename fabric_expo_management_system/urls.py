"""
URL configuration for fabric_expo_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path("accounts/", include("accounts.urls")),
    path('dashboard/',include('admin_dashboard.urls')),
    # """begin::bulk messaging"""
    path('bulk_email/',include('bulk_email.urls')),
    path('bulk_wechat/',include('bulk_wechat.urls')),
    path('bulk_whatsapp/',include('bulk_whatsapp.urls')),
    path('bulk_core/',include('bulk_core.urls')),
    # """end::bulk messaging"""
    path('business_data/',include('business_data.urls')),
    # path('business_data/',include('master_data.urls')),
    # path("upload/", custom_upload_function, name="custom_upload_file"),
    path('', RedirectView.as_view(url='/dashboard/', permanent=True)),  # make the dashboard root url
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
