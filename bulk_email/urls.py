from django.urls import path
from . import views

app_name = 'bulk_email'

urlpatterns = [
    path('import/', views.EmailRecipientCreateView.as_view(), name='import_recipients'),
    path('confirm//<int:datasheet_id>/', views.ConfirmEmailRecipientsView.as_view(), name='confirm_recipients'),
    path('preview/<int:datasheet_id>/', views.PreviewEmailRecipientsView.as_view(), name='preview_recipients'),
    # path('data-sheet/<int:pk>/delete/', views.DataSheetDeleteView.as_view(), name='delete_datasheet'),
]
