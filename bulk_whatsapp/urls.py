from django.urls import path
from . import views

app_name = 'bulk_whatsapp'

urlpatterns = [
    path('import/', views.RecipientCreateView.as_view(), name='import_recipients'),
    path('preview/<int:datasheet_id>/', views.PreviewRecipientsView.as_view(), name='preview_recipients'),
    path('data-sheet/<int:datasheet_id>/delete/', views.DataSheetDeleteView.as_view(), name='delete_datasheet'),

    path('confirm/<int:datasheet_id>/', views.ConfirmWhatsappRecipientsView.as_view(), name='confirm_recipients'),
    path('generate_csv/',views.GenerateCSV.as_view(),name='generate_csv'),

]
