from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext, Context

from notifier_templates.forms import EmailEditForm
from notifier_templates.models import EmailTemplate, options
from notifier_templates.utils import send_html_email, generate_email_html


@staff_member_required
def notify(request, app_label, model_name, pk, action):

    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    obj = content_type.model_class().objects.get(pk=pk)
    label = obj.get_notifier_actions()[action]
    referrer = request.META.get('HTTP_REFERER', reverse('admin:index'))

    if request.method == 'POST':

        form = EmailEditForm(request.POST)

        if form.is_valid():

            send_html_email(
                subject=form.cleaned_data['subject'],
                sender=form.cleaned_data['sender'],
                recipients=form.cleaned_data['recipients'],
                html=form.cleaned_data['message'],
            )

            messages.add_message(request, messages.INFO, 'Notification sent')
            referrer = form.cleaned_data['referrer']
            response = obj.on_notified_success(action, request, referrer)
            return response or HttpResponseRedirect(referrer)

    else:

        email_template = EmailTemplate.objects.get(name=obj.get_email_template(action))
        context = obj.get_notifier_context(action)

        try:
            validate_email(options.from_address)
            sender = options.from_address
        except ValidationError:
            sender = None

        # Try and lookup the 'email' property for each recipient
        # TODO this is a bit specific to the original usage.
        # It would be an improvement to pass in the emails themselves
        # or even better - a list of potential recipients with some indication of their role
        # and allow the user to choose
        recipients = [x for x in obj.get_notifier_recipients(action) if getattr(x, 'email', False)]
        
        initial = {
            'subject': email_template.subject,
            'sender': sender,
            'recipients': recipients,
            'message': email_template.render(Context(context)),
            'referrer': referrer,

        }
        
        if request.GET.get('preview', False):
            initial['html'] = initial['message']
            return HttpResponse(generate_email_html(recipients=[], **initial))
            
        form = EmailEditForm(initial=initial)
        title = label.title()

    return render_to_response(
        'notifier_templates/edit_email.html', {
            'obj': obj,
            'form': form,
            'title': title,
        }, RequestContext(request),
    )