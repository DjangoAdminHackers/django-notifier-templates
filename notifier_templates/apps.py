import logging

from django.apps import AppConfig
from django.db import DatabaseError

from .utils import generate_all_notifier_templates


logger = logging.getLogger(__name__)


class NotifierTemplateAppConfig(AppConfig):

    name = 'notifier_templates'
    verbose_name = 'Notification Templates'

    def ready(self):
        try:
            generate_all_notifier_templates()
        except DatabaseError:
            # During migrations we are called before the table has been created
            logger.warn("Skipping generate_all_notifier_templates as db table doesn't exist")