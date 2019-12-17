# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifier_templates', '0004_auto_20160815_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='is_plain_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='plain_body',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AddField(
            model_name='sentnotification',
            name='plain',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
