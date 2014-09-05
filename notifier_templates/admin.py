from django import forms
from django.contrib import admin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from notifier_templates.models import EmailTemplate


class EmailTemplateAdmin(admin.ModelAdmin):

    list_display = ('name', 'subject')

    fields = ('name', 'subject', 'body', 'available_fields')
    readonly_fields = ('available_fields',)

    def available_fields(self, obj):
        model_class = obj.content_type.model_class()
        obj = model_class.objects.first()
        fields_html = u', '.join([field for field in obj.get_notifier_context().keys()])
        return mark_safe("<div class='help-text'>{}</div>".format(fields_html))

admin.site.register(EmailTemplate, EmailTemplateAdmin)

