from django.urls import path
from . import views

app_name = 'bulk_core'

urlpatterns = [
    path('create_recipients/',views.CategoryCreateView.as_view(),name='create_category'),
    # path('category_detail/<int:pk>/',views.CategoryDetailView.as_view(),name='category_detail'),
    path('category_list/',views.CategoryListView.as_view(),name='category_list'),
    path('update_category/<int:pk>/',views.CategoryUpdateView.as_view(),name='update_category'),
    path('recipient_category/<int:pk>/delete/',views.CategoryDeleteView.as_view(),name='delete_category'),
    
    path('import_email/',views.ImportEmailView.as_view(),name='import_email'),

]
