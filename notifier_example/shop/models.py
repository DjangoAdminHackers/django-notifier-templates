from datetime import timedelta

from django.db import models

from model_utils import Choices
from model_utils.fields import StatusField

from notifier_templates.models import HasNotifiers

class Invoice(models.Model, HasNotifiers):

    STATUS = Choices(
        'draft',
        'sent',
        'paid',
    )

    NOTIFIER_TYPES = Choices(
        'invoice_to_customer',
        'invoice_7_days_before_due',
        'invoice_1_day_before_due',
    )
    
    NOTIFIER_EVENTS = {
        NOTIFIER_TYPES.invoice_7_days_before_due: {'date_field': 'due', 'min_timedelta': timedelta(days=0), 'max_timedelta': timedelta(days=1), 'filters': {'status': STATUS.sent}, },
        NOTIFIER_TYPES.invoice_1_day_before_due: {'date_field': 'due', 'min_timedelta': timedelta(days=0), 'max_timedelta': timedelta(days=7), 'filters': {'status': STATUS.sent}, },
    }

    due = models.DateField(null=True, blank=True)
    status = StatusField(default=STATUS.draft)
    
    def get_notifier_actions(self):
        return Choices(
            (self.NOTIFIER_TYPES.invoice_to_customer, 'Send invoice'),
        )

    def get_notifier_recipients(self, action):
        return ['example@example.com']
        