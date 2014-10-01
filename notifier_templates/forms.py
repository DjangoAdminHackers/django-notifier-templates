from django import forms
from multi_email_field.forms import MultiEmailField
from multi_email_field.widgets import MultiEmailWidget
from mcefield.custom_fields import MCEFormField


class EmailEditForm(forms.Form):

    subject = forms.CharField()
    sender = forms.EmailField()
    recipients = MultiEmailField(help_text="You can enter multiple email addresses, one per line.", widget=MultiEmailWidget(attrs={'rows': '3'}))
    referrer = forms.CharField(widget=forms.HiddenInput())
    message = MCEFormField(config_js_file='mce_emails.js')