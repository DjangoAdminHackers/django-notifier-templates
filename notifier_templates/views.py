from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context

from notifier_templates.forms import EmailEditForm
from notifier_templates.models import EmailTemplate, options
from notifier_templates.utils import send_html_email, generate_email_html


def notify(request, app_label, model_name, pk, action):

    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    obj = content_type.model_class().objects.get(pk=pk)
    label = obj.get_notifier_actions()[action]
    recipients = [getattr(x, 'email', None) or x for x in obj.get_notifier_recipients(action)]

    referrer = request.META.get('HTTP_REFERER', reverse('admin:index'))


    try:
        validate_email(options.from_address)
        from_email = options.from_address
    except ValidationError:
        from_email = None

    if from_email and request.method == 'POST':

        form = EmailEditForm(request.POST)

        if form.is_valid():

            send_html_email(
                subject=form.cleaned_data['subject'],
                from_email=options.from_address,
                recipients=recipients,
                html=form.cleaned_data['message'],
            )

            messages.add_message(request, messages.INFO, 'Notification sent')
            referrer = form.cleaned_data['referrer']
            response = obj.on_notified_success(action, request, referrer)
            return response or HttpResponseRedirect(referrer)

    elif from_email is None:

        form = None
        title = "Please go to settings and fill in a default sender address"

    else:

        email_template = EmailTemplate.objects.get(name=obj.get_email_template(action))
        context = obj.get_notifier_context(action)
        
        initial = {
            'subject': email_template.subject,
            'message': email_template.render(Context(context)),
            'referrer': referrer,
        }
        
        if request.GET.get('preview', False):
            initial['html'] = initial['message']
            initial['from_email'] = ''
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