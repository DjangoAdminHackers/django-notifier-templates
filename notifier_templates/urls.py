from django.conf.urls import *

urlpatterns = patterns('notifier_templates.views',
    url(r'^notify/(?P<app_label>.+)/(?P<model_name>.+)/(?P<pk>\d+?)/(?P<action>.+)/$', 'notify', name='notify'),
)