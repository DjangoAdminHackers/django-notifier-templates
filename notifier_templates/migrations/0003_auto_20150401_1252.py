# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifier_templates', '0002_sentnotification_data'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='emailtemplate',
            unique_together=set([('name', 'content_type')]),
        ),
    ]
