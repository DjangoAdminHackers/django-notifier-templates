import logging

from django.apps import AppConfig
from django.db import DatabaseError
from django.db import ProgrammingError

from .utils import generate_all_notifier_templates


logger = logging.getLogger(__name__)


class NotifierTemplateAppConfig(AppConfig):

    name = 'notifier_templates'
    verbose_name = 'Notification Templates'

    def ready(self):
        try:
            generate_all_notifier_templates()
        except (DatabaseError, RuntimeError, ProgrammingError) as e:
            # During migrations we are called before the table has been created
            if ("Please make sure contenttypes is migrated" in str(e)
                    or 'notifier_templates_emailtemplate\' doesn\'t exist' in str(e)):
                logger.warn("Skipping generation of notifier templates as db tables don't yet exist")
            else:
                raise