# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mcefield.custom_fields


class Migration(migrations.Migration):

    dependencies = [
        ('notifier_templates', '0003_auto_20150401_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='body',
            field=mcefield.custom_fields.MCEField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sentnotification',
            name='message',
            field=mcefield.custom_fields.MCEField(),
        ),
        migrations.AlterField(
            model_name='sentnotification',
            name='sender',
            field=models.EmailField(max_length=254),
        ),
    ]
