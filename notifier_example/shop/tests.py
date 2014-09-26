from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase
from django.db import models
from django.core.management import call_command

from shop.models import Invoice
from django.utils import timezone
from notifier_templates.models import options, SentNotification


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        Site.objects.create(name='example.com', domain='example.com')
        options.from_address = 'example@example.com'
        options.company = 'Example Inc.'
        options.site_url = 'www.example.com'

        now = timezone.now()
        self.now = now
        self.invoice = Invoice.objects.create(due=now + timedelta(days=7))        
    
    def clear_sent_notifications(self):
        SentNotification.objects.all().delete()
    
    def test_draft_invoice(self):
        #testing the filters are working. 
        self.invoice.status = 'draft'
        self.invoice.save()
        call_command('scheduled_notifier_emails')
        #no email should be sent as it's still draft
        self.assertEqual(SentNotification.objects.all().count(), 0)

    def test_far_away_invoice(self):
        #testing the min_timedelta and max_timedelta are working. 
        self.invoice.status = 'sent'
        self.invoice.due = self.now + timedelta(days=8)
        self.invoice.save()
        call_command('scheduled_notifier_emails')
        #no email should be sent as it's not in 7 days yet. 
        self.assertEqual(SentNotification.objects.all().count(), 0)
        
    def test_7_day_invoice(self):
        #testing the min_timedelta and max_timedelta are working. 
        self.invoice.status = 'sent'
        self.invoice.due = self.now + timedelta(days=7)
        self.invoice.save()
        call_command('scheduled_notifier_emails')
        #7 days email should be sent. 
        self.assertEqual(SentNotification.objects.all().count(), 1)
        self.assertEqual(SentNotification.objects.all()[0].action, 'invoice_7_day_pre_due')
        self.clear_sent_notifications()
        
    def test_1_day_invoice(self):
        self.invoice.status = 'sent'
        self.invoice.due = self.now + timedelta(days=1)
        self.invoice.save()
        call_command('scheduled_notifier_emails')
        #both one day and 7 days email should be sent. 
        self.assertEqual(SentNotification.objects.all().count(), 2)
        self.assertEqual(SentNotification.objects.all().filter(action='invoice_7_day_pre_due').count(), 1)
        self.assertEqual(SentNotification.objects.all().filter(action='invoice_1_day_pre_due').count(), 1)
        self.clear_sent_notifications()
        
    def test_paid_invoice(self):
        self.invoice.status = 'paid'
        self.invoice.due = self.now + timedelta(days=1)
        self.invoice.save()
        call_command('scheduled_notifier_emails')
        #no email should be sent as it's already paid.
        self.assertEqual(SentNotification.objects.all().count(), 0)
        self.clear_sent_notifications()
        
    def test_sent_notification(self):
        '''No email should be sent twice. '''
        self.invoice.status = 'sent'
        self.invoice.due = self.now + timedelta(days=1)
        self.invoice.save()
        call_command('scheduled_notifier_emails')
        #both one day and 7 days email should be sent. 
        self.assertEqual(SentNotification.objects.all().count(), 2)
        #call the command again, nothing is sent
        call_command('scheduled_notifier_emails')
        self.assertEqual(SentNotification.objects.all().count(), 2)
        self.clear_sent_notifications()
        
    def test_unconditional_notifier(self):
        original_setting = Invoice.NOTIFIER_EVENTS
        Invoice.NOTIFIER_EVENTS['invoice_to_client'] = {'date_field': 'due', 'filters': {}, }
        self.invoice.status = 'draft'
        self.invoice.save()
        #this will send no matter what as there are neither date filters or conditional filters. 
        call_command('scheduled_notifier_emails')
        self.assertEqual(SentNotification.objects.all().count(), 1)
        Invoice.NOTIFIER_EVENTS = original_setting
        #but still we only sent it once
        call_command('scheduled_notifier_emails')
        self.assertEqual(SentNotification.objects.all().count(), 1)        
