from django.urls import path
from . import views

app_name = 'bulk_email'

urlpatterns = [
    path('import/', views.EmailRecipientCreateView.as_view(), name='import_recipients'),
    path('confirm/', views.ConfirmEmailRecipientsView.as_view(), name='confirm_recipients'),
    path('data-sheet/<int:pk>/delete/', views.DataSheetDeleteView.as_view(), name='delete_datasheet'),
]
