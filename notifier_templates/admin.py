from __future__ import unicode_literals
from django.contrib import admin
from django.conf import settings
from django.utils.safestring import mark_safe
from .list_filters import DataFilter
from .models import EmailTemplate, SentNotification



# Modeladmin mixins

class NotifierActions(object):

    # Support for django_row_actions
    def get_row_actions(self, obj):
        row_actions = super(NotifierActions, self).get_row_actions(obj)
        notifier_actions = obj._get_notifier_actions_list()
        if notifier_actions:
            notifier_actions[0]['divided'] = True
            row_actions += notifier_actions
        return row_actions


# Model admin classes

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):

    list_display = ('friendly_description', 'subject')
    fields = ('friendly_description', 'subject', 'body', 'available_fields')
    readonly_fields = ('friendly_description', 'available_fields',)

    def friendly_description(self, obj):
        return u'{}'.format(obj.name.replace('_', ' ').title())
    friendly_description.short_description = 'Template type'
    friendly_description.admin_order_field = 'name'

    def available_fields(self, obj):
        fields = obj.content_type.model_class().get_available_fields(obj.name)
        fields_html = u', '.join([field for field in fields])
        return mark_safe("<div class='help-text'>{}</div>".format(fields_html))
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request):
        return False


@admin.register(SentNotification)
class SentNotificationAdmin(admin.ModelAdmin):
    
    list_display = ('action', 'subject', 'sender', 'recipient_list', 'timestamp')
    list_filter = ('action', DataFilter) if getattr(settings, 'NOTIFIER_REFS_ENABLED', False) else ('action',)
    
    def recipient_list(self, obj):
        return ', '.join(obj.recipients)

