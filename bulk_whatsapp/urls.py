from django.urls import path
from . import views

app_name = 'bulk_whatsapp'

urlpatterns = [
    # manage recipients
    path('import/', views.RecipientCreateView.as_view(), name='import_recipients'),
    path('preview/<int:datasheet_id>/', views.PreviewRecipientsView.as_view(), name='preview_recipients'),
    path('confirm/<int:datasheet_id>/', views.ConfirmWhatsappRecipientsView.as_view(), name='confirm_recipients'),
    path('generate_csv/',views.GenerateCSV.as_view(),name='generate_csv'),
    path('data-sheet/<int:datasheet_id>/delete/', views.DataSheetDeleteView.as_view(), name='delete_datasheet'),
    path('recipient_list/',views.RecipientListView.as_view(),name='recipient_list'),
    path('export_recipient_list/',views.ExportRecipientToCSVView.as_view(),name='export_recipient_list'),

    # manage templates
    path('create_message/',views.CreateMessageView.as_view(),name="create_message"),
    path('add_attachment/<int:draft_id>/',views.AddAttachmentView.as_view(),name='add_attachment'),
    path('remove_attachment/', views.RemoveAttachmentView.as_view(), name='remove_attachment'),
    path('draft_list/',views.DraftView.as_view(),name="draft_list"),
    path('open_draft/<int:pk>/',views.DraftUpdateView.as_view(),name="open_draft"),
    path('delete_draft/<int:pk>/',views.DraftDeleteView.as_view(),name="delete_draft"),
    
    path('select_recipients/<int:draft_id>/',views.SelectRecipientsView.as_view(),name="select_recipients"),
    path('send_message/<int:draft_id>/',views.SendMessageView.as_view(),name="send_message"),
    path('sent_message_session/',views.SenTMessageSessionListView.as_view(),name='sent_message_session'),
    path('sent_message_queue/',views.SendMessageQueueListView.as_view(),name='sent_message_queue'),
    path('sent_message_queue_ajax/',views.SendMessageQueueAjaxListView.as_view(),name='sent_message_queue_ajax'),



    # path('message_draft')

    

]
