# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notifier_templates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentnotification',
            name='data',
            field=django_pgjson.fields.JsonBField(default={}),
            preserve_default=False,
        ),
    ]
