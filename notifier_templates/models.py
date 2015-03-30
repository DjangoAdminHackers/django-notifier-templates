from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.template import Context, Template
from multi_email_field.fields import MultiEmailField

from mcefield.custom_fields import MCEField
from notifier_templates.admin_settings import notifier_dbsettings


try:
    import django_pgjson
    if getattr(settings, 'JSONB_DISABLED', False):
        from django_pgjson.fields import JsonField
    else:
        from django_pgjson.fields import JsonBField as JsonField
except ImportError:
    django_pgjson = None


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


def get_obj_ref_str(obj):
    return u'%s.%s:%s' % (obj._meta.app_label, obj._meta.model_name, obj.pk)


class NotifierRefMixin(object):
    def get_obj_ref_str(self):
        return get_obj_ref_str(self)


class HasNotifiers(NotifierRefMixin):

    @classmethod
    def get_email_template(cls, action):
        content_type = ContentType.objects.get_for_model(cls, for_concrete_model=False)
        return EmailTemplate.objects.get(name=action, content_type=content_type)

    @classmethod
    def get_sent_notifications(cls, action):
        content_type = ContentType.objects.get_for_model(cls)
        return SentNotification.objects.filter(content_type=content_type, action=action)

    def on_notified_success(self, action, request, referrer):
        try:
            on_success = getattr(self, 'on_notified_{}'.format(action))
            return on_success(action, request, referrer)
        except AttributeError:
            # No specific callback - default behaviour goes here
            pass

    def _get_notifier_actions_list(self):

        content_type = ContentType.objects.get_for_model(type(self), for_concrete_model=False)

        def convert_action(action):
            # Construct a url from a notification name
            # so we can pass this straight to row_actions
            type = action.pop('type')
            url = reverse('notify',kwargs={
                'pk': self.pk,
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'action': type,
            })
            action.update({
                'url': url,
            })
            return action

        return [convert_action(action) for action in self.get_notifier_actions()]

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

    def get_notifier_refs(self, action):
        return []

    def store_sent_notification(self, action, subject, sender, recipients, message):
        refs = self.get_notifier_refs(action)
        sent_notification = SentNotification(
            content_object=self, 
            action=action,
            subject=subject, 
            sender=sender, 
            recipients=recipients, 
            message=message,
        )
        if refs and getattr(settings, 'NOTIFIER_REFS_ENABLED', False):
            data = {}
            for k, ref in refs.items():
                key = u'%s.%s' % (ref._meta.app_label, ref._meta.model_name)
                value = ref.pk
                data[key] = value
            sent_notification.data = data
        sent_notification.save()

    def get_notifier_recipients(self, action):
        # TODO make this more general
        # Currently this expects a list of objects that each have property called 'email'
        raise NotImplementedError

    def get_notifier_sender(self, action):
        return notifier_dbsettings.from_address

    def get_auto_notifer_email(self, action):
        recipients = [getattr(x, 'email', None) or x for x in self.get_notifier_recipients(action)]
        email_template = self._meta.model.get_email_template(action)
        context = self.get_notifier_context(action)
        html=email_template.render(Context(context))
        return dict(
            subject=email_template.subject, 
            sender=self.get_notifier_sender(action),
            recipients=recipients,
            html=html,
        )


    def send_auto_notifer_email(self, action):
        from notifier_templates.utils import send_html_email
        kwargs = self.get_auto_notifer_email(action)
        send_html_email(**kwargs)
        #import pdb; pdb.set_trace()
        kwargs['recipients'] = ','.join(kwargs['recipients'])
        kwargs['message'] = kwargs['html']
        del kwargs['html'] 
        self.store_sent_notification(action, **kwargs)
        return True
    
    @classmethod
    def get_candidates(cls, action):
        rules = cls.NOTIFIER_EVENTS[action]

        # Rules can be a dict or list of dicts
        if isinstance(rules, dict):
            rules = [rules]
        all_candidates = []

        for rule in rules:
            filters = rule.get('filters', {})
            if isinstance(filters, dict):
                q = Q(**filters)
            elif callable(filters):
                q = filters()
            elif isinstance(filters, Q):
                q = filters
            else:
                raise TypeError

            candidates = cls.objects.filter(q)
            date_filters = {}
            days_before = rule.get('days_before', None)
            if days_before:
                date_filters[rule['date_field'] + '__gte'] = timezone.now() + timezone.timedelta(days_before - 1)
                date_filters[rule['date_field'] + '__lte'] = timezone.now() + timezone.timedelta(days_before)
            candidates = candidates.filter(**date_filters)

            # Make sure email had not been sent before
            sent_objects_ids = [values[0] for values in cls.get_sent_notifications(action).values_list('object_id')]
            all_candidates += candidates.exclude(id__in=sent_objects_ids)

        return all_candidates


class NotifierActions(object):

    def get_row_actions(self, obj):
        row_actions = super(NotifierActions, self).get_row_actions(obj)
        notifier_actions = obj._get_notifier_actions_list()
        if notifier_actions:
            notifier_actions[0]['divided'] = True
            row_actions += notifier_actions
        return row_actions


class SentNotification(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=128)

    subject = models.CharField(max_length=512)
    sender = models.EmailField()
    recipients = MultiEmailField(help_text="You can enter multiple email addresses, one per line.")
    message = MCEField()

    if django_pgjson and getattr(settings, 'NOTIFIER_REFS_ENABLED', False):
        data = JsonField()  # can pass attributes like null, blank, ecc.


