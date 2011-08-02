# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CustomSearchField.enable_layout'
        db.add_column('customsearch_customsearchfield', 'enable_layout', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'CustomSearchField.enable_search'
        db.add_column('customsearch_customsearchfield', 'enable_search', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CustomSearchField.enable_layout'
        db.delete_column('customsearch_customsearchfield', 'enable_layout')

        # Deleting field 'CustomSearchField.enable_search'
        db.delete_column('customsearch_customsearchfield', 'enable_search')


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
            'enable_layout': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_search': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'expand_rel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        },
        'customsearch.customsearchordering': {
            'Meta': {'object_name': 'CustomSearchOrdering'},
            'descending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearchField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'search': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customsearch.CustomSearch']"})
        }
    }

    complete_apps = ['customsearch']
