import logging

from django.apps import AppConfig
from django.db import DatabaseError
from django.db import ProgrammingError
from django.db.models.signals import post_migrate


logger = logging.getLogger(__name__)


class NotifierTemplateAppConfig(AppConfig):

    name = 'notifier_templates'
    verbose_name = 'Notification Templates'

    def ready(self):
        super(NotifierTemplateAppConfig, self).ready()
        post_migrate.connect(do_generate_all_notifier_templates, sender=self)


def do_generate_all_notifier_templates(**kwargs):
    # Import locally otherwise models are imported before
    # apps are initialized
    from .utils import generate_all_notifier_templates
    generate_all_notifier_templates()
