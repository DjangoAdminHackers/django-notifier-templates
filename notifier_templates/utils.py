import os
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.template import loader, Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
import pynliner
from notifier_templates import notifier_settings
from notifier_templates.admin_settings import notifier_dbsettings
from notifier_templates.models import EmailTemplate, HasNotifiers
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


def generate_email_html(subject, sender, recipients, html, plain=None, **kwargs):

    template = loader.get_template('notifier_templates/notification_email.html')

    if settings.MEDIA_URL.startswith('http://'):
        media_url = settings.MEDIA_URL
    else:
        media_url = 'http://%s%s' % (Site.objects.get_current().domain, settings.MEDIA_URL)

    if notifier_dbsettings.logo and os.path.exists(os.path.join(settings.MEDIA_ROOT, notifier_dbsettings.logo)):
        logo_url = media_url + notifier_dbsettings.logo
    else:
        logo_url = None

    html = template.render(Context({
        'title': subject,
        'text_color': '333333',
        'year': timezone.now().year,
        'background_color': 'EEEEEE',
        'page_color': 'FFFFFF',
        'link_color': 'A51777',
        'topbar_color': '522E40',
        'html': html,
        'company': notifier_dbsettings.company,
        'site_url': notifier_dbsettings.site_url,
        'footer': notifier_dbsettings.email_footer,
        'logo_url': logo_url,
    }))
    if notifier_settings.USE_PYNLINER:
        return pynliner.fromString(html)
    else:
        return html


def send_html_email(subject, sender, recipients, html, attachments=None, plain=None, cc=None, bcc=None):

    html = generate_email_html(subject, sender, recipients, html, plain)

    if plain is None:
        if BeautifulSoup:
            # https://stackoverflow.com/questions/30565404/remove-all-style-scripts-and-html-tags-from-an-html-page/30565420
            soup = BeautifulSoup(html)
            for to_remove in soup(["script", "style"]): # remove all javascript and stylesheet code
                to_remove.extract()
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            plain = '\n'.join(chunk for chunk in chunks if chunk)
        else:
            plain = strip_tags(html)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain,
        from_email=sender,
        to=recipients,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
    )

    msg.attach_alternative(html, "text/html")
    msg.send()
    return msg


def send_plain_email(subject, sender, recipients, html, attachments=None, plain=None, cc=None, bcc=None):
    msg = EmailMessage(
        subject=subject,
        body=plain,
        from_email=sender,
        to=recipients,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
    )
    msg.send()
    return msg


def do_notify(app_label, model_name, pk, action):
    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    obj = content_type.model_class().objects.get(pk=pk)
    actions = obj.get_notifier_actions()
    # Find the label for the first matching action
    label = [x['label'] for x in actions if x['type']==action][0]
    recipients = [getattr(x, 'email', None) or x for x in obj.get_notifier_recipients(action)]

    email_template = EmailTemplate.objects.get(
        name=obj.get_email_template(action),
        content_type=content_type
    )
    context = obj.get_notifier_context(action)
    html=email_template.render(Context(context))
    obj.send_notifier_email(
        subject=email_template.subject,
        sender=obj.get_notifier_sender(action),
        recipients=recipients,
        html=html,
    )
    return html


def generate_notifier_template(cls, name, content_type=None):
    # We could add any global template defaults here
    # such as company name etc.
    default_context = Context({})
    template = loader.get_template('emails/{}.html'.format(name)).template
    body = template.render(default_context)
    content_type = content_type or ContentType.objects.get_for_model(cls, for_concrete_model=False)
    # See if the template has: {% with subject="Your subject" %}{% endwith %}
    # and use that as the subject if so
    try:
        subject = template.nodelist[0].extra_context['subject'].var
    except:
        subject = name.replace('_', ' ').title()
    return EmailTemplate.objects.get_or_create(
        name=name,
        content_type=content_type,
        defaults={
            'subject': subject,
            'body': body,
            },
        )


def generate_all_notifier_templates():
    """
    Recurses through all classes that use the mixin
    and makes sure we've generated the database entry for their template.
    Only need to call this if new notifiers are added so you can just
    call it in urls.py or use Django 1.7 startup hooks
    """
    def recurse_subclasses(cls_list):
        for subcls in cls_list:
            subcls_list = subcls.__subclasses__()
            if subcls_list:
                recurse_subclasses(subcls_list)
            for action in getattr(subcls, 'NOTIFIER_TYPES', []):
                if not isinstance(action, basestring):
                    # must be a CHOICES tuple
                    name = action[0]
                generate_notifier_template(subcls, name)

    recurse_subclasses([HasNotifiers])


def reset_all_notifier_templates():
    # Don't use bulk deletes unless there's a real performance need
    # as it stops you putting any business logic in delete()
    for template in EmailTemplate.objects.all():
        template.delete()
    generate_all_notifier_templates()
