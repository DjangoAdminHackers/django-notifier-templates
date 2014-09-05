from django import forms
from mcefield.custom_fields import MCEFormField


class EmailEditForm(forms.Form):

    subject = forms.CharField()
    referrer = forms.CharField(widget=forms.HiddenInput())
    message = MCEFormField(config_js_file='mce_emails.js')