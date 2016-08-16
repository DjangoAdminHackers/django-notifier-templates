from django.apps import AppConfig
from .utils import generate_all_notifier_templates


class NotifierTemplateAppConfig(AppConfig):

    name = 'notifier_templates'
    verbose_name = 'Notification Templates'

    def ready(self):
        generate_all_notifier_templates()