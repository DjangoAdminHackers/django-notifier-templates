from django.contrib import admin
from django.conf import settings
from django.utils.safestring import mark_safe
from .models import EmailTemplate, SentNotification
from .utils import generate_all_notifier_templates


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

admin.site.register(EmailTemplate, EmailTemplateAdmin)


class DataFilter(admin.SimpleListFilter):
    title = 'data filter'
    parameter_name = 'related_objects'

    def lookups(self, request, model_admin):
        #This doesn't return all keys, it only return keys of the first SentNotification object. 
        #keys = SentNotification.objects.hkeys(attr='data')
        #choices = [(key, key) for key in keys]
        choices = [('', ''), ] # we need to return a list with choices or thie list filter will be ignored. 
        return choices

    def queryset(self, request, queryset):
        query_value = self.value()
        if query_value: 
            if ':' in query_value:
                key, val = query_value.split(':')
                query = {'data__at_%s' % key: val}
                return queryset.filter(**query)
            else:
                return queryset.filter(data__contains=query_value)


class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ('action', 'timestamp', 'subject')

    list_filter = ('action', )
    if getattr(settings, 'NOTIFIER_REFS_ENABLED', False):
        list_filter = ('action', DataFilter, )

admin.site.register(SentNotification, SentNotificationAdmin)
