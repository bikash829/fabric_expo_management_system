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
    path('buyers/<int:pk>/buyer-detail/', views.BuyerDetailView.as_view(), name='buyer-detail'),
    path('buyer/<int:pk>/edit/', views.BuyerUpdateView.as_view(), name='buyer-edit'),
    path('data-source/buyers/',views.BuyerDataSourceView.as_view(),name="buyer-data-source"),
    path('delete-buyers/',views.DeleteBuyerView.as_view(),name="delete-buyers"),
    # path('success/', lambda request: render(request, 'business_data/manage_buyers/success.html'), name='upload-success'),
    # End::buyer details """
    
    # Begin::Customer details"""
    path('generate-csv-data-file-demo/',views.GenerateCSVCustomer.as_view(),name='customer-demo-csv'),
    path('customer-upload/', views.CustomerUploadView.as_view(), name='customer-upload'),
    path('customer-preview/', views.CustomerPreviewView.as_view(), name='customer-preview'),
    path('customer-list/',views.CustomerListView.as_view(),name='customer-list'),
    path('customer/data-source/',views.CustomerDataSourceView.as_view(),name="customer-data-source"),
    path('customers/<int:pk>/customer-detail/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customer/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer-edit'),
    path('delete-customers/',views.DeleteCustomerView.as_view(),name="delete-customers"),
    # End::Customer details"""

    # Begin::Supplier details"""
    path('supplier-details-demo-csv/',views.GenerateCSVSupplier.as_view(),name="supplier-demo-csv"),
    path('supplier-upload/', views.SupplierUploadView.as_view(), name='supplier-upload'),
    path('supplier-preview/', views.SupplierPreviewView.as_view(), name='supplier-preview'),
    path('supplier-list/',views.SupplierListView.as_view(),name='supplier-list'),
    path('suppliers/data-source/',views.SupplierDataSourceView.as_view(),name="supplier-data-source"),
    path('delete-suppliers/',views.DeleteSupplierView.as_view(),name="delete-suppliers"),
    # End::Supplier details"""

    # Begin::Product details"""
    path('product-details-demo-csv/',views.GenerateCSVProduct.as_view(),name="product-demo-csv"),
    path('product-upload/', views.ProductUploadView.as_view(), name='product-upload'),
    path('product-preview/', views.ProductPreviewView.as_view(), name='product-preview'),
    path('product-list/',views.ProductListView.as_view(),name='product-list'),
    path('products/data-source/', views.ProductDataSourceView.as_view(), name='product_data_source'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products-public/<int:pk>/', views.PublicProductDetailView.as_view(), name='product-detail-public'),
    path('delete-products/',views.DeleteProductView.as_view(),name="delete-products"),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/upload_sample/', views.ProductSampleUploadView.as_view(), name='product-upload-sample'),
    path('product/<int:product_id>/sample/<int:sample_id>/delete/', views.ProductSampleDeleteView.as_view(), name='product-sample-delete'),
    # End::Product details"""

    path('product-list/print-qr-codes/',views.ProductQRCodePDFView.as_view(), name='print_selected_qrcodes'),
    path('product-list/print-barcodes/',views.ProductBarCodePDFView.as_view(), name='print_selected_barcodes'),
    path('product-list/print-product-details/',views.ProductDetailListPDFView.as_view(), name='print-product-list-details'),
    
    path('products/<int:pk>/sticker/', views.ProductDetailViewSticker.as_view(), name='product-detail-sticker'),
    path('products/<int:pk>/print/<str:label_type>/', views.ProductLabelPrintView.as_view(), name='print-product-label'),
    path('products/<int:pk>/save_label_data/', views.SaveProductLabelDataView.as_view(), name='save-product-label-data'),

]


