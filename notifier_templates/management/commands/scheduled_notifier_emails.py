from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from django.utils import timezone

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
                        all_candidates = model.get_candidates(action)
                        
                        for obj in all_candidates:
                            print obj.send_auto_notifer_email(action)
                        
                        
                        