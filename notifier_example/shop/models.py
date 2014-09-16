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
        'invoice_to_client',
        'invoice_7_day_pre_due',
        'invoice_1_day_pre_due',
    )
    
    NOTIFIER_EVENTS = {
        NOTIFIER_TYPES.invoice_1_day_pre_due: {'date_field': 'due', 'min_timedelta': timedelta(days=0), 'max_timedelta': timedelta(days=1), 'filters': {'status': STATUS.sent}, },
        NOTIFIER_TYPES.invoice_7_day_pre_due: {'date_field': 'due', 'min_timedelta': timedelta(days=0), 'max_timedelta': timedelta(days=7), 'filters': {'status': STATUS.sent}, },
    }

    due = models.DateField(null=True, blank=True)
    status = StatusField(default=STATUS.draft)
    
    def get_notifier_actions(self):
        return Choices(
            (self.NOTIFIER_TYPES.invoice_to_client, 'Send invoice'),
            (self.NOTIFIER_TYPES.invoice_7_day_pre_due, 'Send invoice 7 days due'),
            (self.NOTIFIER_TYPES.invoice_1_day_pre_due, 'Send invoice 1 day due'),
        )

    def get_notifier_recipients(self, action):
        return ['example@example.com']
        