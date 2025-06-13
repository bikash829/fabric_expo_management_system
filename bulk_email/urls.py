from django.urls import path
from . import views

app_name = 'bulk_email'

urlpatterns = [
    # manage recipients 
    path('import/', views.EmailRecipientCreateView.as_view(), name='import_recipients'),
    path('confirm//<int:datasheet_id>/', views.ConfirmEmailRecipientsView.as_view(), name='confirm_recipients'),
    path('preview/<int:datasheet_id>/', views.PreviewEmailRecipientsView.as_view(), name='preview_recipients'),
    path('data-sheet/<int:datasheet_id>/delete/', views.DataSheetDeleteView.as_view(), name='delete_datasheet'),
    path('generate_csv/',views.GenerateCSV.as_view(),name='generate_csv'),
    path('recipient_list/',views.RecipientListView.as_view(),name='recipient_list'),
    path('export_recipient_list/',views.ExportRecipientToCSVView.as_view(),name='export_recipient_list'),



    path('email_category/', views.EmailCategories.as_view(), name='email_category'),
    path('category_recipients/<int:pk>/', views.EmailCategoriesRecipientList.as_view(), name='category_recipients'),

    # sending mail 
    path('write_email/',views.CreateEmail.as_view(),name='create_email'),
    path('add_attachment/<int:draft_id>/',views.AddAttachmentView.as_view(),name='add_attachment'),
    path('remove_attachment/', views.RemoveAttachmentView.as_view(), name='remove_attachment'),
    path('draft_list/',views.EmailDraftListView.as_view(),name='draft_list'),
    path('open_draft/<int:pk>/',views.EmailChangeView.as_view(),name='open_draft'),
    path('delete_draft/<int:pk>/',views.DeleteEmailDraftView.as_view(),name='delete_draft'),
    path('select_recipients/<int:draft_id>/',views.SelectRecipientsView.as_view(),name='select_recipients'),
    path('send_email/<int:draft_id>/',views.SendEmailView.as_view(),name='send_email'),
    path('sent_email_session/',views.SenTEmailSessionListView.as_view(),name='sent_email_session'),
    path('email_queue/',views.EmailSessionListView.as_view(),name='email_queue'),
    path('email-session-data-source/',views.EmailSessionAjaxData.as_view(),name='email_session_ajax_data'),
    # path('email-status/<str:session_id>/', views.email_status_view, name='email_status'),

    # path('email_progress/',views.email_progress,name='email_progress'),
]
