# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EmailTemplate'
        db.create_table(u'notifier_templates_emailtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('body', self.gf('mcefield.custom_fields.MCEField')(max_length=4000, null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal(u'notifier_templates', ['EmailTemplate'])


    def backwards(self, orm):
        
        # Deleting model 'EmailTemplate'
        db.delete_table(u'notifier_templates_emailtemplate')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'notifier_templates.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body': ('mcefield.custom_fields.MCEField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['notifier_templates']
