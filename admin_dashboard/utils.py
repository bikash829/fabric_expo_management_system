from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def get_selected_permissions():
    selected = [
        # manage group 
        ('auth','group','add_group'),
        ('auth','group','change_group'),
        ('auth','group','view_group'),
        ('auth','group','delete_group'),

        # user
        ('accounts','user','add_user'),
        ('accounts','user','change_user'),
        ('accounts','user','view_user'),
        ('accounts','user','delete_user'),
        ('accounts','user','can_activate_deactivate_account'),
        ('accounts','user','can_view_active_inactive_users'),

        # manage permissions 
        ('auth','permission','view_permission'),
        ('auth','permission','change_permission'),

        # recipient category
        ('bulk_core','recipientcategory','add_recipientcategory'),
        ('bulk_core','recipientcategory','change_recipientcategory'),
        ('bulk_core','recipientcategory','view_recipientcategory'),
        ('bulk_core','recipientcategory','delete_recipientcategory'),

        # email recipients 
        ('bulk_email','emailrecipient','add_emailrecipient'),
        # ('bulk_email','emailrecipient','change_emailrecipient'),
        ('bulk_email','emailrecipient','view_emailrecipient'),
        # ('bulk_email','emailrecipient','delete_emailrecipient'),

        # email template/draft 
        ('bulk_email', 'emailtemplate', 'add_emailtemplate'),
        ('bulk_email', 'emailtemplate', 'change_emailtemplate'),
        ('bulk_email', 'emailtemplate', 'view_emailtemplate'),
        ('bulk_email', 'emailtemplate', 'delete_emailtemplate'),
        ('bulk_email', 'emailtemplate', 'sendmail_emailtemplate'),

        # email log and queue
        ('bulk_email', 'emailsession', 'view_emailsession'),
        ('bulk_email', 'sentmail', 'view_sentmail'),

        # whatsapp recipients 
        ('bulk_whatsapp','whatsapprecipient', 'add_whatsapprecipient'),
        ('bulk_whatsapp','whatsapprecipient', 'view_whatsapprecipient'),
        # ('bulk_whatsapp','whatsapprecipient', 'change_whatsapprecipient'),
        # ('bulk_whatsapp','whatsapprecipient', 'delete_whatsapprecipient'),

        # whatsapp template/draft 
        ('bulk_whatsapp', 'whatsapptemplate', 'add_whatsapptemplate'),
        ('bulk_whatsapp', 'whatsapptemplate', 'view_whatsapptemplate'),
        ('bulk_whatsapp', 'whatsapptemplate', 'change_whatsapptemplate'),
        ('bulk_whatsapp', 'whatsapptemplate', 'delete_whatsapptemplate'),
        ('bulk_whatsapp', 'whatsapptemplate', 'sendmessage_whatsapptemplate'),

        #whatsapp log 
        ('bulk_whatsapp', 'sentmessage', 'view_sentmessage'),

        # wechat recipients 
        ('bulk_wechat', 'wechatrecipient', 'add_wechatrecipient'),
        ('bulk_wechat', 'wechatrecipient', 'view_wechatrecipient'),
        # ('bulk_wechat', 'wechatrecipient', 'change_wechatrecipient'),
        # ('bulk_wechat', 'wechatrecipient', 'delete_wechatrecipient'),

        # wechat template/draft 
        ('bulk_wechat', 'wechattemplate', 'add_wechattemplate'),
        ('bulk_wechat', 'wechattemplate', 'change_wechattemplate'),
        ('bulk_wechat', 'wechattemplate', 'view_wechattemplate'),
        ('bulk_wechat', 'wechattemplate', 'delete_wechattemplate'),
        ('bulk_wechat', 'wechattemplate', 'sendmessage_wechattemplate'),
        
        #wechat log 
        ('bulk_wechat', 'sentwcmessage', 'view_sentwcmessage'),

    ]
    q = None
    for app_label, model, codename in selected:
        ct = ContentType.objects.get(app_label=app_label, model=model)
        cond = Permission.objects.filter(content_type=ct, codename=codename)
        q = cond if q is None else q | cond
    return q if q is not None else Permission.objects.none()