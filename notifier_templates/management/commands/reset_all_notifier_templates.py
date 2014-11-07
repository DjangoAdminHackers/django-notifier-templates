from django.core.management.base import BaseCommand
from notifier_templates.utils import reset_all_notifier_templates


class Command(BaseCommand):
    help = "Deletes and recreates all email templates "
    def handle(self, *args, **options):
        reset_all_notifier_templates()