from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
from django.template import loader, Context, Template

from mcefield.custom_fields import MCEField
from notifier_templates.admin_settings import EmailOptions


class EmailTemplate(models.Model):

    name = models.CharField("Email type", max_length=256)
    subject = models.CharField("Default email subject", max_length=256)
    body = MCEField(js='mce_emails.js', null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    content_type.verbose_name = 'For'

    def render(self, context):
        return Template(self.body).render(context)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)


class HasNotifiers(object):

    @classmethod
    def get_email_template(cls, action):
        content_type = ContentType.objects.get_for_model(cls)
        return EmailTemplate.objects.get(name=action, content_type=content_type)

    @classmethod
    def get_sent_notifications(cls, action):
        content_type = ContentType.objects.get_for_model(cls)
        return SentNotification.objects.filter(content_type=content_type, action=action)

    def on_notified_success(self, action, request, referrer):
        try:
            on_success = getattr(self, 'on_notified_{}'.format(action))
            return on_success(self, action, request, referrer)
        except AttributeError:
            # No specific callback - default behaviour goes here
            pass

    def _get_notifier_actions_list(self):

        actions = self.get_notifier_actions()
        content_type = ContentType.objects.get_for_model(type(self))

        return [{
            'url': reverse('notify', kwargs={
                'pk': self.pk,
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'action': action,
            }),
            'label': '{}'.format(label.replace('_', ' ')),
        } for action, label in actions]

    @classmethod
    def get_available_fields(cls, action):
        """
        Return all the fields. Assumes get_notifier_context
        can handle being passed a blank instance.
        Override this if you want to handle this yourself.
        """
        return cls().get_notifier_context(action).keys()

    def get_notifier_context(self, action):
        """
        Simple default context that just includes:
        a) the notifier action
        b) the self instance - accessed via it's model name i.e. {{ foo }} for a Foo
        c) the output of vars(self) - which should include most useful properties
        Override this if you need more control over the context.
        """

        context = {
            'action': action,
            type(self).__name__.lower(): self,
            'site': Site.objects.get_current(),
        }
        context.update(vars(self))
        return context

    def get_notifier_recipients(self, action):
        # Attempt a sensible guess
        try:
            recipient = self.account.default_contact
        # If that fails raise an error
        except:
            raise NotImplementedError

        if recipient:
            return [recipient]
        else:
            return None

    def send_auto_notifer_email(self, action):
        from notifier_templates.utils import send_html_email
        recipients = [getattr(x, 'email', None) or x for x in self.get_notifier_recipients(action)]
        email_template = self._meta.model.get_email_template(action)
        context = self.get_notifier_context(action)
        html=email_template.render(Context(context))
        send_html_email(
            subject=email_template.subject, 
            from_email=options.from_address,
            recipients=recipients,
            html=html,
        )
        SentNotification(content_object=self, action=action).save()
        return True


class NotifierActions(object):

    def get_row_actions(self, obj):
        row_actions = super(NotifierActions, self).get_row_actions(obj)
        notifier_actions = obj._get_notifier_actions_list()
        if notifier_actions:
            notifier_actions[0]['divided'] = True
            row_actions += notifier_actions
        return row_actions


class SentNotification(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=128)

# dbsettings

options = EmailOptions()