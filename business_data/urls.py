from django.urls import path 
from business_data import views
from django.shortcuts import render

app_name = "business_data"


urlpatterns = [
    path('buyer-details-demo-csv/',views.GenerateCSVBuyer.as_view(),name="buyer_demo_csv"),
    path('upload/', views.BuyerUploadView.as_view(), name='buyer-upload'),
    path('preview/', views.BuyerPreviewView.as_view(), name='buyer-preview'),
    path('success/', lambda request: render(request, 'business_data/manage_buyers/success.html'), name='upload-success'),
]


