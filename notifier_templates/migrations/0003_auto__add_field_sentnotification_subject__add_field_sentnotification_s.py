# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SentNotification.subject'
        db.add_column(u'notifier_templates_sentnotification', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=512),
                      keep_default=False)

        # Adding field 'SentNotification.sender'
        db.add_column(u'notifier_templates_sentnotification', 'sender',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=75),
                      keep_default=False)

        # Adding field 'SentNotification.recipients'
        db.add_column(u'notifier_templates_sentnotification', 'recipients',
                      self.gf('multi_email_field.fields.MultiEmailField')(default=''),
                      keep_default=False)

        # Adding field 'SentNotification.message'
        db.add_column(u'notifier_templates_sentnotification', 'message',
                      self.gf('mcefield.custom_fields.MCEField')(default='', max_length=4000),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SentNotification.subject'
        db.delete_column(u'notifier_templates_sentnotification', 'subject')

        # Deleting field 'SentNotification.sender'
        db.delete_column(u'notifier_templates_sentnotification', 'sender')

        # Deleting field 'SentNotification.recipients'
        db.delete_column(u'notifier_templates_sentnotification', 'recipients')

        # Deleting field 'SentNotification.message'
        db.delete_column(u'notifier_templates_sentnotification', 'message')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'notifier_templates.emailtemplate': {
            'Meta': {'ordering': "['name']", 'object_name': 'EmailTemplate'},
            'body': ('mcefield.custom_fields.MCEField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'notifier_templates.sentnotification': {
            'Meta': {'object_name': 'SentNotification'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('mcefield.custom_fields.MCEField', [], {'max_length': '4000'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'recipients': ('multi_email_field.fields.MultiEmailField', [], {}),
            'sender': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['notifier_templates']