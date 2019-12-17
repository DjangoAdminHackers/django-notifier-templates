from django import forms
from django.utils.safestring import mark_safe
from multi_email_field.forms import MultiEmailField
from multi_email_field.widgets import MultiEmailWidget
from mcefield.custom_fields import MCEFormField


class EmailEditForm(forms.Form):

    subject = forms.CharField()
    sender = forms.EmailField()
    recipients = MultiEmailField(help_text="You can enter multiple email addresses, one per line.", widget=MultiEmailWidget(attrs={'rows': '3'}))
    referrer = forms.CharField(widget=forms.HiddenInput())
    message = MCEFormField(required=False, config_js_file='mce_emails.js')
    plain = forms.CharField(required=False, widget=forms.Textarea)


class EmailWithAttachmentsEditForm(EmailEditForm):

    def __init__(self, *args, **kwargs):
        pdf_preview_url = kwargs.pop('pdf_preview_url', False)
        super(EmailWithAttachmentsEditForm, self).__init__(*args, **kwargs)
        if pdf_preview_url:
            self.fields['include_attachments'].help_text = mark_safe(
                '<a href="{}" target="_blank">&nbsp;preview attachment</a>'.format(pdf_preview_url)
            )

    include_attachments = forms.BooleanField(label="Include attachments?", initial=True)