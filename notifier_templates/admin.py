from django import forms
from django.contrib import admin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from notifier_templates.models import EmailTemplate


class EmailTemplateAdmin(admin.ModelAdmin):

    list_display = ('name', 'subject')

    fields = ('name', 'subject', 'body', 'available_fields')
    readonly_fields = ('name', 'available_fields',)

    def available_fields(self, obj):
        fields = obj.content_type.model_class().get_available_fields(obj.name)
        fields_html = u', '.join([field for field in fields])
        return mark_safe("<div class='help-text'>{}</div>".format(fields_html))

admin.site.register(EmailTemplate, EmailTemplateAdmin)

