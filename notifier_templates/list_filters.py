from django.contrib import admin


class DataFilter(admin.SimpleListFilter):
    title = 'data filter'
    parameter_name = 'related_objects'

    def lookups(self, request, model_admin):
        # This doesn't return all keys, it only return keys of the first SentNotification object.
        # keys = SentNotification.objects.hkeys(attr='data')
        # choices = [(key, key) for key in keys]
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


