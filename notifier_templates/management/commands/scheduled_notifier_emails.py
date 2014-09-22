from time import timezone

from django.core.management.base import BaseCommand
from django.db import models

from notifier_templates.models import HasNotifiers


class Command(BaseCommand):
    help = "Send scheduled notifier emails. "
    def handle(self, *args, **options):
        print 'Send scheduled notifier emails. '
        for app in models.get_apps():
            model_list = models.get_models(app)
            for model in model_list:
                is_subclass = issubclass(model, HasNotifiers)
                has_events = hasattr(model, 'NOTIFIER_EVENTS')
                if is_subclass and has_events:
                    for action, rules in model.NOTIFIER_EVENTS.items():
                        candidates = model.objects.filter(**rules.get('filters', {}))
                        date_filters = {}
                        min_timedelta, max_timedelta = rules.get('min_timedelta', None), rules.get('max_timedelta', None) 
                        if min_timedelta:
                            date_filters[rules['date_field'] + '__gte'] = timezone.now() + min_timedelta
                        if max_timedelta:
                            date_filters[rules['date_field'] + '__lte'] = timezone.now() + max_timedelta
                        candidates = candidates.filter(**date_filters)
                        #make sure email had not been sent before. 
                        sent_objects_ids = [values[0] for values in model.get_sent_notifications(action).values_list('object_id')]
                        candidates = candidates.exclude(id__in=sent_objects_ids)
                        
                        for obj in candidates:
                            print obj.send_auto_notifer_email(action)
                        
                        
                        