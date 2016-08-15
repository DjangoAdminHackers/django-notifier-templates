from django.apps import AppConfig
from notifier_templates.utils import generate_all_notifier_templates


class ShopAppConfig(AppConfig):

    name = 'shop'

    def ready(self):
        generate_all_notifier_templates()