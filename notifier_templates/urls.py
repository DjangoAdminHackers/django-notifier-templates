from django.urls import *
import notifier_templates.views

urlpatterns = [
    re_path(r'^notify/(?P<app_label>.+)/(?P<model_name>.+)/(?P<pk>\d+?)/(?P<action>.+)/$', notifier_templates.views.notify, name='notify'),
    re_path(r'^admin_helper/$', notifier_templates.views.admin_helper, name='admin_helper'),
    re_path(r'^admin_preview/(?P<app_label>.+)/(?P<model_name>.+)/$', notifier_templates.views.admin_preview_auto_emails, name='admin_preview_auto_emails'),
]