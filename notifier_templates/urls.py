from django.conf.urls import *

urlpatterns = patterns('notifier_templates.views',
    url(r'^notify/(?P<app_label>.+)/(?P<model_name>.+)/(?P<pk>\d+?)/(?P<action>.+)/$', 'notify', name='notify'),
    url(r'^admin_helper/$', 'admin_helper', name='admin_helper'),
    url(r'^admin_preview/(?P<app_label>.+)/(?P<model_name>.+)/$', 'admin_preview_auto_emails', name='admin_preview_auto_emails'),
    
)