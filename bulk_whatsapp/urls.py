from django.urls import path
from . import views

app_name = 'bulk_whatsapp'

urlpatterns = [
    # save or import new recipients from csv file 
    path('import/', views.RecipientCreateView.as_view(), name='import_recipients'),
    path('preview/<int:datasheet_id>/', views.PreviewRecipientsView.as_view(), name='preview_recipients'),
    path('confirm/<int:datasheet_id>/', views.ConfirmWhatsappRecipientsView.as_view(), name='confirm_recipients'),
    path('generate_csv/',views.GenerateCSV.as_view(),name='generate_csv'),
    path('data-sheet/<int:datasheet_id>/delete/', views.DataSheetDeleteView.as_view(), name='delete_datasheet'),

    # create message template for whats app 
    path('create_message/',views.CreateMessageView.as_view(),name="create_message"),
    path('draft_list/',views.DraftView.as_view(),name="draft_list"),
    path('open_draft/<int:pk>/',views.DraftUpdateView.as_view(),name="open_draft"),
    path('select_recipients/<int:draft_id>/',views.SelectRecipientsView.as_view(),name="select_recipients"),
    path('send_message/<int:draft_id>/',views.SendMessageView.as_view(),name="send_message"),
    path('delete_draft/<int:pk>/',views.DraftDeleteView.as_view(),name="delete_draft"),
    path('sent_message_session/',views.SenTMessageSessionListView.as_view(),name='sent_message_session'),

    # path('message_draft')

    

]
