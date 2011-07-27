# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CustomSearchGroup'
        db.create_table('customsearch_customsearchgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('customsearch', ['CustomSearchGroup'])

        # Adding model 'CustomSearchModel'
        db.create_table('customsearch_customsearchmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('customsearch', ['CustomSearchModel'])

        # Adding model 'CustomSearchField'
        db.create_table('customsearch_customsearchfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchModel'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('field_name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('selector', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
        ))
        db.send_create_signal('customsearch', ['CustomSearchField'])

        # Adding model 'CustomSearchLayout'
        db.create_table('customsearch_customsearchlayout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchModel'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('customsearch', ['CustomSearchLayout'])

        # Adding model 'CustomSearchLayoutField'
        db.create_table('customsearch_customsearchlayoutfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchLayout'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchField'])),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('customsearch', ['CustomSearchLayoutField'])

        # Adding model 'CustomSearch'
        db.create_table('customsearch_customsearch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchModel'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchGroup'], null=True, blank=True)),
            ('layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchLayout'])),
        ))
        db.send_create_signal('customsearch', ['CustomSearch'])

        # Adding model 'CustomSearchCondition'
        db.create_table('customsearch_customsearchcondition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('search', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearch'])),
            ('exclude', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customsearch.CustomSearchField'])),
            ('match', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('customsearch', ['CustomSearchCondition'])


    def backwards(self, orm):
        
        # Deleting model 'CustomSearchGroup'
        db.delete_table('customsearch_customsearchgroup')

        # Deleting model 'CustomSearchModel'
        db.delete_table('customsearch_customsearchmodel')

        # Deleting model 'CustomSearchField'
        db.delete_table('customsearch_customsearchfield')

        # Deleting model 'CustomSearchLayout'
        db.delete_table('customsearch_customsearchlayout')

        # Deleting model 'CustomSearchLayoutField'
        db.delete_table('customsearch_customsearchlayoutfield')

        # Deleting model 'CustomSearch'
        db.delete_table('customsearch_customsearch')

        # Deleting model 'CustomSearchCondition'
        db.delete_table('customsearch_customsearchcondition')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'customsearch.customsearch': {
            'Meta': {'object_name': 'CustomSearch'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchLayout']"}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'customsearch.customsearchcondition': {
            'Meta': {'object_name': 'CustomSearchCondition'},
            'exclude': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'search': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearch']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'customsearch.customsearchfield': {
            'Meta': {'object_name': 'CustomSearchField'},
            'field_name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'selector': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'customsearch.customsearchgroup': {
            'Meta': {'object_name': 'CustomSearchGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'customsearch.customsearchlayout': {
            'Meta': {'object_name': 'CustomSearchLayout'},
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['customsearch.CustomSearchField']", 'through': "orm['customsearch.CustomSearchLayoutField']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'customsearch.customsearchlayoutfield': {
            'Meta': {'object_name': 'CustomSearchLayoutField'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchLayout']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'customsearch.customsearchmodel': {
            'Meta': {'object_name': 'CustomSearchModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['customsearch']
