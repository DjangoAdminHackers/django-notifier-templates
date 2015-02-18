# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


# This is pretty bad (controlling migrations from the config), but we want to
# have a way of ensuring JSON fallback for Postgres < 9.4
if getattr(settings, 'USE_JSONB', False):
    from django_pgjson.fields import JsonBField as JsonField
else:
    from django_pgjson.fields import JsonField


class Migration(migrations.Migration):

    dependencies = [
        ('notifier_templates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentnotification',
            name='data',
            field=JsonField(default={}),
            preserve_default=False,
        ),
    ]
