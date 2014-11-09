from django import forms
from django.contrib import admin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from notifier_templates.models import EmailTemplate, SentNotification


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

admin.site.register(EmailTemplate, EmailTemplateAdmin)


class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ('action', 'timestamp', 'subject')
    list_filter = ('action', )

admin.site.register(SentNotification, SentNotificationAdmin)
