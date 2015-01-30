import dbsettings
from mcefield.custom_fields import MCEWidget


class HTMLValue(dbsettings.TextValue):
    def __init__(self, *args, **kwargs):
        super(HTMLValue, self).__init__(*args, widget=MCEWidget(config_js_file='mce_emails.js'), **kwargs)


class EmailOptions(dbsettings.Group):

    test_mode = dbsettings.BooleanValue(
        default=False,
        help_text="All emails will be sent to test recipients instead of original recipients.",
    )
    from_address = dbsettings.StringValue(
        help_text='The address emails are sent from',
    )
    email_footer = HTMLValue(default="You can edit this text via settings")
    logo = dbsettings.ImageValue(upload_to='logos', required=False)
    company = dbsettings.StringValue(
        help_text='Company Name used in email',
    )
    site_url = dbsettings.StringValue(
        help_text='Website url used in email, e.g www.example.com',
    )


notifier_dbsettings = EmailOptions(app_label="Emails")