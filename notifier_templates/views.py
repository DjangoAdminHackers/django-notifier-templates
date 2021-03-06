from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext, Context

from notifier_templates.forms import EmailEditForm, EmailWithAttachmentsEditForm
from notifier_templates.models import HasNotifiers, EmailTemplate
from notifier_templates.utils import generate_email_html


@staff_member_required
def admin_helper(request):
    sections = []
    for app in models.get_apps():
        model_list = models.get_models(app)
        for model in model_list:
            is_subclass = issubclass(model, HasNotifiers)
            has_actions = hasattr(model, 'get_notifier_actions')
            has_events = getattr(model, 'NOTIFIER_EVENTS', None)
            if is_subclass:
                section = {
                    'title': '%s.%s' % (model._meta.app_label, model._meta.model_name),
                    'app_label': model._meta.app_label,
                    'model_name': model._meta.model_name,
                    'errors': '',
                    'urls': [],
                    'has_actions': has_actions,
                    'has_events': has_events,
                }
                sections.append(section)
                if not (has_actions or has_events):
                    section['errors'] = 'Please define at least one of get_notifier_actions and NOTIFIER_EVENTS.'
                    continue
                for obj in model.objects.all()[:1]:
                    if has_actions:
                        actions = dict(obj.get_notifier_actions()).keys()
                    elif has_events:
                        actions = obj.NOTIFIER_EVENTS.keys()
                    for action in actions:
                        url = reverse('notify', args=(model._meta.app_label, model._meta.model_name, obj.id, action, ))
                        section['urls'].append(url)
                
    return render_to_response(
        'notifier_templates/admin_helper.html', {
            'sections': sections,
        }, RequestContext(request),
    )

@staff_member_required
def admin_preview_auto_emails(request, app_label, model_name):
    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    model = content_type.model_class()
    emails = []
    actions = model.NOTIFIER_EVENTS.keys()
    rules = model.NOTIFIER_EVENTS.__repr__()
    for action in actions:
        candidates = model.get_candidates(action)
        for obj in candidates[:3]:
            email = obj.get_auto_notifer_email(action)
            email['action'] = action
            email['obj'] = obj
            emails.append(email)

    return render_to_response(
        'notifier_templates/admin_preview_auto_emails.html', {
            'emails': emails,
            'rules': rules,
        }, RequestContext(request),
    )


@staff_member_required
def notify(request, app_label, model_name, pk, action):

    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    obj = content_type.model_class().objects.get(pk=pk)
    actions = obj.get_notifier_actions()
    # Find the label for the first matching action
    label = [x['label'] for x in actions if x['type'] == action][0]
    referrer = request.META.get('HTTP_REFERER', reverse('admin:index'))
    next_override = request.GET.get('next', None)
    if next_override:
        referrer = next_override

    if hasattr(obj, 'notification_has_attachments') and obj.notification_has_attachments(action):
        form_class = EmailWithAttachmentsEditForm

        pdf_preview_url = obj.get_notifier_attachments_preview_url()
        form_kwargs = {'pdf_preview_url': pdf_preview_url}
    else:
        form_class = EmailEditForm
        form_kwargs = {}

    if request.method == 'POST':

        form = form_class(request.POST, **form_kwargs)

        if form.is_valid():

            if form.cleaned_data.get('include_attachments', False):
                attachments = obj.get_notifier_attachments()
            else:
                attachments = None

            obj.send_notifier_email(
                subject=form.cleaned_data['subject'],
                sender=form.cleaned_data['sender'],
                recipients=form.cleaned_data['recipients'],
                html=form.cleaned_data['message'],
                attachments=attachments,
                plain=form.cleaned_data['plain'],
            )

            obj.store_sent_notification(
                action,
                subject=form.cleaned_data['subject'],
                sender=form.cleaned_data['sender'],
                recipients=','.join(form.cleaned_data['recipients']),
                message=form.cleaned_data['message'],
                plain = form.cleaned_data['plain'],
            )

            messages.add_message(request, messages.INFO, 'Notification sent')
            referrer = form.cleaned_data['referrer']
            response = obj.on_notified_success(action, request, referrer)
            return response or HttpResponseRedirect(referrer)

    else:

        email_template = EmailTemplate.objects.get(
            name=obj.get_email_template(action),
            content_type=content_type,
        )
        context = obj.get_notifier_context(action, request=request)

        try:
            validate_email(obj.get_notifier_sender(action, request=request))
            sender = obj.get_notifier_sender(action, request=request)
        except ValidationError:
            sender = None

        # Try and lookup the 'email' property for each recipient
        # otherwise assume it's a string of the email address
        # TODO this is a bit specific to the original usage.
        # It would be an improvement to pass in the emails themselves
        # or even better - a list of potential recipients with some indication of their role
        # and allow the user to choose
        recipients = []
        for recipient in obj.get_notifier_recipients(action, request=request):
            email = getattr(recipient, 'email', False)
            if not email and isinstance(recipient, basestring):
                email = recipient
            if email:
                recipients.append(email)

        initial = {
            'subject': email_template.subject,
            'sender': sender,
            'recipients': recipients or '',
            'message': email_template.render(
                context=Context(context),
                custom_body_callback=obj.notifier_custom_template_body,
            ),
            'plain': email_template.render_plain(
                context=Context(context),
            ),
            'referrer': referrer,
        }
        
        if request.GET.get('preview', False):
            initial['html'] = initial['message']
            return HttpResponse(generate_email_html(recipients=[], **initial))
            
        form = form_class(initial=initial, **form_kwargs)
    title = label.title()

    return render_to_response(
        'notifier_templates/edit_email.html', {
            'obj': obj,
            'form': form,
            'title': title,
        }, RequestContext(request),
    )
    
