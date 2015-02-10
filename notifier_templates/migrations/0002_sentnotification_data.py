# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
try:
    from django_pgjson.fields import JsonBField as OurJsonField
except ImportError:
    from django_pgjson.fields import JsonField as OurJsonField

class Migration(migrations.Migration):

    dependencies = [
        ('notifier_templates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentnotification',
            name='data',
            field=OurJsonField(default={}),
            preserve_default=False,
        ),
    ]
