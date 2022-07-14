# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mcefield.custom_fields
import django.utils.timezone
import multi_email_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'Email type')),
                ('subject', models.CharField(max_length=256, verbose_name=b'Default email subject')),
                ('body', mcefield.custom_fields.MCEField(max_length=4000, null=True, blank=True)),
                ('content_type', models.ForeignKey(on_delete=models.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SentNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('object_id', models.PositiveIntegerField()),
                ('action', models.CharField(max_length=128)),
                ('subject', models.CharField(max_length=512)),
                ('sender', models.EmailField(max_length=75)),
                ('recipients', multi_email_field.fields.MultiEmailField(help_text=b'You can enter multiple email addresses, one per line.')),
                ('message', mcefield.custom_fields.MCEField(max_length=4000)),
                ('content_type', models.ForeignKey(on_delete=models.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
