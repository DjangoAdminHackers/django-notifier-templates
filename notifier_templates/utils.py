from django.core.mail import EmailMultiAlternatives
from django.contrib.contenttypes.models import ContentType
from django.template import loader, Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
from notifier_templates.models import options, EmailTemplate


def generate_email_html(subject, from_email, recipients, html, plain=None, **kwargs):
    from django.conf import settings
    template = loader.get_template('notifier_templates/notification_email.html')
    
    if settings.MEDIA_URL.startswith('http://'):
        media_url = settings.MEDIA_URL 
    else:
        media_url = 'http://%s%s' % (options.site_url, settings.MEDIA_URL)
    
    html = template.render(Context({
        'title': subject,
        'text_color': '333333',
        'year': timezone.now().year,
        'background_color': 'EEEEEE',
        'page_color': 'FFFFFF',
        'link_color': 'A51777',
        'topbar_color': '522E40',
        'html': html,
        'company': options.company,
        'site_url': options.site_url,
        'footer': options.email_footer,
        'logo': options.logo,
        'media_url': media_url
    }))
    return html


def send_html_email(subject, from_email, recipients, html, plain=None):
    html = generate_email_html(subject, from_email, recipients, html, plain)

    if plain is None:
        plain = strip_tags(html)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain,
        from_email=from_email,
        to=recipients,
    )

    msg.attach_alternative(html, "text/html")
    msg.send()
    return msg


def do_notify(app_label, model_name, pk, action):
    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    obj = content_type.model_class().objects.get(pk=pk)
    label = obj.get_notifier_actions()[action]
    recipients = [getattr(x, 'email', None) or x for x in obj.get_notifier_recipients(action)]

    email_template = EmailTemplate.objects.get(name=obj.get_email_template(action))
    context = obj.get_notifier_context(action)
    html=email_template.render(Context(context))
    send_html_email(
        subject=email_template.subject, 
        from_email=options.from_address,
        recipients=recipients,
        html=html,
    )
    return html
