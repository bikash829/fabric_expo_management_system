from django.urls import path 
from business_data import views
from django.shortcuts import render

app_name = "business_data"


urlpatterns = [
    # Begin::buyer details """
    path('buyer-details-demo-csv/',views.GenerateCSVBuyer.as_view(),name="buyer_demo_csv"),
    path('upload/', views.BuyerUploadView.as_view(), name='buyer-upload'),
    path('preview/', views.BuyerPreviewView.as_view(), name='buyer-preview'),
    path('buyer_list/',views.BuyerListView.as_view(),name='buyer_list'),
    path('delete-buyers/',views.DeleteBuyerView.as_view(),name="delete-buyers"),
    # path('success/', lambda request: render(request, 'business_data/manage_buyers/success.html'), name='upload-success'),
    # End::buyer details """
    
    # Begin::Customer details"""
    path('generate-csv-data-file-demo/',views.GenerateCSVCustomer.as_view(),name='customer-demo-csv'),
    path('customer-upload/', views.CustomerUploadView.as_view(), name='customer-upload'),
    path('customer-preview/', views.CustomerPreviewView.as_view(), name='customer-preview'),
    path('customer-list/',views.CustomerListView.as_view(),name='customer-list'),
    path('delete-customers/',views.DeleteCustomerView.as_view(),name="delete-customers"),
    # End::Customer details"""

    # Begin::Supplier details"""
    path('supplier-details-demo-csv/',views.GenerateCSVSupplier.as_view(),name="supplier-demo-csv"),
    path('supplier-upload/', views.SupplierUploadView.as_view(), name='supplier-upload'),
    path('supplier-preview/', views.SupplierPreviewView.as_view(), name='supplier-preview'),
    path('supplier-list/',views.SupplierListView.as_view(),name='supplier-list'),
    path('delete-suppliers/',views.DeleteSupplierView.as_view(),name="delete-suppliers"),
    # End::Supplier details"""

    # Begin::Product details"""
    path('product-details-demo-csv/',views.GenerateCSVProduct.as_view(),name="product-demo-csv"),
    path('product-upload/', views.ProductUploadView.as_view(), name='product-upload'),
    path('product-preview/', views.ProductPreviewView.as_view(), name='product-preview'),
    path('product-list/',views.ProductListView.as_view(),name='product-list'),
    path('delete-products/',views.DeleteProductView.as_view(),name="delete-products"),
    # End::Product details"""

]


