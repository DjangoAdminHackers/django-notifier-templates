from __future__ import unicode_literals
from django.contrib import admin
from django.conf import settings
from django.utils.safestring import mark_safe
from .list_filters import DataFilter
from .models import EmailTemplate, SentNotification


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):

    list_display = ('friendly_description', 'subject')
    fields = ('friendly_description', 'subject', 'body', 'available_fields', 'plain_body', 'is_plain_only')
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

    date_hierarchy = 'timestamp'
    list_display = ('action', 'subject', 'sender', 'recipient_list', 'timestamp')
    list_filter = [
          'action',
          'timestamp',
    ] + ([DataFilter] if getattr(settings, 'NOTIFIER_REFS_ENABLED', False) else [])

    search_fields = [
        'subject',
        'sender',
        'recipients',
        'message',
    ]
    
    def recipient_list(self, obj):
        return ', '.join(obj.recipients)

