from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
from django.template import loader, Context, Template

from mcefield.custom_fields import MCEField
from notifier_templates.admin_settings import EmailOptions


class EmailTemplateManager(models.Manager):

    def get(self, *args, **kwargs):
        try:
            return super(EmailTemplateManager, self).get(*args, **kwargs)
        except self.model.DoesNotExist:
            # We could add any global template defaults here
            # such as company name etc.
            default_context = Context({})
            template = loader.get_template('emails/template_{}.html'.format(slugify(unicode(kwargs['name']))))
            body = template.render(default_context)
            name = kwargs['name']
            content_type = kwargs['content_type']
            # See if the template has: {% with subject="Your subject" %}{% endwith %}
            # and use that as the subject if so
            try:
                subject = template.nodelist[0].extra_context['subject'].var
            except:
                subject = name.replace('_', ' ').title()
            return EmailTemplate.objects.create(
                name=name,
                subject=subject,
                body=body,
                content_type=content_type,
            )


class EmailTemplate(models.Model):

    name = models.CharField(max_length=256)
    subject = models.CharField(max_length=256)
    body = MCEField(js='mce_emails.js', null=True, blank=True)
    content_type = models.ForeignKey(ContentType)

    def render(self, context):
        return Template(self.body).render(context)

    objects = EmailTemplateManager()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)


class HasNotifiers():

    @classmethod
    def get_email_template(cls, action):
        content_type = ContentType.objects.get_for_model(cls)
        return EmailTemplate.objects.get(name=action, content_type=content_type)

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

    def get_notifier_context(self, action):
        """
        Simple default content that just includes:
        a) the notfier action
        b) the instance accessed via it's model name {{ foo }} for a Foo
        c) the output of vars(foo) - which should include most useful properties
        Override this if you need more control over the context.
        """

        context = {
            'action': action,
            type(self).__name__.lower(): self,
            'site': Site.objects.get_current(),
        }
        context.update(vars(self))
        print context
        return context

    def get_notifier_recipients(self, action):
        # Attempt a sensible guess
        try:
            return [self.account.default_contact]
        # If that fails raise an error
        except:
            raise NotImplementedError


class NotifierActions(object):

    def get_row_actions(self, obj):
        row_actions = super(NotifierActions, self).get_row_actions(obj)
        notifier_actions = obj._get_notifier_actions_list()
        if notifier_actions:
            notifier_actions[0]['divided'] = True
            row_actions += notifier_actions
        return row_actions


# dbsettings
options = EmailOptions()